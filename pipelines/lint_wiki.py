"""Lint the LLM-Wiki for factual errors against the cited dsRAG sources.

Strategy (per page):
  1. Extract atomic verifiable claims, each tagged with the doc_id(s)
     cited inline in parentheses.
  2. For each claim, retrieve top-3 segments from dsRAG scoped to the
     cited doc_id(s).
  3. Ask a judge LLM whether the claim is supported, contradicted, or
     unsupported by the evidence.
  4. Write a single markdown report flagging contradictions and
     unsupported claims (supported claims are summarized but not listed).

This pipeline reads the wiki only — it does NOT edit pages. The report
is meant for a human to review and decide which fixes to make.

Usage:
    # Lint the entire wiki
    python pipelines/lint_wiki.py

    # Lint a single page
    python pipelines/lint_wiki.py metrics/pmiers
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "pipelines"))

# Register Bedrock embedding before KB load (matches build_wiki.py)
import bedrock_embedding  # noqa: F401, E402

WIKI_ROOT = _REPO_ROOT / "data.mi" / "wiki"
REPORT_PATH = _REPO_ROOT / "data.mi" / "wiki_lint_report.md"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


class Claim(BaseModel):
    """An atomic factual claim extracted from a wiki page."""

    text: str = Field(
        description="The claim as a self-contained statement (resolve "
        "pronouns, include the subject and the specific value/condition)."
    )
    cited_doc_ids: list[str] = Field(
        description="The doc_id(s) cited inline in parens for this claim. "
        "Empty list if the claim has no inline citation."
    )
    page_quote: str = Field(
        description="The exact phrase from the page (≤200 chars) that "
        "this claim was extracted from. Used for line-locating in the "
        "report."
    )


class Claims(BaseModel):
    """Container for the structured-output call."""
    claims: list[Claim]


class Verdict(BaseModel):
    """Judge's verdict on a single claim."""

    status: str = Field(
        description="Exactly one of: supported, contradicted, unsupported, "
        "uncheckable. 'supported' = evidence directly confirms. "
        "'contradicted' = evidence directly disagrees. 'unsupported' = "
        "evidence neither confirms nor denies (silent on the topic). "
        "'uncheckable' = the claim is qualitative or cross-cutting and "
        "the cited segment can't reasonably confirm/deny it."
    )
    reason: str = Field(
        description="One sentence explaining the verdict. Cite specific "
        "evidence quote (≤120 chars) where applicable."
    )


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------


_extractor_client = None
_judge_client = None


def _configure_deepseek():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        sys.exit("ERROR: DEEPSEEK_API_KEY not set")
    os.environ.setdefault("OPENAI_API_KEY", api_key)
    os.environ.setdefault(
        "DSRAG_OPENAI_BASE_URL",
        os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    )


def _get_extractor():
    global _extractor_client
    if _extractor_client is not None:
        return _extractor_client
    import instructor
    from openai import OpenAI
    oa = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        timeout=120.0,
    )
    _extractor_client = instructor.from_openai(oa, mode=instructor.Mode.TOOLS)
    return _extractor_client


def _get_judge():
    global _judge_client
    if _judge_client is not None:
        return _judge_client
    import instructor
    from openai import OpenAI
    oa = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        timeout=60.0,
    )
    _judge_client = instructor.from_openai(oa, mode=instructor.Mode.TOOLS)
    return _judge_client


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


_EXTRACTOR_SYSTEM = """\
You extract atomic verifiable claims from a wiki page about US private
mortgage insurance. Each claim should be:
  - factual and specific (a number, a named entity, a regulatory rule,
    a definition, a date, a relationship)
  - self-contained (resolve pronouns; include subject and condition)
  - associated with the doc_id cited inline next to it, e.g. a sentence
    ending in "(MTG_10-K_2024-12-31)" → cited_doc_ids = ["MTG_10-K_2024-12-31"]

Skip the page's title, summary blockquote, and Sources/Related sections —
focus on the body where claims live. Do NOT extract:
  - generic explanatory prose ("analysts watch this metric")
  - the structural section headings themselves
  - claims about *what the page itself says* (meta-content)

If a claim packs multiple facts ("X is Y and Z"), split into separate
claims. Aim for high recall on quantitative claims (figures, percentages,
dates, thresholds) — those are the most-likely-to-be-wrong category.

For each claim, capture a short page_quote (≤200 chars, exact text from
the page) so a human can locate it.
"""


