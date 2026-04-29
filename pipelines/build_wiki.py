"""Generate the LLM-Wiki pages from the dsRAG corpus.

Implementation of Karpathy's LLM-Wiki pattern (April 2026): pre-compile
synthesized knowledge into structured markdown pages, then expose those
pages to the agent as a navigable surface (via the `wiki_*` tools)
instead of relying on chunked retrieval for synthesis questions.

Per page, the pipeline:
  1. Issues a small set of dsRAG queries to gather raw context
  2. Aggregates the retrieved segments
  3. Asks DeepSeek to author a markdown page following the schema in
     `data.mi/wiki/AGENTS.md`
  4. Writes the page to `data.mi/wiki/<category>/<slug>.md`

Usage:
    # Generate everything
    python pipelines/build_wiki.py

    # Generate a single page (by slug)
    python pipelines/build_wiki.py metrics/pmiers
    python pipelines/build_wiki.py topics/pmiers_aug_2024_update

Re-runs overwrite existing pages so iterating on the authoring prompt
or page schema is cheap.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Project root on path so we can import src/* and dsrag_kb
_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "pipelines"))

# Need to register the BedrockTitanEmbedding subclass before KB load
import bedrock_embedding  # noqa: F401, E402

WIKI_ROOT = _REPO_ROOT / "data.mi" / "wiki"


@dataclass
class PageDef:
    """Definition of a single wiki page."""
    slug: str  # e.g. "metrics/pmiers"
    title: str
    purpose: str  # one-line: what an analyst would want from this page
    queries: list[str]  # dsRAG queries to gather context
    doc_id_hints: list[str] = field(default_factory=list)  # preferred doc_ids to scope queries to (cycled across queries)
    related: list[str] = field(default_factory=list)  # slugs of related pages for cross-refs


# ---------------------------------------------------------------------------
# Page slates
# ---------------------------------------------------------------------------

METRIC_PAGES: list[PageDef] = [
    PageDef(
        slug="metrics/pmiers",
        title="PMIERs (Private Mortgage Insurer Eligibility Requirements)",
        purpose="Explain what PMIERs is, the available-assets / required-assets framework, sufficiency ratio, and how the August 2024 update changes the calculation.",
        queries=[
            "What is PMIERs and what does it require for available assets?",
            "How is the PMIERs Sufficiency Ratio calculated?",
            "How did the August 2024 PMIERs update change the calculation of available assets?",
            "What are the recent PMIERs Sufficiency Ratios for the 6 US MI companies?",
        ],
        doc_id_hints=[
            "INDUSTRY_PMIERS_2.0_BASE",
            "INDUSTRY_PMIERS_OVERVIEW_FHFA",
            "INDUSTRY_PMIERS_GUIDANCE_2024-01",
        ],
        related=["topics/pmiers_aug_2024_update", "topics/gse_relationship"],
    ),
    PageDef(
        slug="metrics/niw",
        title="New Insurance Written (NIW)",
        purpose="Define NIW, explain its drivers (origination volume, market share, MI penetration), and summarize recent NIW levels across the 6 MIs.",
        queries=[
            "What is New Insurance Written (NIW) in mortgage insurance?",
            "What were the FY2024 New Insurance Written (NIW) figures for MGIC, Radian, Essent, NMI, Arch, and Enact?",
            "What drives changes in NIW for mortgage insurers?",
        ],
        doc_id_hints=[
            "INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09",
            "MTG_10-K_2024-12-31",
            "RDN_10-K_2024-12-31",
        ],
        related=["metrics/iif", "metrics/persistency", "topics/us_mortgage_market"],
    ),
    PageDef(
        slug="metrics/iif",
        title="Insurance in Force (IIF)",
        purpose="Define primary IIF, explain the roll-forward (NIW in, runoff out), and show recent IIF levels across the 6 MIs.",
        queries=[
            "What is primary insurance in force (IIF) for a mortgage insurer?",
            "How does IIF roll forward from quarter to quarter?",
            "What are recent primary IIF levels at MGIC, Radian, Essent, NMI, Arch, and Enact?",
        ],
        doc_id_hints=[
            "INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09",
            "MTG_10-K_2024-12-31",
            "RDN_10-K_2024-12-31",
            "ESNT_10-K_2024-12-31",
        ],
        related=["metrics/niw", "metrics/persistency"],
    ),
    PageDef(
        slug="metrics/persistency",
        title="Persistency",
        purpose="Define annual persistency, explain its sensitivity to refinance activity and interest rates, and summarize recent persistency rates across the 6 MIs.",
        queries=[
            "What is annual persistency for a mortgage insurer and how is it calculated?",
            "Why is persistency at historically high levels recently?",
            "What are recent persistency rates at MGIC, Radian, Essent, NMI, Arch, and Enact?",
        ],
        doc_id_hints=[
            "INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09",
            "MTG_10-K_2024-12-31",
            "NMIH_10-K_2024-12-31",
        ],
        related=["metrics/iif", "metrics/niw", "topics/us_mortgage_market"],
    ),
    PageDef(
        slug="metrics/loss_ratio",
        title="Loss Ratio (MI-specific)",
        purpose="Define loss ratio in mortgage insurance, explain how it differs from P&C, walk through favorable reserve development, and summarize recent loss ratios across the 6 MIs.",
        queries=[
            "How is the loss ratio calculated for a mortgage insurer and why is it often near zero or negative?",
            "What is favorable prior-year loss reserve development and why has it been a recurring positive for MI loss ratios?",
            "What are recent loss ratios at MGIC, Radian, Essent, and the other MIs?",
        ],
        doc_id_hints=[
            "INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09",
            "MTG_10-K_2024-12-31",
            "RDN_10-K_2024-12-31",
        ],
        related=["metrics/iif", "topics/catastrophe_impact_on_mi"],
    ),
    PageDef(
        slug="metrics/reinsurance_crt",
        title="Reinsurance and Credit Risk Transfer (CRT)",
        purpose="Explain the role of reinsurance (quota share + ILN) in MI capital management, why it matters for PMIERs sufficiency, and how the 6 MIs use it.",
        queries=[
            "How do mortgage insurers use reinsurance and credit risk transfer (CRT) to manage capital?",
            "What is the difference between quota share reinsurance and Insurance-Linked Note (ILN) transactions in MI?",
            "How do MGIC, Radian, Essent, and the other MIs use reinsurance to reduce PMIERs required assets?",
        ],
        doc_id_hints=[
            "INDUSTRY_USMI_RESILIENCY_2023-11",
            "MTG_10-K_2024-12-31",
            "RDN_10-K_2024-12-31",
            "ESNT_10-K_2024-12-31",
        ],
        related=["metrics/pmiers", "topics/mi_regulatory_landscape"],
    ),
]

COMPANY_PAGES: list[PageDef] = [
    PageDef(
        slug="companies/mtg_mgic",
        title="MGIC Investment Corporation (MTG)",
        purpose="Analyst-perspective overview of MGIC: business model, recent financial results, capital position, capital return strategy, and competitive position.",
        queries=[
            "What is MGIC Investment Corporation's business and how does it generate revenue?",
            "What were MGIC's FY2024 financial results — net income, ROE, NIW, IIF, persistency?",
            "What is MGIC's capital position and capital return strategy?",
            "How does MGIC's recent competitive position compare to the other US MIs?",
        ],
        doc_id_hints=[
            "MTG_10-K_2024-12-31",
            "MTG_10-K_2025-12-31",
            "MTG_TRANSCRIPT_2024-12-31",
        ],
        related=[
            "metrics/pmiers", "metrics/niw", "metrics/iif", "metrics/persistency",
        ],
    ),
    PageDef(
        slug="companies/rdn_radian",
        title="Radian Group Inc. (RDN)",
        purpose="Analyst-perspective overview of Radian: business model, recent financials, capital position, segment structure (mortgage + homegenius), and capital return.",
        queries=[
            "What is Radian Group's business including its mortgage and homegenius segments?",
            "What were Radian's FY2024 financial results — net income, ROE, NIW, IIF, persistency?",
            "What is Radian's capital position and capital return strategy?",
        ],
        doc_id_hints=[
            "RDN_10-K_2024-12-31",
            "RDN_10-K_2025-12-31",
            "RDN_TRANSCRIPT_2024-12-31",
        ],
        related=[
            "metrics/pmiers", "metrics/niw", "metrics/iif", "metrics/persistency",
        ],
    ),
    PageDef(
        slug="companies/esnt_essent",
        title="Essent Group Ltd. (ESNT)",
        purpose="Analyst-perspective overview of Essent: business model, recent financials, capital position, and conservative underwriting approach.",
        queries=[
            "What is Essent Group's business and how does it differ from peers?",
            "What were Essent's FY2024 financial results — net income, ROE, NIW, IIF, persistency?",
            "What is Essent's capital position and capital return strategy?",
        ],
        doc_id_hints=[
            "ESNT_10-K_2024-12-31",
            "ESNT_10-K_2025-12-31",
            "ESNT_TRANSCRIPT_2024-12-31",
        ],
        related=[
            "metrics/pmiers", "metrics/niw", "metrics/iif", "metrics/persistency",
        ],
    ),
    PageDef(
        slug="companies/nmih_nmi",
        title="NMI Holdings Inc. (NMIH / National MI)",
        purpose="Analyst-perspective overview of NMI Holdings: business model, recent financials, capital position, and growth profile as the youngest MI.",
        queries=[
            "What is NMI Holdings' business and competitive position as the newest US MI?",
            "What were NMI Holdings' FY2024 financial results — net income, ROE, NIW, IIF, persistency?",
            "What is NMI Holdings' capital position and capital return strategy?",
        ],
        doc_id_hints=[
            "NMIH_10-K_2024-12-31",
            "NMIH_10-K_2025-12-31",
            "NMIH_TRANSCRIPT_2024-12-31",
        ],
        related=[
            "metrics/pmiers", "metrics/niw", "metrics/iif", "metrics/persistency",
        ],
    ),
    PageDef(
        slug="companies/acgl_arch",
        title="Arch Capital Group Ltd. (ACGL)",
        purpose="Analyst-perspective overview of Arch Capital: focus on the mortgage segment within the broader insurance/reinsurance group, USMI vs international, recent financials.",
        queries=[
            "What is Arch Capital Group's mortgage segment (USMI) within its broader insurance/reinsurance business?",
            "What were Arch Capital's mortgage segment FY2024 results — underwriting income, NIW, IIF, PMIERs sufficiency?",
            "How does Arch's mortgage segment compare to its insurance and reinsurance segments?",
        ],
        doc_id_hints=[
            "ACGL_10-K_2024-12-31",
            "ACGL_10-K_2025-12-31",
            "ACGL_TRANSCRIPT_2024-12-31",
        ],
        related=[
            "metrics/pmiers", "metrics/niw", "metrics/reinsurance_crt",
        ],
    ),
    PageDef(
        slug="companies/act_enact",
        title="Enact Holdings Inc. (ACT)",
        purpose="Analyst-perspective overview of Enact: business model, Genworth ownership history, recent financials, capital return profile.",
        queries=[
            "What is Enact Holdings' business and its history with Genworth Financial?",
            "What were Enact Holdings' FY2024 financial results — net income, ROE, NIW, IIF, persistency?",
            "What is Enact's capital position and capital return strategy?",
        ],
        doc_id_hints=[
            "ACT_10-K_2024-12-31",
            "ACT_10-K_2025-12-31",
            "ACT_TRANSCRIPT_2024-12-31",
        ],
        related=[
            "metrics/pmiers", "metrics/niw", "metrics/iif", "metrics/persistency",
        ],
    ),
]

TOPIC_PAGES: list[PageDef] = [
    PageDef(
        slug="topics/pmiers_aug_2024_update",
        title="August 2024 PMIERs Update",
        purpose="Explain the August 2024 PMIERs update — investment-risk deductions to available assets, the phase-in schedule (March 2025 → September 2026), and the impact on each of the 6 MIs' available assets and Sufficiency Ratios.",
        queries=[
            "What changed in the August 2024 PMIERs update? Investment risk deductions, NAIC bond categories, phase-in schedule.",
            "What is the expected impact of the August 2024 PMIERs update on Arch Capital's mortgage subsidiaries' available assets and Sufficiency Ratio?",
            "What is the expected impact of the August 2024 PMIERs update on MGIC's available assets and Sufficiency Ratio?",
            "How are Radian, Essent, NMI, and Enact affected by the August 2024 PMIERs update?",
        ],
        doc_id_hints=[
            "INDUSTRY_PMIERS_GUIDANCE_2024-01",
            "INDUSTRY_PMIERS_GUIDANCE_2024-02",
            "ACGL_10-K_2024-12-31",
            "MTG_10-K_2024-12-31",
        ],
        related=["metrics/pmiers", "topics/gse_relationship"],
    ),
    PageDef(
        slug="topics/gse_relationship",
        title="The GSE Relationship (Fannie Mae, Freddie Mac, FHFA)",
        purpose="Explain the structural role of Fannie Mae, Freddie Mac, and FHFA as the counterparties / regulators that determine MI eligibility, business volume, and capital requirements.",
        queries=[
            "How do mortgage insurers operate in relation to Fannie Mae and Freddie Mac as counterparties?",
            "What is the role of FHFA in regulating mortgage insurers?",
            "How do MIs maintain GSE-approved status and what happens if they lose it?",
        ],
        doc_id_hints=[
            "INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09",
            "INDUSTRY_FHFA_ANNUAL_REPORT_2024",
            "INDUSTRY_PMIERS_OVERVIEW_FHFA",
        ],
        related=["metrics/pmiers", "topics/mi_regulatory_landscape"],
    ),
    PageDef(
        slug="topics/us_mortgage_market",
        title="The US Mortgage Market and MI Penetration",
        purpose="Provide industry-level context on the US mortgage origination market, MI penetration in the high-LTV segment, and the cyclical dynamics analysts watch.",
        queries=[
            "What is the size of the US mortgage origination market and what share of high-LTV originations does private MI cover?",
            "How does the US mortgage market cycle affect MI new insurance written volumes?",
            "What is the market share split among the 6 US private mortgage insurers?",
        ],
        doc_id_hints=[
            "INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09",
            "INDUSTRY_USMI_WHITE_PAPER_2020-10",
            "INDUSTRY_FHFA_ANNUAL_REPORT_2024",
        ],
        related=["metrics/niw", "metrics/iif", "topics/mi_regulatory_landscape"],
    ),
    PageDef(
        slug="topics/mi_regulatory_landscape",
        title="MI Regulatory Landscape",
        purpose="Map the regulatory framework MIs operate under: state insurance regulation, GSE/FHFA oversight via PMIERs, federal capital frameworks, and recent regulatory developments.",
        queries=[
            "What are the regulatory bodies and frameworks that govern US private mortgage insurers?",
            "What is the relationship between state insurance regulation and PMIERs?",
            "What are the recent regulatory developments affecting US MIs?",
        ],
        doc_id_hints=[
            "INDUSTRY_PMIERS_OVERVIEW_FHFA",
            "INDUSTRY_USMI_RESILIENCY_2023-11",
            "INDUSTRY_FHFA_ANNUAL_REPORT_2024",
        ],
        related=["metrics/pmiers", "topics/gse_relationship", "topics/pmiers_aug_2024_update"],
    ),
    PageDef(
        slug="topics/catastrophe_impact_on_mi",
        title="Catastrophe and Hurricane Impact on MIs",
        purpose="Explain how natural catastrophes (hurricanes, wildfires) affect MI delinquencies, loss reserves, and how the MIs have managed recent events (Helene, Milton, California wildfires).",
        queries=[
            "How do natural catastrophes like hurricanes and wildfires affect mortgage insurance delinquencies and losses?",
            "What was the impact of Hurricanes Helene and Milton on the US MIs?",
            "How are MIs reserving and disclosing exposure to the 2025 California wildfires?",
        ],
        doc_id_hints=[
            "MTG_10-K_2024-12-31",
            "RDN_10-K_2024-12-31",
            "ESNT_10-K_2024-12-31",
            "ACT_10-K_2024-12-31",
        ],
        related=["metrics/loss_ratio", "metrics/iif"],
    ),
]

ALL_PAGES = METRIC_PAGES + COMPANY_PAGES + TOPIC_PAGES


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

_AUTHORING_SYSTEM_PROMPT = """\
You are authoring a page for the MI Wiki, an LLM-maintained knowledge
base about US private mortgage insurance. Read the schema below before
writing.

