# eval/

Regression-testing harness for the agent. Driven by a CSV of
`(question, expected_answer)` pairs; uses Bedrock Haiku as a judge to
grade each answer.

## Files

| Path | What it is |
|---|---|
| `run_eval.py` | The harness. `python eval/run_eval.py [csv_path]` |
| `pricing.py` | Per-model token rates for cost rollup |
| `usage.py` | LangChain callback that aggregates token usage |
| `results/*.csv` | Per-question detail for one eval run (committed; durable record) |
| `results/sweep_*.json` | Summary of one multi-run experiment (committed) |
| `results/alpha_sweep_*.json` | Summary of the α/dedup sweep |
| `logs.json` | Append-only chronological log (gitignored — noisy) |

## Running an eval

The default CSV is `eval/questions_financebench.csv`. That CSV is **not
checked in** — it's a copy of `sec_agent/eval/questions_financebench.csv`
from the parent repo. To run the FB regression eval:

```bash
./scripts/switch_kb.sh financebench
cp ../sec_agent/eval/questions_financebench.csv eval/   # one-time
set -a && . .env && set +a
python eval/run_eval.py
```

For the MI eval set (committed at `eval/questions_mi.csv` — 10
analyst-style questions about the 6 MI companies' 2024 10-Ks):

```bash
./scripts/switch_kb.sh mi
python eval/run_eval.py eval/questions_mi.csv
```

The MI eval set was hand-constructed (no MI-specific public benchmark
exists). Questions are framed from analyst concerns — PMIERs
sufficiency, persistency, reserve development, capital return,
regulatory impact — rather than derived from our parsed-data
chunking. Ground-truth answers verified against the filings.

## Sweep drivers

For systematic A/B tests, two driver scripts exist at the repo root:

- `scripts/run_sweep.py` — 2x2x2 retrieval matrix
  (semantic vs hybrid) × (no-rerank vs FlashRank) × (top_k 50 vs 200)
- `scripts/run_alpha_sweep.py` — 2x4 hybrid-only matrix
  (no-dedup vs dedup) × (α ∈ {0.4, 0.5, 0.6, smart})

Each runs all configurations sequentially and prints a final
comparison table. Outputs land in `eval/results/sweep_*.json` or
`alpha_sweep_*.json` for permanent record.

## Notable results to date (best-config history)

| Date | Eval set | Acc | Time | Cost | Avg calls/q | Notes |
|---|---|---:|---:|---:|---:|---|
| 2026-04-26 | FB | 20/23 | 506s | $0.073 | 1.22 | pre-hybrid baseline |
| 2026-04-27 | FB | 21/23 | 608s | $0.124 | 2.39 | + hybrid (BM25+vector RRF), doc_id filter fix |
| 2026-04-27 | FB | **22/23** | 618s | $0.128 | 2.52 | + parallel-call prompt |
| 2026-04-27 | FB | **22/23** | 509s | $0.085 | 1.61 | + α=0.4 — *most-accurate static* |
| 2026-04-27 | FB | 21/23 | **516s** | **$0.081** | **1.52** | + α=smart (current default) ⭐ |

Two notes:
- **α=0.4 is technically the most accurate static value** on this
  23-question FB eval (22/23 vs smart's 21/23 — one question of
  difference). We chose α=smart as the default anyway because it
  generalizes per question, runs 1 fewer tool call/q on average, and
  costs slightly less. The single-question gap is well within
  LLM-temperature noise across runs (e.g. Q20 has flipped between
  pass/fail across multiple runs at the same config).
- Switch to `RRF_ALPHA=0.4` as an env override if you want the
  squeezed-out accuracy on FB-shaped questions specifically.

See `eval/results/alpha_sweep_1777332640.json` for the full 2×4 sweep
that established these numbers.

## Adding a new eval to the historical record

1. Run the eval. It produces a CSV in `eval/results/` and appends a
   summary entry to `eval/logs.json`.
2. If the run is a meaningful baseline (new best config, regression
   probe of a notable change, etc.), `git add eval/results/<csv>` and
   commit it.
3. If the run is one cell in a sweep, the sweep driver writes a JSON
   summary; commit that too.
4. Update the table above with one row when a new headline config
   wins decisively. Keep it short.

The `logs.json` file isn't tracked by design — every eval run
mutates it, and the CSVs hold the same per-question detail. Use it
locally for chronological browsing.