def extract_claims(page_text: str, page_slug: str) -> list[Claim]:
    client = _get_extractor()
    resp = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=4000,
        temperature=0.1,
        response_model=Claims,
        messages=[
            {"role": "system", "content": _EXTRACTOR_SYSTEM},
            {"role": "user", "content": f"Page slug: {page_slug}\n\nPage:\n{page_text}"},
        ],
    )
    return resp.claims


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


_JUDGE_SYSTEM = """\
You are a fact-checker. Given a CLAIM and EVIDENCE retrieved from the
cited source document, decide whether the claim is supported, contradicted,
unsupported, or uncheckable by the evidence.

Definitions:
  - supported: the evidence directly confirms the claim. The numeric
    value, name, or condition matches.
  - contradicted: the evidence directly disagrees with the claim
    (different value, different name, different condition).
  - unsupported: the evidence is silent on the claim — it neither
    confirms nor denies. Use this when the retrieval simply missed
    the relevant section, OR when the cited doc genuinely doesn't say
    what the claim asserts (which is itself a citation error).
  - uncheckable: the claim is qualitative, cross-document, or otherwise
    not amenable to single-segment verification (e.g. "X is the largest
    by market share" needs cross-MI synthesis).

Be strict on numbers: "approximately 25%" vs "25%" → supported; "25%"
vs "0.20%" → contradicted. Do NOT infer values; if the evidence doesn't
state the number, it's unsupported.

Be lenient on rephrasing: a claim is supported if its substance matches
even if the wording differs.
"""


