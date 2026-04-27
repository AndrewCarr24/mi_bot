import os
import re
import shutil
from pathlib import Path

from sec_edgar_downloader import Downloader


def _extract_period_from_submission(accession_dir: Path) -> str | None:
    """Read CONFORMED PERIOD OF REPORT from full-submission.txt → YYYY-MM-DD."""
    submission_file = accession_dir / "full-submission.txt"
    if not submission_file.exists():
        return None
    try:
        with open(submission_file, "r", encoding="utf-8", errors="ignore") as f:
            head = "".join(next(f) for _ in range(200))
    except (StopIteration, Exception):
        return None
    match = re.search(r"CONFORMED PERIOD OF REPORT:\s*(\d{8})", head)
    if not match:
        return None
    raw = match.group(1)
    return f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}"


def _reorganize_by_period(filings_dir: str):
    """Reorganize raw filings from {ticker}/{form}/{accession}/
    to {ticker}/{form}/{period}/{accession}/ so periods are visible
    in the folder structure.

    Skips directories that are already nested under a period folder
    (YYYY-MM-DD pattern).
    """
    filings_path = Path(filings_dir)
    if not filings_path.exists():
        return

    for ticker_dir in filings_path.iterdir():
        if not ticker_dir.is_dir():
            continue
        for form_dir in ticker_dir.iterdir():
            if not form_dir.is_dir():
                continue
            for child in list(form_dir.iterdir()):
                if not child.is_dir():
                    continue
                # Skip if already under a period folder (YYYY-MM-DD)
                if re.match(r"\d{4}-\d{2}-\d{2}$", child.name):
                    continue
                accession_name = child.name
                period = _extract_period_from_submission(child)
                if period is None:
                    print(f"  WARN: no period for {ticker_dir.name}/{form_dir.name}/{accession_name}, skipping reorg")
                    continue
                period_dir = form_dir / period
                period_dir.mkdir(exist_ok=True)
                dest = period_dir / accession_name
                if dest.exists():
                    continue
                shutil.move(str(child), str(dest))
                print(f"  Moved {ticker_dir.name}/{form_dir.name}/{accession_name} → …/{period}/{accession_name}")


def fetch_sec_filings(
    tickers: list[str],
    download_folder: str,
    form_type: str = "10-K",
    limit: int | None = None,
    after: str | None = None,
    before: str | None = None,
):
    """
    Downloads SEC filings for a list of tickers into the specified folder,
    then reorganizes by period: {ticker}/{form}/{period}/{accession}/.

    `after` / `before` are filing-date filters in YYYY-MM-DD form
    (sec-edgar-downloader matches against the SEC filing date, not the
    period of report). Pass `after="2023-04-01"` to capture all filings
    with periods Q1 2023 onward (Q1 2023 10-Qs file by mid-May 2023).

    `limit` caps the per-(ticker, form) result count. Defaults to None
    (no cap) when `after`/`before` are used; set explicitly for
    "most recent N" semantics.
    """
    print(f"Initializing SEC Edgar Downloader in {download_folder}...")

    dl = Downloader("AI_Eval_Tool", "eval_user@example.com", download_folder)

    for ticker in tickers:
        bound_desc = " ".join(
            f"{label}={val}"
            for label, val in [("limit", limit), ("after", after), ("before", before)]
            if val is not None
        ) or "(no bounds — most recent only)"
        print(f"Fetching {form_type} filings for {ticker} [{bound_desc}]...")
        try:
            kwargs = {"download_details": True}
            if limit is not None:
                kwargs["limit"] = limit
            if after is not None:
                kwargs["after"] = after
            if before is not None:
                kwargs["before"] = before
            dl.get(form_type, ticker, **kwargs)
            print(f"Successfully downloaded {ticker} {form_type}.")
        except Exception as e:
            print(f"Failed to download {ticker} {form_type}: {e}")

    filings_dir = os.path.join(download_folder, "sec-edgar-filings")
    print("Reorganizing raw filings by period...")
    _reorganize_by_period(filings_dir)


# Mortgage-insurance peer set: Enact, Essent, MGIC, Radian, Arch Capital, NMI.
MI_TICKERS = ["ACT", "ESNT", "MTG", "RDN", "ACGL", "NMIH"]


if __name__ == "__main__":
    rag_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(rag_app_dir, "data", "raw")
    print(f"Targeting download directory: {target_dir}")

    # Filing-date cutoff. Q1 2023 10-Qs (period 2023-03-31) file by mid-May
    # 2023; FY22 10-Ks (period 2022-12-31) file Feb-Mar 2023, so 2023-04-01
    # excludes them. This captures all filings with periods Q1 2023 forward.
    AFTER_DATE = "2023-04-01"

    fetch_sec_filings(MI_TICKERS, target_dir, form_type="10-K", after=AFTER_DATE)
    fetch_sec_filings(MI_TICKERS, target_dir, form_type="10-Q", after=AFTER_DATE)
