"""2x4 sweep over (dedup ∈ {off, on}) × (alpha ∈ {0.5, 0.6, 0.4, smart}).

Skips the (dedup=off, alpha=0.5) cell since that's the prior 21/23 baseline.
7 runs total on the 23-question FB eval set. ~70 min wall-clock, ~$1 cost.

All cells share the same retrieval frame: hybrid (BM25+vector), no
reranker, top_k=200. Variations are entirely in chunk-dedup behavior
and RRF weighting.

Pre-reqs: data symlink → data.financebench, eval/questions_financebench.csv.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "eval" / "logs.json"

CONFIGS: list[dict] = [
    # (label, DEDUP_CHUNKS, RRF_ALPHA)
    {"label": "1_no-dedup_alpha-bm25-favored",  "dedup": "false", "alpha": "0.6"},
    {"label": "2_no-dedup_alpha-semantic-favored", "dedup": "false", "alpha": "0.4"},
    {"label": "3_no-dedup_alpha-smart",         "dedup": "false", "alpha": "smart"},
    {"label": "4_dedup_alpha-balanced",         "dedup": "true",  "alpha": "0.5"},
    {"label": "5_dedup_alpha-bm25-favored",     "dedup": "true",  "alpha": "0.6"},
    {"label": "6_dedup_alpha-semantic-favored", "dedup": "true",  "alpha": "0.4"},
    {"label": "7_dedup_alpha-smart",            "dedup": "true",  "alpha": "smart"},
]


def _read_latest_log() -> dict:
    return json.loads(LOGS.read_text())[-1]


def _avg_calls(results_path: Path) -> float:
    rows = list(csv.DictReader(results_path.open()))
    total = sum(len(json.loads(r["tool_calls"])) for r in rows)
    return total / max(len(rows), 1)


def main() -> None:
    venv_py = REPO / ".venv" / "bin" / "python"

    # Common base config: hybrid + no reranker + top_k=200
    base_env = os.environ.copy()
    base_env["HYBRID_BM25"] = "true"
    base_env["RETRIEVAL_TOP_K"] = "200"
    base_env["RERANKER"] = ""

    results: list[dict] = []
    for cfg in CONFIGS:
        env = dict(base_env)
        env["DEDUP_CHUNKS"] = cfg["dedup"]
        env["RRF_ALPHA"] = cfg["alpha"]

        print(f"\n=== {cfg['label']} ===")
        print(f"    DEDUP_CHUNKS={cfg['dedup']}  RRF_ALPHA={cfg['alpha']}")
        t0 = time.time()
        rc = subprocess.call(
            [str(venv_py), "-u", "eval/run_eval.py"],
            env=env, cwd=str(REPO),
        )
        wall = time.time() - t0
        if rc != 0:
            print(f"    eval failed (rc={rc})")
            continue

        latest = _read_latest_log()
        results_csv = REPO / "eval" / latest["results_file"]
        avg_calls = _avg_calls(results_csv)
        results.append({
            "label": cfg["label"],
            "config": cfg,
            "accuracy": latest["accuracy"],
            "n_correct": latest["n_correct"],
            "cost_usd": latest["total_cost_usd"],
            "run_seconds": latest["run_seconds"],
            "avg_calls": avg_calls,
            "wall_seconds": wall,
        })
        print(f"    → {latest['n_correct']}/23 ({latest['accuracy']:.0%}), "
              f"{latest['run_seconds']:.0f}s, ${latest['total_cost_usd']:.4f}, "
              f"avg {avg_calls:.2f} tool calls/q")

    # Final table
    print("\n\n" + "=" * 100)
    print("ALPHA × DEDUP SWEEP — final comparison")
    print("=" * 100)
    header = f"{'config':<38}  {'acc':>5}  {'time':>5}  {'cost':>8}  {'avg calls/q':>11}"
    print(header)
    print("-" * len(header))
    # Insert the prior baseline for context
    print(f"{'(0_baseline_no-dedup_alpha=0.5)':<38}  91.3%  625s  $0.1222  2.39")
    for r in results:
        print(f"{r['label']:<38}  "
              f"{r['accuracy']:>5.1%}  "
              f"{r['run_seconds']:>4.0f}s  "
              f"${r['cost_usd']:>7.4f}  "
              f"{r['avg_calls']:>11.2f}")

    out = REPO / "eval" / "results" / f"alpha_sweep_{int(time.time())}.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nFull sweep data written to {out}")


if __name__ == "__main__":
    main()
