"""Run all CSV rows in a SINGLE conversation thread.

Unlike run_eval.py (one fresh session per row), this carries the full
message list across turns so the agent's state grows with each question.
Tests:
  - summarize_history firing when the running thread crosses 60K tokens
  - whether prior turns help (cross-turn context) or pollute (off-topic carryover)
  - whether wiki preload re-fires when the same slug routes twice in a session

Usage:
    cd agent_fin
    python eval/run_session_eval.py                     # questions_mi_28q.csv
    python eval/run_session_eval.py eval/other.csv

Outputs (under eval/results/session_<ts>/):
    turns.csv           # one row per turn — appended live, safe to crash
    session.json        # final state dump (full message list, base64-safe)
    summary.json        # accuracy, latency, cost, summarize-fire count
"""

import asyncio
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE.parents[1]))

# Pin MI KB as default for this eval script — matches the multi-session
# eval (langsmith_eval.py). The session-mode dataset is MI-cohort-specific;
# silently running against data.financebench would produce meaningless
# results. Set DSRAG_STORE_DIR explicitly in your shell or .env to override.
_MI_STORE = _HERE.parents[1] / "data.mi" / "dsrag_store"
if _MI_STORE.is_dir():
    os.environ.setdefault("DSRAG_STORE_DIR", str(_MI_STORE))

from langchain_aws import ChatBedrockConverse  # noqa: E402
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage  # noqa: E402
from langchain_core.messages.utils import count_tokens_approximately  # noqa: E402
from loguru import logger  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from pricing import cost_usd  # noqa: E402
from usage import UsageCollector  # noqa: E402

from src.application.orchestrator.streaming import get_streaming_events  # noqa: E402
from src.config import Settings, settings  # noqa: E402
from src.infrastructure.model import extract_text_content  # noqa: E402


EVAL_DIR = _HERE.parent
RESULTS_DIR = EVAL_DIR / "results"

# Judge aligned with eval/langsmith_eval.py:correctness_evaluator so the
# single-session result is comparable to the multi-session baseline.
# Same model (Bedrock Haiku via ROUTER_MODEL_ID), same system prompt,
# same Pydantic structured-output schema.
JUDGE_SYSTEM = (
    "Compare a model answer to a reference answer. Mark correct=True only "
    "if the model answer captures the key facts in the reference. Numeric "
    "values within 1% rounding tolerance count as correct. Extra context "
    "is fine. Missing or contradicting facts are not."
)


class CorrectnessJudgment(BaseModel):
    correct: bool = Field(
        description="Whether the model answer captures the key facts in the reference answer"
    )
    rationale: str = Field(description="Brief explanation, ≤30 words")


def judge(question: str, expected: str, actual: str, collector: UsageCollector) -> tuple[bool, str]:
    llm = ChatBedrockConverse(
        model_id=settings.ROUTER_MODEL_ID,
        region_name=settings.AWS_REGION,
        temperature=0,
    ).with_structured_output(CorrectnessJudgment)
    result: CorrectnessJudgment = llm.invoke(
        [
            ("system", JUDGE_SYSTEM),
            (
                "user",
                f"Question:\n{question}\n\n"
                f"Reference answer:\n{expected}\n\n"
                f"Model answer:\n{actual}",
            ),
        ],
        config={"callbacks": [collector]},
    )
    return result.correct, result.rationale


def _serialize_message(m: BaseMessage) -> dict:
    """Lossy but readable JSON form for archival."""
    out: dict = {"type": type(m).__name__}
    content = m.content
    out["content"] = content if isinstance(content, str) else extract_text_content(content)
    if isinstance(m, AIMessage) and m.tool_calls:
        out["tool_calls"] = [
            {"name": tc.get("name"), "args": tc.get("args"), "id": tc.get("id")}
            for tc in m.tool_calls
        ]
    if isinstance(m, ToolMessage):
        out["tool_call_id"] = m.tool_call_id
        out["name"] = m.name
    return out


