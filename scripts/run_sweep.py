"""Run the 2x2x2 retrieval sweep on the FB eval set and produce a comparison table.

Sweep dimensions:
- HYBRID_BM25:        false, true       (semantic-only vs hybrid w/ BM25 + RRF)
- RERANKER:           '', 'flashrank'   (no reranker vs FlashRank cross-encoder)
- RETRIEVAL_TOP_K:    50, 200           (candidate-pool size per retriever)

8 runs total. Each appends an entry to eval/logs.json; we tag each with
the config and aggregate at the end.

Pre-reqs: data symlink → data.financebench, eval/questions_financebench.csv
must exist. Run from agent_fin/.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "eval" / "logs.json"

CONFIGS: list[dict] = [
    # (label, hybrid, reranker, top_k)
    {"label": "1a_semantic_no-rerank_top200", "bm25": "false", "reranker": "",          "top_k": "200"},
    {"label": "1b_semantic_no-rerank_top50",  "bm25": "false", "reranker": "",          "top_k": "50"},
    {"label": "2a_hybrid_no-rerank_top200",   "bm25": "true",  "reranker": "",          "top_k": "200"},
    {"label": "2b_hybrid_no-rerank_top50",    "bm25": "true",  "reranker": "",          "top_k": "50"},
    {"label": "3a_semantic_rerank_top200",    "bm25": "false", "reranker": "flashrank", "top_k": "200"},
    {"label": "3b_semantic_rerank_top50",     "bm25": "false", "reranker": "flashrank", "top_k": "50"},
    {"label": "4a_hybrid_rerank_top200",      "bm25": "true",  "reranker": "flashrank", "top_k": "200"},
    {"label": "4b_hybrid_rerank_top50",       "bm25": "true",  "reranker": "flashrank", "top_k": "50"},
]


def _read_latest_log() -> dict:
    return json.loads(LOGS.read_text())[-1]


def _avg_calls(results_path: Path) -> float:
    rows = list(csv.DictReader(results_path.open()))
    total = sum(len(json.loads(r["tool_calls"])) for r in rows)
    return total / max(len(rows), 1)


def main() -> None:
    venv_py = REPO / ".venv" / "bin" / "python"

    # Capture pre-existing log length so we can identify which entries
    # belong to this sweep.
    pre_count = len(json.loads(LOGS.read_text())) if LOGS.exists() else 0

    results: list[dict] = []
    for cfg in CONFIGS:
        env = os.environ.copy()
        env["HYBRID_BM25"] = cfg["bm25"]
        env["RERANKER"] = cfg["reranker"]
        env["RETRIEVAL_TOP_K"] = cfg["top_k"]

        print(f"\n=== {cfg['label']} ===")
        print(f"    BM25={cfg['bm25']}  reranker={cfg['reranker'] or '(none)'}  top_k={cfg['top_k']}")
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

    # Print final comparison table
    print("\n\n" + "=" * 100)
    print("FINAL COMPARISON TABLE")
    print("=" * 100)
    header = f"{'config':<35}  {'acc':>5}  {'time':>5}  {'cost':>8}  {'avg calls/q':>11}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['label']:<35}  "
              f"{r['accuracy']:>5.1%}  "
              f"{r['run_seconds']:>4.0f}s  "
              f"${r['cost_usd']:>7.4f}  "
              f"{r['avg_calls']:>11.2f}")

    # Persist for later reference
    out = REPO / "eval" / "results" / f"sweep_{int(time.time())}.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nFull sweep data written to {out}")


if __name__ == "__main__":
    main()
