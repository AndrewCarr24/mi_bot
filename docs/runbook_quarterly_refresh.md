# Runbook: quarterly corpus + wiki refresh

Run this after each earnings season, once all six MIs have reported
(roughly: mid-Feb for Q4/10-K season, mid-May for Q1, mid-Aug for Q2,
mid-Nov for Q3). First executed end-to-end June 2026 (Q1 2026 season +
FY2022 backfill); time the steps took then is noted as a baseline.

Two venvs are involved — this is the #1 source of confusion:
- `./.venv` (agent_fin) — dsRAG, the app, build_kb, lint_wiki, evals
- `../.venv` (parse_sec parent) — sec_edgar_downloader, docling, bs4

---

## 0. Pre-flight (5 min)

```bash
cd agent_fin
ls -la data            # MUST point at data.mi — never data.financebench
tar -czf data.mi/dsrag_store.pre-<label>.tar.gz -C data.mi dsrag_store   # ~240MB, rollback point
```

Delete the snapshot once the refresh has settled (they're gitignored).

## 1. Fetch SEC filings (10 min)

Use `pipelines/fetchers.py::fetch_sec_filings` from the PARENT venv,
with filing-date windows per form. Earnings 8-Ks file ~4-6 weeks after
quarter end; 10-Qs ~6 weeks; 10-Ks Feb-Mar.

```python
from fetchers import fetch_sec_filings, _filter_8k_to_item_202, _extract_8k_ex99
TICKERS = ["MTG","RDN","ESNT","NMIH","ACT","ACGL"]
fetch_sec_filings(TICKERS, "data.mi/raw", form_type="10-Q", after=..., before=...)
fetch_sec_filings(TICKERS, "data.mi/raw", form_type="8-K",  after=..., before=...)
_filter_8k_to_item_202("data.mi/raw/sec-edgar-filings")   # drops non-earnings 8-Ks
_extract_8k_ex99("data.mi/raw/sec-edgar-filings")         # merges EX-99 exhibits → combined.htm
```

GOTCHA: `_extract_8k_ex99` merges multiple EX-99 exhibits into ONE
valid HTML document (`_merge_html_bodies`). Do not revert to naive
concatenation — docling stops at the first `</html>` and silently
drops the financial supplements (this lost every ACGL/ACT supplement
until June 2026).

## 2. Fetch transcripts (30-60 min, partly manual)

Per-source reality:
- **Radian**: deterministic IR-site PDFs — extend `scripts/transcripts/pull_radian.py`'s year/quarter list. Convert PDF→txt with pypdf (agent venv).
- **Others**: Insider Monkey (full transcripts, paginated; coverage began ~Q4 2022), Motley Fool, AlphaStreet. URLs are not guessable except AlphaStreet's slug pattern — hunt via web search; Yahoo Finance syndications of IM articles link back to the IM original (use the original — syndications truncate to page 1).
- Feed found URLs to `scripts/transcripts/pull_insider_monkey.py <jobs.json>` / the fool+alphastreet puller.
- Expect gaps; pre-Q4-2022 transcripts are paywall-only (Seeking Alpha). Record gaps in the welcome/coverage text if material.

Then parse: `./.venv/bin/python pipelines/parse_transcripts.py`
GOTCHA: the head/tail trimmer is tuned for Insider Monkey's format.
AlphaStreet articles use bare "Operator" lines and a related-articles
nav block — check the output `.md` is >15K chars; hand-clean if the
trimmer ate it (June 2026: MTG Q1'26 came out as 437 bytes).

## 3. Parse filings with docling (parent venv; ~1 min/doc)

```bash
/path/to/parse_sec/.venv/bin/python pipelines/parsers.py
```

Idempotent (skips existing `.md`). Verify supplements survived:

```bash
grep -c "NIW by credit quality" data.mi/parsed/ACGL_8-K_<latest>.md   # expect >=1
wc -c data.mi/parsed/*_8-K_<latest>.md                                # ACGL/ACT should be >100KB
```

## 4. Index into the KB (agent venv; ~1-3 min/doc, DeepSeek + Bedrock billable)

```bash
set -a; source .env; set +a
./.venv/bin/python -u pipelines/build_kb.py 2>&1 | tee /tmp/index.log
```

- Idempotent by doc_id; safe to interrupt and rerun (use `-u` — output is block-buffered otherwise and looks hung).
- If a previously-indexed doc was RE-parsed (content changed), delete its doc_id first via `kb.delete_document(doc_id)` or it will be skipped.
- Cost: ~$0.05-0.10/doc (semantic sectioning + AutoContext on deepseek-chat, Titan embeddings). Keep deepseek-chat as the AutoContext model for chunk-header consistency with the existing corpus.
- A laptop sleeping mid-run leaves the process hung on a dead socket: kill + rerun.

Verify: doc count + thin docs (<15 chunks = probable parse failure) + spot retrieval per new doc type.

## 5. Refresh the wiki (1-2 h)

For each company page + persistency/niw/pmiers/us_mortgage_market (and
any metric page the quarter's news touches):
1. Add a cited "### Q<N> 20XX update" block under `## Current state`,
   bump the as-of date in the header.
2. VERIFY EVERY FIGURE against the parsed filings by grep before
   writing — never from memory. (See wiki/AGENTS.md authoring rules.)
3. Sweep the page's `## Sources` section with the new doc_ids.
4. If the quarter resolved a forward-looking statement ("expected to
   close..."), rewrite it as fact.

Also update, if coverage changed: the simple-response prompt's coverage
text + welcome message (chat.py) + wiki/AGENTS.md layer description.
New wiki pages must be registered in ROUTER_PROMPT's <wiki_pages> list
or the router will never preload them.

## 6. Lint the wiki (30-60 min run + triage)

```bash
./.venv/bin/python pipelines/lint_wiki.py            # full corpus
./.venv/bin/python pipelines/lint_wiki.py metrics/x  # targeted
```

Report → `data.mi/wiki_lint_report.md`. Triage protocol:
- For each CONTRADICTED/unsupported finding, verify MANUALLY against
  the parsed filing (small grep windows — the linter's own retrieval
  misses things; June 2026 run: 8 findings = 5 real, 4 retrieval
  misses where the claim was verbatim in the filing).
- Fix real errors in the page AND its Sources line.
- The linter cannot catch absence-claims ("X doesn't disclose Y") —
  spot-check those by hand; they were the worst wiki bug to date.

## 7. Eval gates (15-25 min)

```bash
./.venv/bin/python eval/langsmith_eval.py run --tag <q>-refresh --concurrency 4                       # 28q
./.venv/bin/python eval/langsmith_eval.py run --dataset mi_v2_18q --tag <q>-refresh-v2 --concurrency 4 # 21q
./.venv/bin/python eval/session_eval.py run --tag <q>-refresh-sessions --concurrency 3                 # multi-turn
```

Report accuracy AND latency (mean/p50/p95) vs. the prior run. Norms as
of June 2026: 28q ≥27/28, v2 21/21, latency v2 mean ~10-17s / 28q mean
~18-30s. Two known flaky 28q questions (ACGL repurchase detail; the
subjective new-entrant stress question) — a single miss on those is
noise, two misses elsewhere is a regression.

GOTCHA: eval references go stale when the corpus improves — if the
agent now answers something a reference says is unanswerable, fix the
REFERENCE (verify against filings first), re-upload the dataset with
--force, and note it in the commit.

## 8. Ship

- Restart the local app (`uvicorn api:app --port 8001`) — prompts and
  KB are loaded at startup (wiki pages are read per-request).
- Commit in logical units: corpus/data, wiki content, prompt/code,
  eval datasets. Eval result CSVs in eval/results/ are tracked;
  separate results commits from code commits.
- AWS redeploy: batch with other improvements per repo convention
  (scripts/deploy.sh builds/pushes; service may be PAUSED — resume,
  then update-service to the new image tag, then re-pause if desired).

## Baseline timings (June 2026, Q1 2026 season + FY2022 backfill)

fetch ~10 min · transcripts ~1 h (incl. URL hunting) · parse 63 docs
~25 min · index ~110 docs ~4.5 h wall (interrupted once) · wiki refresh
~1.5 h · lint 528 claims ~45 min + triage 30 min · gates ~20 min.
A normal single-quarter refresh (~25 new docs) should run well under
half of this.