async def main(csv_path: Path) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    with csv_path.open() as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{csv_path} has no rows")

    from src.infrastructure.dsrag_kb import DSRAG_STORE_DIR
    if not DSRAG_STORE_DIR.exists():
        raise SystemExit(f"KB not found at {DSRAG_STORE_DIR}.")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = RESULTS_DIR / f"session_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)
    turns_csv = run_dir / "turns.csv"
    session_json = run_dir / "session.json"
    summary_json = run_dir / "summary.json"

    collector = UsageCollector()

    def _total_cost() -> float:
        return sum(
            cost_usd(m, u.input_tokens, u.output_tokens,
                     u.cache_read_tokens, u.cache_creation_tokens)
            for m, u in collector.by_model.items()
        )

    thread_id = f"session-{ts}"

    state_messages: list[BaseMessage] = []
    fields = [
        "turn", "question", "expected", "answer", "correct", "rationale",
        "agent_seconds", "agent_cost_usd", "judge_cost_usd",
        "kb_calls_in_turn", "messages_after_turn", "tokens_after_turn",
        "summarize_fires_in_turn",
    ]
    turns_csv.write_text(",".join(fields) + "\n")

    run_start = time.perf_counter()
    results = []

    for i, row in enumerate(rows, 1):
        q = row["question"]
        expected = row["expected_answer"]
        logger.info(f"[turn {i}/{len(rows)}] {q[:120]}")

        state_messages.append(HumanMessage(content=q))

        c0 = _total_cost()
        summarize_count_before = _summarize_fires.count
        t0 = time.perf_counter()

        # Same entrypoint, customer_name, and answer-extraction logic as
        # eval/langsmith_eval.py:predictor. The ONLY single-session deltas
        # vs. multi-session are: (a) state_messages carries prior turns,
        # (b) thread_id is reused across all turns. Cost-tracking callback
        # is operational only (observer; doesn't change agent output).
        answer_parts: list[str] = []
        turn_tool_calls: list[dict] = []
        try:
            async for ev in get_streaming_events(
                messages=state_messages,
                customer_name="Evaluator",
                conversation_id=thread_id,
                callbacks=[collector],
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
                    turn_tool_calls.append({"tool": ev["tool"], "args": ev.get("args", {})})
            answer = "".join(answer_parts).strip() or "[no answer streamed]"
        except Exception as e:
            logger.exception(f"agent error on turn {i}: {e}")
            answer = f"[agent error: {type(e).__name__}: {e}]"
        state_messages.append(AIMessage(content=answer))

        agent_seconds = time.perf_counter() - t0
        c1 = _total_cost()
        kb_calls = sum(1 for tc in turn_tool_calls if tc["tool"] == "dsrag_kb")
        summarize_fires = _summarize_fires.count - summarize_count_before
        tokens_after = count_tokens_approximately(state_messages)

        try:
            correct, rationale = judge(q, expected, answer, collector)
        except Exception as e:
            correct, rationale = False, f"[judge error: {e}]"
        c2 = _total_cost()

        logger.info(
            f"  -> {'OK' if correct else 'MISS'} | {agent_seconds:.1f}s | "
            f"{kb_calls} kb calls | {len(state_messages)} msgs / {tokens_after:,} tok | "
            f"summarize fired x{summarize_fires} | {rationale}"
        )

        row_out = {
            "turn": i,
            "question": q,
            "expected": expected,
            "answer": answer,
            "correct": correct,
            "rationale": rationale,
            "agent_seconds": round(agent_seconds, 2),
            "agent_cost_usd": round(c1 - c0, 6),
            "judge_cost_usd": round(c2 - c1, 6),
            "kb_calls_in_turn": kb_calls,
            "messages_after_turn": len(state_messages),
            "tokens_after_turn": tokens_after,
            "summarize_fires_in_turn": summarize_fires,
        }
        results.append(row_out)

        # Append the row immediately so a crash mid-run doesn't lose data.
        with turns_csv.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writerow(row_out)

    run_seconds = time.perf_counter() - run_start

    # Final state dump — full message list, lossy-but-readable JSON.
    session_json.write_text(json.dumps(
        {
            "thread_id": thread_id,
            "csv": csv_path.name,
            "ts": ts,
            "run_seconds": round(run_seconds, 2),
            "messages": [_serialize_message(m) for m in state_messages],
        },
        indent=2,
        default=str,
    ))

    n_correct = sum(r["correct"] for r in results)
    accuracy = n_correct / len(results)
    total_summarize = sum(r["summarize_fires_in_turn"] for r in results)
    total_kb = sum(r["kb_calls_in_turn"] for r in results)
    total_cost = round(_total_cost(), 6)

    config_snapshot = Settings.runtime_snapshot()
    for secret in ("DEEPSEEK_API_KEY",):
        if config_snapshot.get(secret):
            config_snapshot[secret] = "<redacted>"

    summary = {
        "csv": csv_path.name,
        "ts": ts,
        "n_turns": len(results),
        "n_correct": n_correct,
        "accuracy": round(accuracy, 4),
        "run_seconds": round(run_seconds, 2),
        "total_cost_usd": total_cost,
        "total_kb_calls": total_kb,
        "total_summarize_fires": total_summarize,
        "final_messages": len(state_messages),
        "final_tokens": count_tokens_approximately(state_messages),
        "settings": config_snapshot,
    }
    summary_json.write_text(json.dumps(summary, indent=2, default=str))

    print(f"\nAccuracy:        {accuracy:.1%} ({n_correct}/{len(results)})")
    print(f"Run time:        {run_seconds:.1f}s")
    print(f"Total cost:      ${total_cost:.4f}")
    print(f"Total kb calls:  {total_kb}")
    print(f"Summarize fires: {total_summarize}")
    print(f"Final state:     {len(state_messages)} msgs / {count_tokens_approximately(state_messages):,} tokens")
    print(f"Turns CSV:       {turns_csv}")
    print(f"Session JSON:    {session_json}")
    print(f"Summary JSON:    {summary_json}")


class _SummarizeCounter:
    """Tally of how many times summarize_history's 'compressing N messages'
    log line has fired during the current run. Wired in below via loguru."""
    count = 0


_summarize_fires = _SummarizeCounter()


def _install_summarize_counter() -> None:
    """Hook a loguru sink that increments _summarize_fires.count each time
    summarize_history logs its 'compressing N messages' line. Cheaper than
    monkey-patching the function; survives if the function is reimported."""
    def _sink(message):
        record = message.record
        if record["function"] == "summarize_history" and "compressing" in record["message"]:
            _summarize_fires.count += 1

    logger.add(_sink, level="INFO")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=str(EVAL_DIR / "questions_mi_28q.csv"),
    )
    args = parser.parse_args()
    _install_summarize_counter()
    asyncio.run(main(Path(args.csv_path)))
