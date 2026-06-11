"""Multi-turn session eval — the third gate alongside the v2/28q sets.

Why this exists: the single-turn eval sets cannot catch conversational
failures, and every live bug found during beta (staging rewriter
fabrication, "figures you cited" misattribution, ack-turn context loss,
clarification punts) was multi-turn. Sessions in eval/sessions_mi_v1.json
script realistic research conversations; each turn has its own reference
answer and is judged independently.

Mechanics: each LangSmith example = one session. The predictor replays
the conversation the same way chat.py does — prior turns as
[HumanMessage, AIMessage, ...] plus the new user turn — through
streaming.get_streaming_events with a stable conversation_id. The
evaluator judges every turn with the same Bedrock Haiku judge as
langsmith_eval.py and emits:
  - turn_correctness  (fraction of turns passing)
  - session_pass      (1 iff every turn passes)

Usage (from agent_fin/):
    python eval/session_eval.py upload            # (re)create dataset
    python eval/session_eval.py run --tag <tag>   # run the gate
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

import os  # noqa: E402
os.environ.setdefault("DSRAG_STORE_DIR", str(_HERE.parent / "data.mi" / "dsrag_store"))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langsmith import Client  # noqa: E402

from eval.langsmith_eval import CorrectnessJudgment, _judge_model  # noqa: E402

DATASET_NAME = "mi_sessions_v1"
SESSIONS_PATH = _HERE / "sessions_mi_v1.json"


def cmd_upload(args) -> None:
    client = Client()
    sessions = json.loads(SESSIONS_PATH.read_text())
    examples = [
        {
            "inputs": {"turns": [t["user"] for t in s["turns"]],
                       "session_id": s["session_id"]},
            "outputs": {"expected": [t["expected"] for t in s["turns"]]},
            "metadata": {"category": s["category"]},
        }
        for s in sessions
    ]
    existing = list(client.list_datasets(dataset_name=DATASET_NAME))
    if existing:
        if not args.force:
            print(f"Dataset {DATASET_NAME!r} exists; use --force to replace.")
            return
        for ex in client.list_examples(dataset_id=existing[0].id):
            client.delete_example(ex.id)
        ds = existing[0]
    else:
        ds = client.create_dataset(
            dataset_name=DATASET_NAME,
            description=(
                "Multi-turn MI research sessions: follow-up chains, ambiguity "
                "narrowing, ack interruptions, scope pivots, shorthand, table "
                "extensions, transcript Q&A. Per-turn references; judged per turn."
            ),
        )
    client.create_examples(dataset_id=ds.id, examples=examples)
    n_turns = sum(len(s["turns"]) for s in sessions)
    print(f"Uploaded {len(examples)} sessions ({n_turns} turns) to {DATASET_NAME!r}")


async def _run_session(turns: list[str], session_id: str) -> dict:
    """Replay a scripted session through the graph, turn by turn, the
    same way chat.py replays thread history."""
    from src.application.orchestrator.streaming import get_streaming_events

    transcript: list = []
    answers: list[str] = []
    latencies: list[float] = []
    conv_id = f"sess-{session_id}-{int(time.time())}"
    for user_text in turns:
        msgs = transcript + [HumanMessage(content=user_text)]
        t0 = time.time()
        parts: list[str] = []
        async for ev in get_streaming_events(
            messages=msgs, customer_name="SessionEval", conversation_id=conv_id
        ):
            if ev.get("kind") == "answer_token":
                parts.append(ev["text"])
        answer = "".join(parts).strip()
        latencies.append(round(time.time() - t0, 1))
        answers.append(answer)
        transcript.append(HumanMessage(content=user_text))
        transcript.append(AIMessage(content=answer))
    return {"answers": answers, "latencies": latencies}


async def predictor(inputs: dict) -> dict:
    return await _run_session(inputs["turns"], inputs.get("session_id", "anon"))


def _judge_turn(question: str, expected: str, actual: str) -> tuple[bool, str]:
    if not actual:
        return False, "empty answer"
    judge = _judge_model().with_structured_output(CorrectnessJudgment)
    result: CorrectnessJudgment = judge.invoke([
        {"role": "system", "content": (
            "Compare a model answer to a reference answer for one turn of a "
            "multi-turn conversation. Mark correct=True only if the model "
            "answer captures the key facts in the reference, including any "
            "requirements the reference marks CRITICAL. Numeric values within "
            "1% rounding tolerance count as correct. Extra context is fine."
        )},
        {"role": "user", "content": (
            f"User turn:\n{question}\n\nReference:\n{expected}\n\nModel answer:\n{actual}"
        )},
    ])
    return result.correct, result.rationale


def turns_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> list[dict]:
    turns = inputs["turns"]
    expected = reference_outputs["expected"]
    answers = outputs.get("answers", [])
    results = []
    n_pass = 0
    fail_notes = []
    for i, (q, exp) in enumerate(zip(turns, expected)):
        actual = answers[i] if i < len(answers) else ""
        ok, why = _judge_turn(q, exp, actual)
        n_pass += int(ok)
        if not ok:
            fail_notes.append(f"T{i+1} '{q[:40]}': {why}")
    frac = n_pass / len(turns) if turns else 0.0
    results.append({
        "key": "turn_correctness",
        "score": round(frac, 3),
        "comment": "; ".join(fail_notes) if fail_notes else f"all {len(turns)} turns pass",
    })
    results.append({
        "key": "session_pass",
        "score": 1 if n_pass == len(turns) else 0,
        "comment": f"{n_pass}/{len(turns)} turns",
    })
    return results


async def cmd_run(args) -> None:
    from langsmith import aevaluate

    client = Client()
    results = await aevaluate(
        predictor,
        data=DATASET_NAME,
        evaluators=[turns_evaluator],
        experiment_prefix=args.tag,
        max_concurrency=int(args.concurrency),
        client=client,
    )
    print(f"\nExperiment complete. View at: <{results}>")


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    p_up = sub.add_parser("upload")
    p_up.add_argument("--force", action="store_true")
    p_run = sub.add_parser("run")
    p_run.add_argument("--tag", required=True)
    p_run.add_argument("--concurrency", default="3")
    args = p.parse_args()
    if args.cmd == "upload":
        cmd_upload(args)
    else:
        asyncio.run(cmd_run(args))


if __name__ == "__main__":
    main()
