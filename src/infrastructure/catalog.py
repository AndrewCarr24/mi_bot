"""Catalog of available filings, derived from data/parsed/<TICKER>_<FORM>_<PERIOD>.md.

This is the source of truth for what the agent can answer about — the dsRAG
KB is built directly from these markdowns, and the doc_id assigned at
ingestion time is the filename stem (TICKER_FORM_PERIOD). `format_for_prompt`
renders the catalog as a compact block for the agent's system prompt so the
agent can map (ticker, period) → doc_id without calling a tool.
"""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
PARSED_ROOT = _REPO_ROOT / "data" / "parsed"

_PARSED_MD_RE = re.compile(
    r"^(?P<ticker>[A-Z]+)_(?P<form>10-K|10-Q|10-K-A|10-Q-A|8-K|8-K-A|TRANSCRIPT)_(?P<period>\d{4}-\d{2}-\d{2})\.md$"
)

# Industry / regulatory reference docs (PMIERs, USMI white papers, FHFA
# reports). Filename stem is INDUSTRY_<slug>, no fiscal period.
_INDUSTRY_MD_RE = re.compile(r"^INDUSTRY_(?P<slug>.+)\.md$")

# Human-readable labels for industry docs, keyed on filename stem (without
# extension). Maps to (filing_type, period_label). Anything not listed
# here falls back to the slug as the type and an empty period label.
_INDUSTRY_LABELS: dict[str, tuple[str, str]] = {
    "INDUSTRY_PMIERS_2.0_BASE": ("PMIERs 2.0 base requirements", "Fannie Mae"),
    "INDUSTRY_PMIERS_GUIDANCE_2024-01": ("PMIERs Guidance 2024-01 (Aug 2024 update)", "Freddie Mac"),
    "INDUSTRY_PMIERS_GUIDANCE_2024-02": ("PMIERs Guidance 2024-02", "Freddie Mac"),
    "INDUSTRY_PMIERS_OVERVIEW_FHFA": ("PMIERs overview", "FHFA"),
    "INDUSTRY_USMI_WHITE_PAPER_2020-10": ("USMI policy white paper", "Oct 2020"),
    "INDUSTRY_USMI_RESILIENCY_2023-11": ("USMI resiliency white paper", "Nov 2023"),
    "INDUSTRY_USMI_PMIERS_FACTSHEET_2015-10": ("USMI PMIERs fact sheet", "Oct 2015"),
    "INDUSTRY_FHFA_ANNUAL_REPORT_2024": ("FHFA Annual Report to Congress", "2024"),
    "INDUSTRY_FHFA_PAR_2024": ("FHFA Performance and Accountability Report", "FY 2024"),
    "INDUSTRY_FREDDIE_PMI_HANDBOOK_2021-09": ("Private MI Handbook (industry primer)", "Freddie Mac, Sep 2021"),
}

TICKER_TO_COMPANY = {
    "ACT": "Enact Holdings",
    "RDN": "Radian",
    "NMIH": "NMI Holdings",
    "ESNT": "Essent",
    "MTG": "MGIC",
    "ACGL": "Arch Capital",
    "AMD": "Advanced Micro Devices",
    "BA": "The Boeing Company",
    "AXP": "American Express",
}


def _period_label(filing_type: str, period_end: str) -> str:
    year = period_end[:4]
    month = int(period_end[5:7])
    form = filing_type.split("/", 1)[0].upper()
    if form == "10-K":
        return f"FY {year}"
    if form == "10-Q":
        quarter = (month - 1) // 3 + 1
        return f"Q{quarter} {year}"
    if form == "TRANSCRIPT":
        # Period is fiscal quarter end: 2024-09-30 → "Q3 2024 call"
        quarter = (month - 1) // 3 + 1
        return f"Q{quarter} {year} call"
    if form == "8-K":
        # Period is the event date (release/news date), not a fiscal period.
        return f"{period_end} (8-K)"
    return period_end


def list_filings() -> list[dict]:
    """Scan PARSED_ROOT and return one dict per markdown filing.

    Returns dicts with both machine-friendly (period_end, doc_id) and
    human-friendly (period_label, company) forms.
    """
    if not PARSED_ROOT.exists():
        return []
    out: list[dict] = []
    for md in sorted(PARSED_ROOT.glob("*.md")):
        m = _PARSED_MD_RE.match(md.name)
        if m:
            ticker = m.group("ticker")
            form = m.group("form").replace("-A", "/A")  # restore amended suffix
            period_end = m.group("period")
            out.append(
                {
                    "ticker": ticker,
                    "company": TICKER_TO_COMPANY.get(ticker, ticker),
                    "filing_type": form,
                    "period_end": period_end,
                    "period_label": _period_label(form, period_end),
                    # doc_id matches the dsRAG KB's ingestion convention.
                    "doc_id": md.stem,
                    "path": str(md),
                }
            )
            continue
        im = _INDUSTRY_MD_RE.match(md.name)
        if im:
            stem = md.stem
            filing_type, period_label = _INDUSTRY_LABELS.get(
                stem, (im.group("slug"), "")
            )
            out.append(
                {
                    "ticker": "INDUSTRY",
                    "company": "Industry / Regulatory",
                    "filing_type": filing_type,
                    "period_end": "",
                    "period_label": period_label,
                    "doc_id": stem,
                    "path": str(md),
                }
            )
    return out


def format_for_prompt() -> str:
    """Render the catalog as a compact table for the agent's system prompt."""
    filings = list_filings()
    if not filings:
        return "No filings indexed yet."
    lines = ["ticker | company | form | period_label | period_end | doc_id (filter on this)"]
    for f in filings:
        lines.append(
            f"{f['ticker']} | {f['company']} | {f['filing_type']} | "
            f"{f['period_label']} | {f['period_end']} | {f['doc_id']}"
        )
    return "\n".join(lines)
