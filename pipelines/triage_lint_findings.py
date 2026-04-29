"""Triage flagged claims from the wiki lint report by grepping the source.

Reads `data.mi/wiki_lint_report.md`, extracts the contradicted and
unsupported findings, and re-checks each one by grepping the parsed
markdown of the cited doc(s) for keyword phrases extracted from the
claim. This is a complementary verifier to the lint:

  - The lint uses dsRAG retrieval (top-k segment fetch). It can miss
    table chunks and densely-numeric sections — those become "false
    unsupported" verdicts.
  - The triage uses literal grep over the full parsed markdown. It
    can't be defeated by chunk boundaries, but it CAN be defeated by
    paraphrase: if the source uses different wording than the claim,
    grep misses it.

Together, a claim flagged by lint AND confirmed by triage is
high-confidence a real error and worth fixing in the wiki. A claim
flagged by lint but rescued by triage was almost certainly a lint
recall failure, not a wiki bug.

Usage:
    # Run after lint_wiki.py has produced its report
    python pipelines/triage_lint_findings.py
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

LINT_REPORT_PATH = _REPO_ROOT / "data.mi" / "wiki_lint_report.md"
TRIAGE_LOG_PATH = _REPO_ROOT / "data.mi" / "wiki_triage_log.md"
PARSED_ROOT = _REPO_ROOT / "data.mi" / "parsed"


# ---------------------------------------------------------------------------
# Lint-report parsing
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    page_slug: str
    status: str  # 'contradicted' | 'unsupported'
    claim_text: str
    page_quote: str
    cited_doc_ids: list[str]
    lint_reason: str


_PAGE_HEADER_RE = re.compile(
    r"^###\s+`(?P<slug>[^`]+)`",
    re.MULTILINE,
)


def parse_lint_report(report_path: Path) -> list[Finding]:
    """Pull contradicted + unsupported findings out of the markdown report."""
    if not report_path.exists():
        sys.exit(f"Lint report not found at {report_path}")

    text = report_path.read_text()

    # Split the report by page headers; each page chunk has 0+ findings.
    findings: list[Finding] = []
    page_chunks = _PAGE_HEADER_RE.split(text)
    # split returns: [preamble, slug1, body1, slug2, body2, ...]
    if len(page_chunks) < 3:
        return findings
    for i in range(1, len(page_chunks), 2):
        slug = page_chunks[i].strip()
        body = page_chunks[i + 1]
        findings.extend(_parse_page_body(slug, body))
    return findings


def _parse_page_body(slug: str, body: str) -> list[Finding]:
    """Pull each `- **CONTRADICTED**` / `- *unsupported*` bullet out of one page."""
    items: list[Finding] = []

    # Each bullet starts with one of these patterns. Capture everything until
    # the next bullet (or end of body).
    bullet_re = re.compile(
        r"^- (?:\*\*CONTRADICTED\*\*|\*unsupported\*)\s*$"
        r"(?P<body>(?:\n  .*?)+?)"
        r"(?=^- (?:\*\*CONTRADICTED\*\*|\*unsupported\*)|^### |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    field_re = re.compile(
        r"^\s+\*(?P<key>Claim|Page quote|Cited|Reason):\*\s*(?P<value>.*?)(?=\n\s+\*\w|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    for m in bullet_re.finditer(body):
        bullet_text = m.group(0)
        is_contradicted = "**CONTRADICTED**" in bullet_text
        bullet_body = m.group("body")
        fields: dict[str, str] = {}
        for fm in field_re.finditer(bullet_body):
            fields[fm.group("key").lower().replace(" ", "_")] = fm.group("value").strip()

        cited_raw = fields.get("cited", "").strip("`")
        cited_doc_ids = [c.strip() for c in cited_raw.split(",") if c.strip()]

        items.append(
            Finding(
                page_slug=slug,
                status="contradicted" if is_contradicted else "unsupported",
                claim_text=fields.get("claim", "").strip().strip('"'),
                page_quote=fields.get("page_quote", "").strip().strip('"'),
                cited_doc_ids=cited_doc_ids,
                lint_reason=fields.get("reason", "").strip(),
            )
        )
    return items


# ---------------------------------------------------------------------------
# Search-term extraction + grep
# ---------------------------------------------------------------------------


class SearchTerms(BaseModel):
    """Distinctive phrases that should appear in the source if the claim
    is supported. Pick numbers, exact regulatory terms, named entities —
    things that would NOT appear in unrelated paragraphs."""

    terms: list[str] = Field(
        description="2-4 distinctive search phrases. Prefer numeric "
        "values (e.g. '0.20%', '$5.8 billion'), exact regulatory or "
        "metric names ('PMIERs sufficiency ratio'), and named entities "
        "('Enact Re', 'EMICO'). Avoid generic words ('insurance', "
        "'company') that match too broadly."
    )


_extractor_client = None
_judge_client = None


def _configure_deepseek():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        sys.exit("ERROR: DEEPSEEK_API_KEY not set")
    os.environ.setdefault("OPENAI_API_KEY", api_key)


def _get_extractor():
    global _extractor_client
    if _extractor_client is not None:
        return _extractor_client
    import instructor
    from openai import OpenAI
    oa = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        timeout=60.0,
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


def extract_search_terms(claim: str) -> list[str]:
    client = _get_extractor()
    resp = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=300,
        temperature=0.0,
        max_retries=1,
        response_model=SearchTerms,
        messages=[
            {
                "role": "system",
                "content": "Extract 2-4 distinctive search terms that "
                "should appear in any source text supporting this claim.",
            },
            {"role": "user", "content": claim},
        ],
    )
    return [t.strip() for t in resp.terms if t and t.strip()]


def grep_source(doc_id: str, terms: list[str], window: int = 600) -> list[str]:
    """For each term, find all occurrences in parsed/<doc_id>.md and
    return ±window-char context windows. Dedup overlapping windows."""
    md_path = PARSED_ROOT / f"{doc_id}.md"
    if not md_path.is_file():
        return [f"[error] parsed source not found: {doc_id}.md"]
    text = md_path.read_text()
    text_lower = text.lower()

    # Collect all match-positions across all terms
    positions: list[int] = []
    matched_terms: dict[int, str] = {}
    for term in terms:
        if not term:
            continue
        needle = term.lower()
        start = 0
        while True:
            idx = text_lower.find(needle, start)
            if idx < 0:
                break
            positions.append(idx)
            matched_terms[idx] = term
            start = idx + max(1, len(needle))

    if not positions:
        return []

    # Build windows; merge overlapping
    positions.sort()
    windows: list[tuple[int, int, list[str]]] = []
    for p in positions:
        lo = max(0, p - window)
        hi = min(len(text), p + window)
        if windows and lo <= windows[-1][1]:
            # Overlap: extend the previous window
            prev_lo, prev_hi, prev_terms = windows[-1]
            windows[-1] = (
                prev_lo,
                max(prev_hi, hi),
                prev_terms + [matched_terms[p]],
            )
        else:
            windows.append((lo, hi, [matched_terms[p]]))

    # Render
    rendered: list[str] = []
    for lo, hi, hit_terms in windows:
        snippet = text[lo:hi]
        terms_str = ", ".join(sorted(set(hit_terms)))
        rendered.append(f"[match: {terms_str}]\n{snippet}")
    return rendered


# ---------------------------------------------------------------------------
# Triage judging
# ---------------------------------------------------------------------------


class TriageVerdict(BaseModel):
    status: str = Field(
        description="One of: real_error, likely_real, lint_noise, "
        "inconclusive. 'real_error' = grep found supporting context but "
        "the source contradicts the claim, OR grep found nothing and "
        "the claim names specific values that should appear if true. "
        "'lint_noise' = grep found context that supports the claim "
        "(lint missed it). 'likely_real' = grep found nothing OR found "
        "context that suggests the claim is wrong, but with some "
        "ambiguity. 'inconclusive' = can't tell."
    )
    reason: str = Field(
        description="One sentence explaining the verdict. Quote a short "
        "supporting/contradicting phrase from grep (≤120 chars)."
    )
    recommended_action: str = Field(
        description="One short phrase: 'fix - rewrite claim', 'fix - "
        "remove claim', 'fix - re-cite to correct doc_id', 'no action - "
        "lint noise', or 'manual review needed'."
    )


_TRIAGE_JUDGE_SYSTEM = """\
You triage a wiki claim that the lint flagged as contradicted or
unsupported. You see the original claim plus literal grep matches from
the parsed source document. Decide:

  - real_error: the grep evidence shows the source disagrees with the
    claim (e.g. claim says 25%, source says 50%); OR grep found nothing
    AND the claim makes specific numeric/named assertions that would
    have grep-matched if true.
  - likely_real: grep evidence is weak/ambiguous and leans against the
    claim, but you're not 100% certain.
  - lint_noise: grep evidence supports the claim. The lint missed the
    relevant chunk; the wiki is fine.
  - inconclusive: not enough evidence either way.

