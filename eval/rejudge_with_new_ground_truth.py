"""Re-judge existing LangSmith run answers against newly-authored ground
truth from eval/inputs/analyst_questions/ground_truth.json.

Does NOT re-run the agent. Pulls agent answers from a prior LangSmith
experiment, calls Bedrock Haiku as judge with the same prompt
langsmith_eval.py uses, records pass/fail + rationale.

Usage:
    python eval/rejudge_with_new_ground_truth.py \
        --experiment analyst-156-baseline \
        --topics 01-quarterly-results

Add more topics as ground_truth.json grows.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import Client
from loguru import logger
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import settings  # noqa: E402

GROUND_TRUTH_PATH = ROOT / "eval" / "inputs" / "analyst_questions" / "ground_truth.json"


class CorrectnessJudgment(BaseModel):
    correct: bool = Field(description="Whether the model answer captures the key facts in the reference answer")
    rationale: str = Field(description="Brief explanation, ≤30 words")


JUDGE_SYSTEM = (
    "You are a strict grader for an SEC-filings RAG agent eval. Compare the model "
    "answer to the reference answer. Return correct=True ONLY if the model answer "
    "captures the key facts in the reference answer (specific figures, names, "
    "dates, and qualitative characterizations where present). Return correct=False "
    "if the model answer contradicts the reference, omits a key fact, or "
    "fabricates information not in the reference. Brief rationale, ≤30 words."
)


def _judge_model():
    return ChatBedrockConverse(
        model_id=settings.ROUTER_MODEL_ID,
        region_name=settings.AWS_REGION,
        temperature=0,
    )


def judge_one(question: str, model_answer: str, reference: str, judge) -> CorrectnessJudgment:
    structured = judge.with_structured_output(CorrectnessJudgment)
    user_prompt = (
        f"Question:\n{question}\n\n"
        f"Reference answer:\n{reference}\n\n"
        f"Model answer:\n{model_answer}\n\n"
        f"Grade per system instructions."
    )
    return structured.invoke([
        SystemMessage(content=JUDGE_SYSTEM),
        HumanMessage(content=user_prompt),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", default="analyst-156-baseline",
                        help="experiment name prefix to find in LangSmith")
    parser.add_argument("--topics", nargs="+",
                        default=["01-quarterly-results"],
                        help="ground_truth.json topic keys to re-judge")
    args = parser.parse_args()

    # Load new ground truth.
    gt = json.loads(GROUND_TRUTH_PATH.read_text())
    questions_to_rejudge: dict[str, dict] = {}  # question_text -> {topic, qid, expected_answer}
    for topic in args.topics:
        if topic not in gt:
            logger.error(f"Topic {topic!r} not in ground_truth.json")
            sys.exit(1)
        for qid, entry in gt[topic].items():
            if qid.startswith("_"):
                continue
            questions_to_rejudge[entry["question"]] = {
                "topic": topic,
                "qid": qid,
                "expected_answer": entry["expected_answer"],
            }
    logger.info(f"Re-judging {len(questions_to_rejudge)} questions across topics: {args.topics}")

    # Connect to LangSmith.
    client = Client()
    projs = list(client.list_projects(name_contains=args.experiment))
    if not projs:
        logger.error(f"No experiment found containing {args.experiment!r}")
        sys.exit(1)
    proj = projs[0]
    logger.info(f"Using experiment: {proj.name}")

    # Pull all root runs from the experiment, indexed by question text.
    all_runs = list(client.list_runs(project_id=proj.id, is_root=True))
    runs_by_q: dict[str, dict] = {}
    for r in all_runs:
        q = (r.inputs or {}).get("question", "") if r.inputs else ""
        if q:
            runs_by_q[q] = {"id": r.id, "answer": (r.outputs or {}).get("answer", "")}
    logger.info(f"Pulled {len(runs_by_q)} runs from experiment")

    # Match each ground-truth question to its run, judge, record.
    judge = _judge_model()
    results: list[dict] = []
    missing: list[str] = []
    for q, gt_entry in questions_to_rejudge.items():
        if q not in runs_by_q:
            missing.append(q[:90])
            continue
        run = runs_by_q[q]
        if not run["answer"]:
            logger.warning(f"{gt_entry['qid']}: agent answer empty; skipping")
            continue
        t0 = time.time()
        verdict = judge_one(
            question=q,
            model_answer=run["answer"],
            reference=gt_entry["expected_answer"],
            judge=judge,
        )
        elapsed = time.time() - t0
        verdict_dict = {
            "topic": gt_entry["topic"],
            "qid": gt_entry["qid"],
            "question": q,
            "model_answer": run["answer"],
            "reference_answer": gt_entry["expected_answer"],
            "correct": verdict.correct,
            "rationale": verdict.rationale,
            "judge_seconds": round(elapsed, 2),
        }
        results.append(verdict_dict)
        logger.info(
            f"{gt_entry['qid']}: {'PASS' if verdict.correct else 'FAIL'} "
            f"({elapsed:.1f}s) — {verdict.rationale[:120]}"
        )

    if missing:
        logger.warning(f"{len(missing)} questions not found in experiment runs:")
        for q in missing:
            logger.warning(f"  - {q}")

    # Summary.
    n = len(results)
    n_correct = sum(1 for r in results if r["correct"])
    print()
    print("=" * 72)
    print(f"Re-judge complete — {n_correct}/{n} = {n_correct/max(1,n)*100:.1f}% correct")
    print(f"  topics: {args.topics}")
    print(f"  experiment: {proj.name}")
    print("=" * 72)
    print()
    print("Per-question:")
    for r in results:
        mark = "✅" if r["correct"] else "❌"
        print(f"  {mark} {r['qid']}: {r['rationale'][:140]}")

    # Persist results.
    out_path = ROOT / "eval" / "inputs" / "analyst_questions" / "rejudge_results.json"
    out_path.write_text(json.dumps({
        "experiment": proj.name,
        "topics": args.topics,
        "summary": {
            "n": n,
            "correct": n_correct,
            "accuracy": round(n_correct / max(1, n), 4),
        },
        "results": results,
    }, indent=2))
    print(f"\nResults saved: {out_path}")


if __name__ == "__main__":
    main()
