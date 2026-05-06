# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`agent_fin` is a deploy-ready LangGraph ReAct agent over a [dsRAG](https://github.com/D-Star-AI/dsRAG) KB of SEC filings. Single retrieval tool (`dsrag_kb`); orchestrator LLM swappable between DeepSeek (default) and Bedrock; router and judge are always Bedrock Haiku.

This directory is its own git repo (origin: `AndrewCarr24/mi_bot`) — gitignored from the parent `parse_sec/`. Commits here don't show up in `parse_sec`'s log.

See README.md for setup, run commands, the local→deploy loop, and orchestrator switching.

## Architecture

**Three entrypoints share one core.** `run_app.py` (CLI), `api.py` (FastAPI with Chainlit mounted at `/chat`), and `chat.py` all call `streaming.get_streaming_response`. Behavior changes propagate to all three automatically.

**Graph topology:** `router_node → [route_by_intent] → wiki_preload | agent | simple_response → finalize? → memory_post_hook → END`. The router (Bedrock Haiku) classifies intent and may tag a wiki slug. `agent_node` is the ReAct loop; `should_continue` routes to `finalize_node` when `MAX_TOOL_CALLS_PER_TURN` is hit. No answer-cache node — the old `cache_check_node` placeholder was removed. The Bedrock prompt-cache (`cachePoint` blocks in `chains.py`) is unrelated and still load-bearing — don't delete it.

**`dsrag_kb` has two implementations, not one branching tool.** `get_tools()` in `workflow/tools.py` returns either the strict `doc_id: str | None` variant (`MULTI_DOC_FILTER=off`, the champion) or the list-accepting variant (`filter`/`quota`). Edits to one don't propagate.

**Settings have two consumption patterns.** `src/config.py` exports a `settings` singleton built once at import. Some callers in `workflow/{nodes,tools,edges}.py` deliberately read `os.environ.get(...)` live so runtime A/B knobs can flip mid-process without reloading the KB — don't migrate them to `settings.X`. Active runtime-flip knobs: `HISTORY_STRATEGY`, `MAX_TOOL_CALLS_PER_TURN`, `DISABLE_WIKI_PRELOAD`, `DEDUP_CHUNKS`, `RRF_ALPHA`, `AUTO_QUERY_MAX`, `MULTI_DOC_FILTER`.

**`data/` is a symlink** to `data.mi/` or `data.financebench/`. All code reads through `data/...` — never hardcode either real path. Use `./scripts/switch_kb.sh` to flip; the LangSmith eval pins MI explicitly via `DSRAG_STORE_DIR`.

## Evaluation

**Default to `eval/langsmith_eval.py`** over the CSV-based `eval/run_eval.py`. LangSmith experiments give cross-run comparison and same-config aggregation; CSVs are standalone. Keep the CSV path for fast local sanity checks only.

Two evaluators per question: `correctness` (LLM judge vs reference) and `retrieval_correctness` (deterministic doc_id check; catches structural failures where retrieval succeeded but cap+trim dropped data downstream). A faithfulness evaluator was prototyped and removed for cost; restore `FaithfulnessJudgment` and add it to evaluators in `cmd_run` to re-enable.

LangSmith dataset: `mi_28q_v1`. Tag experiments with `--tag <descriptive>` (e.g. `champion-off`, `refactor-pre`).

## Things that will trip you up

- **`run_eval.py` silently corrupts results** if `data/` points at the wrong KB. Run `switch_kb.sh` first.
- **`scripts/transcripts/` is gitignored** — URL JSONs are ad-hoc per fetch; scrapers depend on fragile site HTML. Don't expect reproducibility.
- **Eval result CSVs in `eval/results/` ARE tracked** by convention (`.gitignore` ~line 28). Separate code/dataset commits from accumulated results commits.
- **Pre-change KB snapshots** (`data.mi/dsrag_store.pre-*.tar.gz`) are gitignored. Create one before risky reindexes; delete once the change settles.
- **Don't propose AWS redeploys** until several local improvements are batched.
