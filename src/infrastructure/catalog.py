"""Catalog of available filings, derived from the loaded dsRAG KB.

The catalog reads doc_ids directly from `kb.chunk_db.get_all_doc_ids()` so
it can never drift from the KB contents. (Earlier this module scanned a
hardcoded `data/parsed/` directory; that broke whenever the KB pointed
at a different corpus, e.g. the MI corpus at `data.mi/dsrag_store`.)

`format_for_prompt` renders the catalog as a compact block for the agent's
system prompt so the agent can map (ticker, period) → doc_id without
calling a tool.
"""

from __future__ import annotations

import re
from pathlib import Path

from loguru import logger

_REPO_ROOT = Path(__file__).resolve().parents[2]
# Filesystem fallback: only consulted if chunk_db can't be loaded.
PARSED_ROOT = _REPO_ROOT / "data" / "parsed"

# doc_ids in chunk_db have no .md suffix. Same pattern otherwise.
_DOC_ID_RE = re.compile(
    r"^(?P<ticker>[A-Z]+)_(?P<form>10-K|10-Q|10-K-A|10-Q-A|8-K|8-K-A|TRANSCRIPT)_(?P<period>\d{4}-\d{2}-\d{2})$"
)
_INDUSTRY_DOC_ID_RE = re.compile(r"^INDUSTRY_(?P<slug>.+)$")

# Filesystem-fallback patterns (with .md suffix).
_PARSED_MD_RE = re.compile(
    r"^(?P<ticker>[A-Z]+)_(?P<form>10-K|10-Q|10-K-A|10-Q-A|8-K|8-K-A|TRANSCRIPT)_(?P<period>\d{4}-\d{2}-\d{2})\.md$"
)
_INDUSTRY_MD_RE = re.compile(r"^INDUSTRY_(?P<slug>.+)\.md$")

# Human-readable labels for industry docs, keyed on doc_id (no extension).
# Anything not listed here falls back to the slug as the type and an
# empty period label.
_INDUSTRY_LABELS: dict[str, tuple[str, str]] = {
    "INDUSTRY_PMIERS_2.0_BASE": ("PMIERs 2.0 base requirements", "Fannie Mae"),
    "INDUSTRY_PMIERS_GUIDANCE_2024-01": ("PMIERs Guidance 2024-01 (Aug 2024 update)", "Freddie Mac"),
    "INDUSTRY_PMIERS_GUIDANCE_2024-02": ("PMIERs Guidance 2024-02", "Freddie Mac"),
    "INDUSTRY_PMIERS_OVERVIEW_FHFA": ("PMIERs overview", "FHFA"),
    "INDUSTRY_USMI_WHITE_PAPER_2020-10": ("USMI policy white paper", "Oct 2020"),
    "INDUSTRY_USMI_RESILIENCY_2023-11": ("USMI resiliency white paper", "Nov 2023"),
    "INDUSTRY_USMI_PMIERS_FACTSHEET_2015-10": ("USMI PMIERs fact sheet", "Oct 2015"),
    "INDUSTRY_FHFA_ANNUAL_REPORT_2024": ("FHFA Annual Report to Congress", "FY 2024 (published 2025)"),
    "INDUSTRY_FHFA_PAR_2024": ("FHFA Performance and Accountability Report", "FY 2024 (published 2025)"),
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
        quarter = (month - 1) // 3 + 1
        return f"Q{quarter} {year} call"
    if form == "8-K":
        return f"{period_end} (8-K)"
    return period_end


def _filing_dict_from_doc_id(doc_id: str) -> dict | None:
    """Parse a doc_id (no extension) into the catalog dict shape."""
    m = _DOC_ID_RE.match(doc_id)
    if m:
        ticker = m.group("ticker")
        form = m.group("form").replace("-A", "/A")
        period_end = m.group("period")
        return {
            "ticker": ticker,
            "company": TICKER_TO_COMPANY.get(ticker, ticker),
            "filing_type": form,
            "period_end": period_end,
            "period_label": _period_label(form, period_end),
            "doc_id": doc_id,
        }
    im = _INDUSTRY_DOC_ID_RE.match(doc_id)
    if im:
        filing_type, period_label = _INDUSTRY_LABELS.get(
            doc_id, (im.group("slug"), "")
        )
        return {
            "ticker": "INDUSTRY",
            "company": "Industry / Regulatory",
            "filing_type": filing_type,
            "period_end": "",
            "period_label": period_label,
            "doc_id": doc_id,
        }
    return None


def list_filings() -> list[dict]:
    """Return one dict per filing in the loaded KB's chunk_db.

    Falls back to scanning PARSED_ROOT if the KB can't be loaded — useful
    for tooling that runs before the KB is built (e.g. the build_kb
    pipeline itself or eval scripts that introspect the corpus).
    """
    try:
        from src.infrastructure.dsrag_kb import get_kb

        kb = get_kb()
        doc_ids = sorted(kb.chunk_db.get_all_doc_ids())
    except Exception as e:
        logger.warning(
            f"catalog: chunk_db unavailable ({e}); falling back to "
            f"filesystem scan of {PARSED_ROOT}"
        )
        return _list_filings_from_disk()

    out: list[dict] = []
    for doc_id in doc_ids:
        d = _filing_dict_from_doc_id(doc_id)
        if d is not None:
            out.append(d)
    return out


def _list_filings_from_disk() -> list[dict]:
    """Filesystem fallback: scan PARSED_ROOT for *.md filings."""
    if not PARSED_ROOT.exists():
        return []
    out: list[dict] = []
    for md in sorted(PARSED_ROOT.glob("*.md")):
        m = _PARSED_MD_RE.match(md.name)
        if m:
            ticker = m.group("ticker")
            form = m.group("form").replace("-A", "/A")
            period_end = m.group("period")
            out.append(
                {
                    "ticker": ticker,
                    "company": TICKER_TO_COMPANY.get(ticker, ticker),
                    "filing_type": form,
                    "period_end": period_end,
                    "period_label": _period_label(form, period_end),
                    "doc_id": md.stem,
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