Be decisive. If grep matched the exact figure or name from the claim
and the surrounding context confirms it, that's lint_noise. If grep
matched a related figure that contradicts the claim, that's real_error.
If grep matched only generic terms with no specific support, lean
likely_real or inconclusive.
"""


def triage_finding(finding: Finding) -> tuple[list[str], list[str], TriageVerdict]:
    """Returns (search_terms, grep_windows, verdict)."""
    try:
        terms = extract_search_terms(finding.claim_text)
    except Exception as e:
        return (
            [],
            [],
            TriageVerdict(
                status="inconclusive",
                reason=f"Search-term extraction failed: {e}",
                recommended_action="manual review needed",
            ),
        )

    all_windows: list[str] = []
    for d_id in finding.cited_doc_ids:
        windows = grep_source(d_id, terms)
        if windows:
            all_windows.append(f"--- doc_id: {d_id} ---")
            all_windows.extend(windows)
        else:
            all_windows.append(f"--- doc_id: {d_id} --- (no matches for any term)")

    user_msg = (
        f"CLAIM (lint-flagged as {finding.status}):\n{finding.claim_text}\n\n"
        f"PAGE QUOTE: {finding.page_quote}\n\n"
        f"CITED DOC_IDS: {', '.join(finding.cited_doc_ids)}\n\n"
        f"LINT'S REASON: {finding.lint_reason}\n\n"
        f"GREP RESULTS (literal matches in cited source):\n\n"
        + "\n\n".join(all_windows)
    )

    client = _get_judge()
    try:
        verdict = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=500,
            temperature=0.0,
            max_retries=1,
            response_model=TriageVerdict,
            messages=[
                {"role": "system", "content": _TRIAGE_JUDGE_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
        )
    except Exception as e:
        verdict = TriageVerdict(
            status="inconclusive",
            reason=f"Judge call failed: {e}",
            recommended_action="manual review needed",
        )

    return terms, all_windows, verdict


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def write_triage_log(
    findings: list[Finding],
    triages: list[tuple[list[str], list[str], TriageVerdict]],
) -> None:
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    counts = {"real_error": 0, "likely_real": 0, "lint_noise": 0, "inconclusive": 0}
    for _, _, v in triages:
        counts[v.status] = counts.get(v.status, 0) + 1

    lines = [
        "# Wiki triage log",
        "",
        f"Generated: {ts}",
        f"Source lint report: `data.mi/wiki_lint_report.md`",
        "",
        f"Findings triaged: **{len(findings)}**",
        f"  - real_error:    **{counts['real_error']}**  (high-confidence wiki bugs)",
        f"  - likely_real:   **{counts['likely_real']}**  (probable bugs, manual review recommended)",
        f"  - lint_noise:    **{counts['lint_noise']}**  (grep found supporting evidence; wiki is fine)",
        f"  - inconclusive:  **{counts['inconclusive']}**",
        "",
        "Each entry below preserves the full chain (claim → search terms → grep matches → verdict)",
        "so you can re-derive any decision later without re-running the pipeline.",
        "",
        "## Recommended fixes",
        "",
    ]
    # Real errors first, grouped by page
    real_errors = [
        (f, t, w, v)
        for (f, (t, w, v)) in zip(findings, triages)
        if v.status == "real_error"
    ]
    if real_errors:
        # Group by page
        by_page: dict[str, list] = {}
        for f, t, w, v in real_errors:
            by_page.setdefault(f.page_slug, []).append((f, t, w, v))
        for slug in sorted(by_page):
            lines.append(f"### `{slug}`")
            lines.append("")
            for f, t, w, v in by_page[slug]:
                lines.append(f"- **{v.recommended_action}**: {f.claim_text}")
                lines.append(f"  ↳ {v.reason}")
            lines.append("")
    else:
        lines.append("(none)")
        lines.append("")

    lines += [
        "## Likely real errors (manual review)",
        "",
    ]
    likely = [
        (f, t, w, v)
        for (f, (t, w, v)) in zip(findings, triages)
        if v.status == "likely_real"
    ]
    if likely:
        for f, t, w, v in likely:
            lines.append(f"- `{f.page_slug}` — {f.claim_text}")
            lines.append(f"  ↳ {v.reason}")
        lines.append("")
    else:
        lines.append("(none)")
        lines.append("")

    lines += [
        "## Full triage log (every flagged claim, with evidence)",
        "",
        "Order: real_error → likely_real → inconclusive → lint_noise.",
        "",
    ]

    status_order = {"real_error": 0, "likely_real": 1, "inconclusive": 2, "lint_noise": 3}
    indexed = list(zip(findings, triages))
    indexed.sort(key=lambda x: (status_order.get(x[1][2].status, 9), x[0].page_slug))

    for finding, (terms, windows, verdict) in indexed:
        lines.append(f"### [{verdict.status.upper()}] `{finding.page_slug}`")
        lines.append("")
        lines.append(f"**Lint flag:** {finding.status}  ")
        lines.append(f"**Claim:** {finding.claim_text}  ")
        lines.append(f"**Page quote:** \"{finding.page_quote}\"  ")
        lines.append(f"**Cited:** `{', '.join(finding.cited_doc_ids)}`  ")
        lines.append(f"**Lint reason:** {finding.lint_reason}")
        lines.append("")
        lines.append(f"**Search terms:** {terms}")
        lines.append("")
        lines.append(f"**Triage verdict:** {verdict.status} — {verdict.reason}  ")
        lines.append(f"**Recommended action:** {verdict.recommended_action}")
        lines.append("")
        lines.append("<details><summary>Grep evidence</summary>")
        lines.append("")
        for w in windows[:6]:  # cap at 6 windows for readability
            lines.append("```")
            # Trim very-long windows for the log
            lines.append(w[:2000] + ("\n…" if len(w) > 2000 else ""))
            lines.append("```")
        if len(windows) > 6:
            lines.append(f"_({len(windows) - 6} additional windows omitted)_")
        lines.append("")
        lines.append("</details>")
        lines.append("")
        lines.append("---")
        lines.append("")

    TRIAGE_LOG_PATH.write_text("\n".join(lines))
    print(f"\nWrote triage log → {TRIAGE_LOG_PATH.relative_to(_REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    _configure_deepseek()
    findings = parse_lint_report(LINT_REPORT_PATH)
    if not findings:
        print("No flagged findings to triage.")
        return
    print(f"Triaging {len(findings)} flagged findings from lint report...")

    triages: list[tuple[list[str], list[str], TriageVerdict]] = []
    for i, f in enumerate(findings, 1):
        terms, windows, verdict = triage_finding(f)
        marker = {
            "real_error": "X",
            "likely_real": "!",
            "lint_noise": ".",
            "inconclusive": "?",
        }.get(verdict.status, "?")
        print(
            f"  [{i}/{len(findings)}] {marker} {verdict.status}  "
            f"`{f.page_slug}`  {f.claim_text[:60]}"
        )
        triages.append((terms, windows, verdict))

    write_triage_log(findings, triages)


if __name__ == "__main__":
    main()