def verify_claim(claim: Claim, kb) -> Verdict:
    """Retrieve evidence and ask the judge LLM.

    Recall trick: query both the synthesized claim text AND the original
    page quote, then dedup. The synthesized claim is canonical English;
    the page quote often contains the literal numbers/phrasing that BM25
    needs to land on a table row. Forcing a BM25-leaning alpha (0.7)
    helps with bare-number / table-row chunks where semantic similarity
    is weak.
    """
    if not claim.cited_doc_ids:
        # No citation → can't be checked against a specific source
        return Verdict(
            status="uncheckable",
            reason="No inline citation; can't verify against a specific source.",
        )

    queries = [claim.text]
    if claim.page_quote and claim.page_quote.strip() != claim.text.strip():
        queries.append(claim.page_quote)

    evidence_blocks: list[str] = []
    seen_keys: set[tuple[str, str]] = set()
    for d_id in claim.cited_doc_ids:
        metadata_filter = {"field": "doc_id", "operator": "equals", "value": d_id}
        try:
            kb._rrf_alpha = 0.7  # lexical-leaning: tables, exact figures
            results = kb.query(queries, metadata_filter=metadata_filter)
        except Exception as e:
            evidence_blocks.append(f"[doc_id: {d_id}] retrieval failed: {e}")
            continue
        finally:
            kb._rrf_alpha = 0.4

        top = results[:5]
        if not top:
            evidence_blocks.append(f"[doc_id: {d_id}] no segments retrieved")
            continue
        for r in top:
            # dsRAG segments can be 10k+ chars (multi-chunk RSE outputs).
            # Don't pre-truncate aggressively — the table or footnote that
            # supports the claim often sits in the back half of a long
            # segment. DeepSeek's 128k context easily handles 5×12k.
            content = (r.get("content") or r.get("text") or "")[:12000]
            key = (d_id, content[-200:])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            evidence_blocks.append(f"[doc_id: {d_id}]\n{content}")

    if not evidence_blocks:
        return Verdict(status="unsupported", reason="No evidence retrieved.")

    evidence_str = "\n\n---\n\n".join(evidence_blocks)

    client = _get_judge()
    user_msg = (
        f"CLAIM:\n{claim.text}\n\n"
        f"PAGE QUOTE: {claim.page_quote}\n\n"
        f"CITED DOC_IDS: {', '.join(claim.cited_doc_ids)}\n\n"
        f"EVIDENCE (top retrieved segments from the cited doc(s)):\n\n"
        f"{evidence_str}"
    )
    resp = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=400,
        temperature=0.0,
        response_model=Verdict,
        messages=[
            {"role": "system", "content": _JUDGE_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
    )
    return resp


# ---------------------------------------------------------------------------
# Page driver
# ---------------------------------------------------------------------------


@dataclass
class PageReport:
    slug: str
    n_claims: int
    findings: list[tuple[Claim, Verdict]]  # only contradicted + unsupported

    @property
    def n_contradicted(self) -> int:
        return sum(1 for _, v in self.findings if v.status == "contradicted")

    @property
    def n_unsupported(self) -> int:
        return sum(1 for _, v in self.findings if v.status == "unsupported")


def lint_page(page_path: Path, kb) -> PageReport:
    slug = page_path.relative_to(WIKI_ROOT).with_suffix("").as_posix()
    print(f"\n[{slug}]")
    text = page_path.read_text()

    try:
        claims = extract_claims(text, slug)
    except Exception as e:
        print(f"  extract failed: {e}")
        return PageReport(slug=slug, n_claims=0, findings=[])
    print(f"  extracted {len(claims)} claims")

    findings: list[tuple[Claim, Verdict]] = []
    for i, c in enumerate(claims, 1):
        try:
            v = verify_claim(c, kb)
        except Exception as e:
            print(f"    [{i}/{len(claims)}] verify failed: {e}")
            continue
        marker = {"supported": ".", "contradicted": "X", "unsupported": "?", "uncheckable": "~"}.get(v.status, "?")
        print(f"    [{i}/{len(claims)}] {marker} {v.status} — {c.text[:80]}")
        if v.status in ("contradicted", "unsupported"):
            findings.append((c, v))

    return PageReport(slug=slug, n_claims=len(claims), findings=findings)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def write_report(reports: list[PageReport]) -> None:
    total_claims = sum(r.n_claims for r in reports)
    total_contradicted = sum(r.n_contradicted for r in reports)
    total_unsupported = sum(r.n_unsupported for r in reports)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    lines = [
        f"# Wiki lint report",
        "",
        f"Generated: {ts}",
        "",
        f"Pages linted: **{len(reports)}**  •  ",
        f"Claims checked: **{total_claims}**  •  ",
        f"Contradicted: **{total_contradicted}**  •  ",
        f"Unsupported: **{total_unsupported}**",
        "",
        "Definitions: *contradicted* = evidence in the cited source",
        "directly disagrees. *unsupported* = the cited source is silent",
        "on the claim (often means the page cited the wrong source, or",
        "fabricated a number that isn't in any source).",
        "",
        "Supported and uncheckable claims are not listed here — they are",
        "the majority and uninteresting for review.",
        "",
        "## Per-page findings",
        "",
    ]

    # Sort: pages with most contradictions first, then most unsupported
    reports_sorted = sorted(
        reports,
        key=lambda r: (r.n_contradicted, r.n_unsupported, r.n_claims),
        reverse=True,
    )
    for r in reports_sorted:
        if not r.findings:
            lines.append(f"### `{r.slug}` — {r.n_claims} claims, **clean** ✓")
            lines.append("")
            continue

        lines.append(
            f"### `{r.slug}` — {r.n_claims} claims, "
            f"**{r.n_contradicted} contradicted**, **{r.n_unsupported} unsupported**"
        )
        lines.append("")

        # contradictions first
        for c, v in r.findings:
            if v.status != "contradicted":
                continue
            lines.append(f"- **CONTRADICTED**  ")
            lines.append(f"  *Claim:* {c.text}  ")
            lines.append(f"  *Page quote:* \"{c.page_quote.strip()}\"  ")
            lines.append(f"  *Cited:* `{', '.join(c.cited_doc_ids)}`  ")
            lines.append(f"  *Reason:* {v.reason}")
            lines.append("")
        for c, v in r.findings:
            if v.status != "unsupported":
                continue
            lines.append(f"- *unsupported*  ")
            lines.append(f"  *Claim:* {c.text}  ")
            lines.append(f"  *Page quote:* \"{c.page_quote.strip()}\"  ")
            lines.append(f"  *Cited:* `{', '.join(c.cited_doc_ids)}`  ")
            lines.append(f"  *Reason:* {v.reason}")
            lines.append("")

    REPORT_PATH.write_text("\n".join(lines))
    print(f"\nWrote report → {REPORT_PATH.relative_to(_REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    _configure_deepseek()
    selected_slugs = sys.argv[1:]

    # Skip the schema doc, the index, and the changelog — none have
    # verifiable per-claim factual content.
    skip_files = {"AGENTS.md", "index.md", "log.md"}

    page_paths: list[Path] = []
    if selected_slugs:
        for slug in selected_slugs:
            p = WIKI_ROOT / f"{slug}.md"
            if p.is_file():
                page_paths.append(p)
            else:
                print(f"WARN: skipping unknown slug {slug!r}")
    else:
        for p in sorted(WIKI_ROOT.rglob("*.md")):
            if p.name in skip_files:
                continue
            page_paths.append(p)

    if not page_paths:
        sys.exit("No pages to lint")

    from src.infrastructure.dsrag_kb import get_kb
    kb = get_kb()

    print(f"Linting {len(page_paths)} pages...")
    reports = [lint_page(p, kb) for p in page_paths]
    write_report(reports)


if __name__ == "__main__":
    main()
