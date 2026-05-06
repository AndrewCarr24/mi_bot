"""LangSmith eval pipeline: dataset upload + evaluators + experiments.

Two evaluators per question:
  - correctness          (LLM-judge vs reference answer; ports run_eval.py's logic)
  - retrieval_correctness (deterministic: did dsrag_kb retrieve the expected
                           doc_ids? catches structural failures where retrieval
                           succeeded but the cap+trim chain dropped data)

Note: a faithfulness evaluator (claims-vs-context check, ~30k-80k input
tokens per question) was prototyped but disabled to control Bedrock Haiku
spend. To re-enable, restore the FaithfulnessJudgment class +
faithfulness_evaluator and add it back to the evaluators list in cmd_run.

Usage:
    cd agent_fin
    # Upload (or refresh) the dataset to LangSmith — once per change:
    python eval/langsmith_eval.py upload

    # Run an experiment in OFF mode against the full 28-question dataset:
    python eval/langsmith_eval.py run --mode off --tag champion-off

    # Run only the 5 stress questions (Q24-Q28):
    python eval/langsmith_eval.py run --mode off --tag stress-only --stress-only

The script defers all retrieval-context inspection to the predictor's return
value — predictor returns answer + retrieved_doc_ids + retrieved_context, and
evaluators compare those fields directly. No run-tree walking required.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[1]))

# Pin MI KB as default for this eval pipeline. The dataset is MI-cohort-
# specific, so accidentally running against data.financebench produces
# meaningless "no MI filings in catalog" results. Set DSRAG_STORE_DIR
# explicitly in your shell or .env to override (e.g. for a different
# corpus eval).
_MI_STORE = _HERE.parents[1] / "data.mi" / "dsrag_store"
if _MI_STORE.is_dir():
    os.environ.setdefault("DSRAG_STORE_DIR", str(_MI_STORE))

from langchain_aws import ChatBedrockConverse  # noqa: E402
from langsmith import Client, aevaluate  # noqa: E402
from loguru import logger  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from src.application.orchestrator.streaming import get_streaming_events  # noqa: E402
from src.config import settings  # noqa: E402  (also propagates .env into os.environ)
from src.infrastructure.model import extract_text_content  # noqa: E402


DATASET_NAME = "mi_28q_v1"
DATASET_DESCRIPTION = (
    "MI cohort eval set: original 23 financial questions + 5 stress questions "
    "(yield drift, control weakness, Arch repurchases, pricing analytical, "
    "8-K board changes). Reference outputs include expected_answer, optional "
    "expected_doc_ids, and optional key_facts."
)


# ── Reference data: questions + retrieval-correctness expectations ──────────
#
# expected_doc_ids is the set of filings that MUST appear in dsrag_kb's
# returned segments for the agent to have enough evidence to answer correctly.
# Soft list (partial credit if some retrieved). Empty list means "any
# retrieval is fine; correctness is judged on the answer text alone."

STRESS_EXPECTED_DOC_IDS = {
    24: ["MTG_10-K_2024-12-31", "RDN_10-K_2024-12-31", "ESNT_10-K_2024-12-31",
         "NMIH_10-K_2024-12-31", "ACT_10-K_2024-12-31", "ACGL_10-K_2024-12-31"],
    25: ["MTG_10-K_2024-12-31", "RDN_10-K_2024-12-31", "ESNT_10-K_2024-12-31",
         "NMIH_10-K_2024-12-31", "ACT_10-K_2024-12-31", "ACGL_10-K_2024-12-31"],
    26: ["ACGL_10-K_2024-12-31", "ACGL_8-K_2025-02-10", "ACGL_TRANSCRIPT_2024-12-31"],
    27: [],  # subjective question; multiple defensible answers
    28: ["MTG_8-K_2024-01-31"],  # the Thompson-appointment 8-K
}


def _read_csv_rows(csv_path: Path) -> list[dict]:
    with csv_path.open() as f:
        return list(csv.DictReader(f))


def _build_examples(csv_path: Path) -> list[dict]:
    """Build LangSmith example dicts from the 28q CSV."""
    examples = []
    rows = _read_csv_rows(csv_path)
    for i, row in enumerate(rows, 1):
        outputs: dict = {"expected_answer": row["expected_answer"]}
        if i in STRESS_EXPECTED_DOC_IDS:
            outputs["expected_doc_ids"] = STRESS_EXPECTED_DOC_IDS[i]
        examples.append({
            "inputs": {"question": row["question"]},
            "outputs": outputs,
            "metadata": {"qnum": i, "is_stress": i >= 24},
        })
    return examples


def cmd_upload(args) -> None:
    """Create or refresh the LangSmith dataset."""
    client = Client()
    csv_path = _HERE.parent / args.csv
    examples = _build_examples(csv_path)

    # Check if dataset already exists
    existing = list(client.list_datasets(dataset_name=DATASET_NAME))
    if existing:
        ds = existing[0]
        if not args.force:
            print(
                f"Dataset {DATASET_NAME!r} already exists (id={ds.id}). "
                f"Use --force to replace its examples."
            )
            return
        # Delete existing examples then re-add
        existing_examples = list(client.list_examples(dataset_id=ds.id))
        for ex in existing_examples:
            client.delete_example(ex.id)
        print(f"Deleted {len(existing_examples)} existing examples from {DATASET_NAME!r}")
    else:
        ds = client.create_dataset(
            dataset_name=DATASET_NAME,
            description=DATASET_DESCRIPTION,
        )
        print(f"Created dataset {DATASET_NAME!r} (id={ds.id})")

    client.create_examples(dataset_id=ds.id, examples=examples)
    print(f"Uploaded {len(examples)} examples to {DATASET_NAME!r}")
    n_stress = sum(1 for e in examples if e["metadata"]["is_stress"])
    print(f"  {n_stress} stress questions (with expected_doc_ids)")
    print(f"  {len(examples) - n_stress} original questions")


# ── Predictor ───────────────────────────────────────────────────────────────

async def predictor(inputs: dict) -> dict:
    """Invoke the agent on a single question. Returns answer + retrieval
    metadata that the evaluators consume."""
    import uuid
    question = inputs["question"]
    answer_parts: list[str] = []
    tool_calls: list[dict] = []
    retrieved_segments: list[dict] = []

    # Unique thread per question so DEDUP_CHUNKS state and message history
    # don't leak across examples. (Passing None falls back to the shared
    # 'default-thread' which would taint cross-example results.)
    thread_id = f"ls-eval-{uuid.uuid4().hex[:12]}"

    async for ev in get_streaming_events(
        messages=question,
        customer_name="Evaluator",
        conversation_id=thread_id,
    ):
        kind = ev.get("kind")
        if kind == "answer_token":
            answer_parts.append(ev["text"])
        elif kind == "rewind_to_thinking":
            text = ev["text"]
            joined = "".join(answer_parts)
            if joined.endswith(text):
                answer_parts = [joined[: -len(text)]]
        elif kind == "tool_call":
            tool_calls.append({"tool": ev["tool"], "args": ev.get("args", {})})
        elif kind == "tool_result_segment":
            retrieved_segments.append({
                "doc_id": ev.get("doc_id", ""),
                "score": ev.get("score"),
                "content": ev.get("content", ""),
            })

    retrieved_doc_ids = sorted({s["doc_id"] for s in retrieved_segments if s["doc_id"]})
    answer = "".join(answer_parts).strip()

    return {
        "answer": answer,
        "tool_calls": tool_calls,
        "retrieved_doc_ids": retrieved_doc_ids,
        "retrieved_segments": retrieved_segments,
    }


# ── Evaluators ──────────────────────────────────────────────────────────────

class CorrectnessJudgment(BaseModel):
    correct: bool = Field(description="Whether the model answer captures the key facts in the reference answer")
    rationale: str = Field(description="Brief explanation, ≤30 words")


def _judge_model():
    """Bedrock Haiku judge — same model run_eval.py uses."""
    return ChatBedrockConverse(
        model_id=settings.ROUTER_MODEL_ID,
        region_name=settings.AWS_REGION,
        temperature=0,
    )


def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """LLM-judge: does the model's answer match the reference semantically?"""
    expected = reference_outputs.get("expected_answer", "")
    actual = outputs.get("answer", "")
    if not actual:
        return {"key": "correctness", "score": 0, "comment": "empty answer"}

    judge = _judge_model().with_structured_output(CorrectnessJudgment)
    result: CorrectnessJudgment = judge.invoke([
        {"role": "system", "content": (
            "Compare a model answer to a reference answer. Mark correct=True only "
            "if the model answer captures the key facts in the reference. Numeric "
            "values within 1% rounding tolerance count as correct. Extra context "
            "is fine. Missing or contradicting facts are not."
        )},
        {"role": "user", "content": (
            f"Question:\n{inputs.get('question', '')}\n\n"
            f"Reference answer:\n{expected}\n\n"
            f"Model answer:\n{actual}"
        )},
    ])
    return {
        "key": "correctness",
        "score": 1 if result.correct else 0,
        "comment": result.rationale,
    }