<schema>
{schema}
</schema>

<page_definition>
slug: {slug}
title: {title}
purpose: {purpose}
related_pages: {related}
</page_definition>

<retrieved_context>
The following are excerpts from the dsRAG knowledge base, retrieved
by issuing the page's source-gathering queries. Each excerpt is tagged
with its `doc_id`. Use these as your grounding — do not invent figures
or assert claims that aren't supported by an excerpt.

{context}
</retrieved_context>

Write the page in markdown, following the exact section structure from
the schema (title heading, summary blockquote, "What it is", "Why it
matters", "Current state (as of YYYY-MM-DD)", "How it has evolved",
"Sources", "Related"). The "Current state" date should be the most
recent period referenced in your retrieved context.

Cite specific facts inline with `(doc_id)` parentheses — plain parens,
no backticks, no italics, e.g. `(MTG_10-K_2024-12-31)`. The Sources
section at the bottom should list every doc_id you cited, with one
sentence describing what it contributed.

For "Related", reproduce EXACTLY the related_pages list provided above —
do not add other slugs, do not invent new pages. Format each entry as
a markdown wikilink, one per line: `- [[metrics/persistency]]`. If
related_pages is "(none)", omit the Related section.

Write in an analyst-perspective voice — direct, factual, no marketing
language. Aim for 400-800 words on the body (excluding sources/related).
"""


def _load_schema() -> str:
    schema_path = WIKI_ROOT / "AGENTS.md"
    if schema_path.exists():
        return schema_path.read_text()
    return "(AGENTS.md not found)"


def _gather_context(page: PageDef, kb, max_segments: int = 12) -> str:
    """Run each of the page's queries against dsRAG and concatenate
    the top-scoring segments. Returns the formatted context block."""
    from src.application.orchestrator.workflow.tools import dsrag_kb  # noqa: F401
    # We call dsRAG directly to avoid the tool-decorator overhead
    from src.infrastructure.dsrag_kb import get_search_queries, smart_rrf_alpha

    seen_keys: set[tuple] = set()
    accumulated: list[dict] = []

    # Cycle through doc_id_hints across queries; pad with None for unscoped
    hints = page.doc_id_hints or [None]
    for i, q in enumerate(page.queries):
        doc_id = hints[i % len(hints)] if hints else None
        try:
            sub_queries = get_search_queries(q, max_queries=4)
        except Exception:
            sub_queries = [q]

        metadata_filter = (
            {"field": "doc_id", "operator": "equals", "value": doc_id}
            if doc_id
            else None
        )
        kb._rrf_alpha = smart_rrf_alpha(q)
        try:
            results = kb.query(sub_queries, metadata_filter=metadata_filter)
        except Exception as e:
            print(f"    query failed: {e}")
            continue
        finally:
            kb._rrf_alpha = 0.4

        for r in results[:5]:  # take top 5 per query
            d_id = r.get("doc_id", "")
            content = r.get("content") or r.get("text") or ""
            key = (d_id, content[-300:])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            accumulated.append({
                "doc_id": d_id,
                "score": r.get("score", 0.0),
                "content": content[:5000],
            })

    # Sort by score descending, take top max_segments
    accumulated.sort(key=lambda s: s.get("score", 0.0) or 0.0, reverse=True)
    top = accumulated[:max_segments]

    blocks = []
    for s in top:
        blocks.append(f"[doc_id: {s['doc_id']}]\n{s['content']}")
    return "\n\n---\n\n".join(blocks)


def _author_page(page: PageDef, context: str, schema: str) -> str:
    """Ask DeepSeek to author the page from the gathered context."""
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY") or os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        timeout=300.0,
    )

    related_str = ", ".join(page.related) if page.related else "(none)"
    system = _AUTHORING_SYSTEM_PROMPT.format(
        schema=schema,
        slug=page.slug,
        title=page.title,
        purpose=page.purpose,
        related=related_str,
        context=context,
    )

    resp = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=4000,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Write the wiki page now."},
        ],
    )
    return (resp.choices[0].message.content or "").strip()


def generate_page(page: PageDef, kb, schema: str) -> Path:
    print(f"\n[{page.slug}]")
    print(f"  purpose: {page.purpose[:100]}")

    context = _gather_context(page, kb)
    if not context:
        print("  WARN: no context retrieved — skipping")
        return None

    print(f"  context: {len(context):,} chars from {context.count('[doc_id:')} segments")

    page_md = _author_page(page, context, schema)
    out_path = WIKI_ROOT / f"{page.slug}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page_md)
    print(f"  wrote {len(page_md):,} chars → {out_path.relative_to(_REPO_ROOT)}")
    return out_path


def generate_index(pages: list[PageDef]) -> Path:
    """Generate index.md cataloging all pages by category."""
    lines = [
        "# MI Wiki — index",
        "",
        "LLM-maintained knowledge base for the US private mortgage insurance",
        "industry. Schema and conventions: [[AGENTS]].",
        "",
        "## Metrics",
        "",
    ]
    for p in METRIC_PAGES:
        lines.append(f"- [[{p.slug}]] — {p.purpose}")
    lines += ["", "## Companies", ""]
    for p in COMPANY_PAGES:
        lines.append(f"- [[{p.slug}]] — {p.purpose}")
    lines += ["", "## Topics", ""]
    for p in TOPIC_PAGES:
        lines.append(f"- [[{p.slug}]] — {p.purpose}")

    out_path = WIKI_ROOT / "index.md"
    out_path.write_text("\n".join(lines) + "\n")
    print(f"\nWrote index → {out_path.relative_to(_REPO_ROOT)}")
    return out_path


def main():
    selected_slugs = sys.argv[1:]
    if selected_slugs:
        pages = [p for p in ALL_PAGES if p.slug in selected_slugs]
        if not pages:
            sys.exit(f"No matching pages for slugs: {selected_slugs}")
    else:
        pages = ALL_PAGES

    # Configure DeepSeek-as-OpenAI for both auto-query and authoring
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        sys.exit("ERROR: DEEPSEEK_API_KEY not set")
    os.environ.setdefault("OPENAI_API_KEY", api_key)
    os.environ.setdefault(
        "DSRAG_OPENAI_BASE_URL",
        os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    )

    from src.infrastructure.dsrag_kb import get_kb
    kb = get_kb()

    schema = _load_schema()

    print(f"Generating {len(pages)} wiki pages...")
    for page in pages:
        try:
            generate_page(page, kb, schema)
        except Exception as e:
            print(f"  ERROR on {page.slug}: {type(e).__name__}: {e}")
            import traceback; traceback.print_exc()

    if not selected_slugs:
        # Only regen the index when generating everything, so partial
        # runs don't blow away references to existing pages.
        generate_index(pages)


if __name__ == "__main__":
    main()
