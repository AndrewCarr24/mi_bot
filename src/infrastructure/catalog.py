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
    r"^(?P<ticker>[A-Z]+)_(?P<form>10-K|10-Q|10-K-A|10-Q-A)_(?P<period>\d{4}-\d{2}-\d{2})\.md$"
)

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
        if not m:
            continue
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