def retrieval_correctness_evaluator(outputs: dict, reference_outputs: dict, **_) -> dict:
    """Deterministic: fraction of expected_doc_ids that appear in the agent's
    retrieved doc_ids. Scores 1.0 if all expected docs were retrieved, 0 if
    none, partial credit between."""
    expected = reference_outputs.get("expected_doc_ids") or []
    if not expected:
        return {"key": "retrieval_correctness", "score": None, "comment": "no expected_doc_ids on this example"}
    retrieved = set(outputs.get("retrieved_doc_ids") or [])
    found = [d for d in expected if d in retrieved]
    score = len(found) / len(expected) if expected else 0.0
    missing = [d for d in expected if d not in retrieved]
    comment = (
        f"found all {len(expected)} expected docs"
        if not missing
        else f"missing {len(missing)}/{len(expected)}: {', '.join(missing[:6])}"
    )
    return {"key": "retrieval_correctness", "score": round(score, 3), "comment": comment}


# ── Experiment runner ───────────────────────────────────────────────────────

async def cmd_run(args) -> None:
    client = Client()
    # Verify dataset exists
    existing = list(client.list_datasets(dataset_name=DATASET_NAME))
    if not existing:
        print(f"Dataset {DATASET_NAME!r} not found. Run `upload` first.")
        sys.exit(1)
    ds = existing[0]

    # Apply mode env var
    if args.mode:
        os.environ["MULTI_DOC_FILTER"] = args.mode
        print(f"MULTI_DOC_FILTER = {args.mode}")

    # Optional filtering: only the stress questions (Q24-Q28)
    data: Any = DATASET_NAME
    if args.stress_only:
        # Pull just stress examples
        all_examples = list(client.list_examples(dataset_id=ds.id))
        stress_examples = [e for e in all_examples if (e.metadata or {}).get("is_stress")]
        print(f"Filtering to {len(stress_examples)} stress examples")
        data = stress_examples

    metadata = {
        "mode": args.mode or "default",
        "tag": args.tag,
        "settings_snapshot": {
            "MULTI_DOC_FILTER": os.environ.get("MULTI_DOC_FILTER", ""),
            "HISTORY_STRATEGY": os.environ.get("HISTORY_STRATEGY", ""),
            "RRF_ALPHA": os.environ.get("RRF_ALPHA", ""),
            "DEDUP_CHUNKS": os.environ.get("DEDUP_CHUNKS", ""),
            "MAX_TOOL_CALLS_PER_TURN": os.environ.get("MAX_TOOL_CALLS_PER_TURN", ""),
        },
    }

    # Visibility: print the active KB path so we don't silently run against
    # the wrong corpus (the langsmith_eval predictor doesn't enforce a KB).
    from src.infrastructure.dsrag_kb import DSRAG_STORE_DIR
    print(f"KB store: {DSRAG_STORE_DIR}")
    if "data.mi" not in str(DSRAG_STORE_DIR) and "data/dsrag_store" in str(DSRAG_STORE_DIR):
        print("  ⚠ Using default 'data/' symlink. Set DSRAG_STORE_DIR explicitly "
              "if this isn't the corpus you want.")
    print(f"Starting experiment: tag={args.tag} mode={args.mode}")
    results = await aevaluate(
        predictor,
        data=data,
        evaluators=[
            correctness_evaluator,
            retrieval_correctness_evaluator,
        ],
        experiment_prefix=args.tag,
        metadata=metadata,
        max_concurrency=int(args.concurrency),
    )
    print(f"\nExperiment complete. View at: {results}")


# ── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_up = sub.add_parser("upload", help="Upload/refresh dataset")
    p_up.add_argument("--csv", default="questions_mi_28q.csv",
                      help="CSV file relative to eval/")
    p_up.add_argument("--force", action="store_true",
                      help="Replace existing dataset's examples")
    p_up.set_defaults(func=cmd_upload)

    p_run = sub.add_parser("run", help="Run an experiment")
    p_run.add_argument("--tag", required=True, help="experiment_prefix")
    p_run.add_argument("--mode", choices=["off", "filter", "quota"],
                       help="MULTI_DOC_FILTER mode")
    p_run.add_argument("--stress-only", action="store_true",
                       help="Filter to Q24-Q28 only")
    p_run.add_argument("--concurrency", default="2",
                       help="Max parallel predictor calls")
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    if asyncio.iscoroutinefunction(args.func):
        asyncio.run(args.func(args))
    else:
        args.func(args)


if __name__ == "__main__":
    main()
