"""Parse Insider Monkey transcripts into clean markdown.

Walks data.mi/raw/transcripts/{TICKER}/{period}/{TICKER}_Q{N}_{year}.txt and
emits data.mi/parsed/{TICKER}_TRANSCRIPT_{period}.md after stripping the
leading article metadata and the trailing IM widget.

Conservative approach — only trims at the head and tail. Inter-page UI
button bursts inside the transcript are left in place rather than risk
removing real content.

Head trim: drop everything before the first speaker turn ("Operator:",
"Conference Operator:", or "FirstName LastName:"). This drops:
    News / - / Transcripts / {Company} Earnings Call Transcript /
    Published on... by Insider Monkey Transcripts / in / News / , /
    Transcripts / Share / Page 1 of N / Next >> / [restated title]

Tail trim: cut from the FIRST trailing footer marker through end of file.
Markers (any of):
    "Insider Monkey Quarterly Strategy"
    "Related Insider Monkey Articles"
    "Hedge Fund Resource Center"
    "Billionaire Hedge Funds"
The earliest of these (after the transcript content) anchors the cut.
"""
from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = _REPO_ROOT / "data.mi" / "raw" / "transcripts"
PARSED_DIR = _REPO_ROOT / "data.mi" / "parsed"

# Trailing-footer markers. The IM widget always begins with one of these
# two lines (Related Articles → Quarterly Strategy → Resource Center →
# Billionaires). To excise the entire widget we cut at the START marker,
# not the LAST marker in the widget. The widget repeats once per IM page
# break, so we anchor at the LAST occurrence (== final widget at EOF).
TAIL_MARKERS = (
    "Related Insider Monkey Articles",
    "Insider Monkey Quarterly Strategy",
)

# Speaker turn: "Operator:", "Conference Operator:", "Mark Casale:" etc.
# Allow up to 4 capitalized words then optional space and required colon.
SPEAKER_TURN_RE = re.compile(
    r"^\s*(?:"
    r"(?:Conference\s+)?Operator"
    r"|[A-Z][a-zA-Z\.\']{1,30}(?:\s+[A-Z][a-zA-Z\.\']{1,30}){0,3}"
    r")\s*:\s*$",
)


def _clean_one(text: str) -> str:
    lines = text.split("\n")

    # Head trim: drop everything before the first speaker turn.
    head = 0
    for i, line in enumerate(lines):
        if SPEAKER_TURN_RE.match(line):
            head = i
            break
    lines = lines[head:]

    # Tail trim: anchor at the LAST occurrence of "Follow {Company}", the
    # first line of every IM tail block (UI buttons + privacy + taxonomy +
    # related articles + Quarterly Strategy widget + billionaires).
    # Falls back to "Related Insider Monkey Articles" then "Insider Monkey
    # Quarterly Strategy" if absent. Markers repeat per IM page break, so
    # LAST occurrence anchors the bottom-of-file widget. Mid-text repeats
    # remain — user accepts small residual noise vs. risking content loss.
    last_follow = -1
    last_related = -1
    last_quarterly = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if re.match(r"^Follow\s+[A-Z]", s):
            last_follow = i
        elif s.startswith("Related Insider Monkey Articles"):
            last_related = i
        elif s.startswith("Insider Monkey Quarterly Strategy"):
            last_quarterly = i
    if last_follow >= 0:
        tail = last_follow
        # IM doubles the Follow line — walk back over consecutive Follow
        # lines so the cut lands at the start of the run, not mid-run.
        while tail > 0 and re.match(r"^Follow\s+[A-Z]", lines[tail - 1].strip()):
            tail -= 1
    elif last_related >= 0:
        tail = last_related
    elif last_quarterly >= 0:
        tail = last_quarterly
    else:
        tail = len(lines)
    lines = lines[:tail]

    return "\n".join(lines).strip()


def parse_all() -> None:
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    paths = sorted(RAW_DIR.rglob("*.txt"))
    written = 0
    for path in paths:
        # path: data.mi/raw/transcripts/TICKER/{period}/{TICKER}_Q{N}_{year}.txt
        try:
            ticker = path.parts[-3]
            period = path.parts[-2]
        except IndexError:
            print(f"  SKIP (unexpected path): {path}")
            continue

        out_path = PARSED_DIR / f"{ticker}_TRANSCRIPT_{period}.md"
        raw = path.read_text(encoding="utf-8", errors="ignore")
        cleaned = _clean_one(raw)

        before = len(raw.split())
        after = len(cleaned.split())
        ratio = after / before if before else 0.0

        out_path.write_text(cleaned, encoding="utf-8")
        print(f"  {out_path.name}: {before:>5}w → {after:>5}w  ({ratio:.0%} kept)")
        written += 1
    print(f"\nWrote {written} transcripts to {PARSED_DIR}")


if __name__ == "__main__":
    parse_all()
