"""Diagnostic harness — runs each failing question and captures everything:
router output, tool calls + args, full retrieved chunks, agent reasoning
between tool calls, and the final answer. Output goes to a single
human-readable trace file per question.

Usage:
    .venv/bin/python eval/diagnose_failed4.py
"""

from __future__ import annotations

import asyncio
import csv
import json
import os
import sys
import time
from pathlib import Path

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from loguru import logger

# Ensure repo root is on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.application.orchestrator.workflow.graph import create_graph  # noqa: E402
from src.infrastructure.model import extract_text_content  # noqa: E402


QUESTIONS_CSV = ROOT / "eval" / "questions_mi_failed4.csv"
OUT_DIR = ROOT / "eval" / "diagnostics"


def _strip_aimsg_reasoning(msg) -> str:
    """Pull DeepSeek's reasoning_content out of an AIMessage if present."""
    extra = getattr(msg, "additional_kwargs", None) or {}
    return (extra.get("reasoning_content") or "").strip()


async def diagnose_one(question: str, expected: str, qidx: int) -> dict:
    """Run a single question and capture a full event trace."""
    graph = create_graph()
    thread_id = f"diag-{qidx}-{int(time.time())}"

    config = {
        "configurable": {
            "thread_id": thread_id,
            "customer_name": "Diagnostic",
            "actor_id": "user:diagnostic",
        },
        "recursion_limit": 55,
    }
    input_data = {
        "messages": [HumanMessage(content=question)],
        "customer_name": "Diagnostic",
        "tool_call_count": 0,
    }

    trace: dict = {
        "question_idx": qidx,
        "question": question,
        "expected": expected,
        "router": None,
        "events": [],  # Ordered list of {type, ...} entries
        "final_answer": "",
        "wall_seconds": 0.0,
    }
    start = time.time()
    streamed_text: list[str] = []
    final_state = None

    async for event in graph.astream_events(
        input=input_data, config=config, version="v2"
    ):
        et = event.get("event")
        name = event.get("name", "")
        data = event.get("data", {})

        if et == "on_chain_end" and name == "router_node":
            output = data.get("output") or {}
            trace["router"] = {
                "intent": output.get("intent"),
                "wiki_slug": output.get("wiki_slug"),
                "cohort_query": output.get("cohort_query"),
            }
            trace["events"].append({"type": "router", **trace["router"]})

        elif et == "on_chain_end" and name in (
            "wiki_preload_node", "cohort_preload_node",
        ):
            output = data.get("output") or {}
            messages = output.get("messages") or []
            preload_calls = []
            preload_results = []
            for m in messages:
                if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
                    for tc in m.tool_calls:
                        preload_calls.append({
                            "tool": tc.get("name"),
                            "args": tc.get("args", {}),
                            "id": tc.get("id"),
                        })
                elif isinstance(m, ToolMessage):
                    preload_results.append({
                        "tool_call_id": m.tool_call_id,
                        "tool": m.name,
                        "content": str(m.content),
                    })
            trace["events"].append({
                "type": "preload",
                "node": name,
                "calls": preload_calls,
                "results": preload_results,
            })

        elif et == "on_chain_end" and name == "agent_node":
            # Each agent_node invocation: capture the AI message it
            # produced. This is where reasoning lives.
            output = data.get("output") or {}
            messages = output.get("messages") or []
            for m in messages:
                if isinstance(m, AIMessage):
                    entry = {
                        "type": "agent_response",
                        "reasoning": _strip_aimsg_reasoning(m),
                        "content_text": extract_text_content(m.content) or "",
                        "tool_calls": [],
                    }
                    for tc in (getattr(m, "tool_calls", None) or []):
                        entry["tool_calls"].append({
                            "tool": tc.get("name"),
                            "args": tc.get("args", {}),
                            "id": tc.get("id"),
                        })
                    trace["events"].append(entry)

        elif et == "on_tool_end" and name == "dsrag_kb":
            # Capture full content (chunks) returned by dsrag_kb.
            output = data.get("output")
            if hasattr(output, "content"):
                raw = output.content
            else:
                raw = output
            try:
                parsed = json.loads(raw) if isinstance(raw, str) else raw
            except Exception:
                parsed = raw
            inp = data.get("input") or {}
            trace["events"].append({
                "type": "tool_result",
                "tool": "dsrag_kb",
                "args": {
                    "question": inp.get("question"),
                    "doc_id": inp.get("doc_id"),
                },
                "segments": (
                    parsed if isinstance(parsed, list) else
                    [{"raw": str(parsed)[:2000]}]
                ),
            })

        elif et == "on_tool_end" and name == "wiki_read_page":
            output = data.get("output")
            content = output.content if hasattr(output, "content") else output
            inp = data.get("input") or {}
            trace["events"].append({
                "type": "tool_result",
                "tool": "wiki_read_page",
                "args": inp,
                "content": str(content)[:5000] + ("..." if len(str(content)) > 5000 else ""),
            })

        elif et == "on_chain_end" and name == "finalize_node":
            output = data.get("output") or {}
            messages = output.get("messages") or []
            for m in messages:
                if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None):
                    trace["events"].append({
                        "type": "finalize",
                        "content_text": extract_text_content(m.content) or "",
                    })

        elif et == "on_chain_end" and name == "LangGraph":
            output = data.get("output") or {}
            if isinstance(output, dict):
                final_state = output

    trace["wall_seconds"] = round(time.time() - start, 2)

    # Pull final answer from state
    if final_state and "messages" in final_state:
        for m in reversed(final_state["messages"]):
            if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None):
                text = extract_text_content(m.content)
                if text:
                    trace["final_answer"] = text
                    break

    return trace


def render_trace(trace: dict) -> str:
    """Format a trace as readable plaintext."""
    lines = []
    lines.append("=" * 100)
    lines.append(f"Q{trace['question_idx']}: {trace['question']}")
    lines.append("-" * 100)
    lines.append(f"EXPECTED:")
    lines.append(trace['expected'])
    lines.append(f"\nWall time: {trace['wall_seconds']}s")
    lines.append("")

    # Router
    r = trace["router"] or {}
    lines.append("[ROUTER]")
    lines.append(
        f"  intent={r.get('intent')!r} "
        f"wiki_slug={r.get('wiki_slug')!r} "
        f"cohort_query={r.get('cohort_query')!r}"
    )
    lines.append("")

    for i, ev in enumerate(trace["events"]):
        t = ev.get("type")
        if t == "router":
            continue  # already rendered above
        if t == "preload":
            lines.append(f"[PRELOAD via {ev['node']}] — {len(ev['calls'])} calls")
            for c in ev["calls"]:
                lines.append(f"  → {c['tool']}({c['args']})")
            lines.append(f"  ({len(ev['results'])} results, {sum(len(r['content']) for r in ev['results'])} total chars)")
            lines.append("")
            continue
        if t == "agent_response":
            lines.append(f"[AGENT_RESPONSE]")
            if ev.get("reasoning"):
                lines.append(f"  REASONING ({len(ev['reasoning'])} chars):")
                # Indent reasoning
                for line in ev["reasoning"].splitlines():
                    lines.append(f"    | {line}")
            if ev.get("content_text"):
                lines.append(f"  CONTENT_TEXT ({len(ev['content_text'])} chars):")
                for line in ev["content_text"].splitlines():
                    lines.append(f"    > {line}")
            if ev.get("tool_calls"):
                lines.append(f"  TOOL_CALLS:")
                for tc in ev["tool_calls"]:
                    lines.append(f"    → {tc['tool']}({tc['args']})")
            lines.append("")
            continue
        if t == "tool_result":
            tool = ev["tool"]
            lines.append(f"[TOOL_RESULT {tool}]")
            lines.append(f"  args={ev.get('args')}")
            if tool == "dsrag_kb":
                segs = ev.get("segments") or []
                lines.append(f"  → returned {len(segs)} segments")
                for j, seg in enumerate(segs):
                    if isinstance(seg, dict):
                        sc = seg.get("score")
                        did = seg.get("doc_id", "?")
                        cont = seg.get("content") or seg.get("raw") or ""
                        lines.append(f"  --- segment {j}: doc_id={did} score={sc} len={len(cont)} ---")
                        # Print chunk content (truncated)
                        chunk = cont[:1800]
                        for line in chunk.splitlines():
                            lines.append(f"    : {line}")
                        if len(cont) > 1800:
                            lines.append(f"    ... [truncated, {len(cont)-1800} more chars]")
            else:
                content = ev.get("content", "")
                lines.append(f"  content ({len(content)} chars):")
                for line in content[:1500].splitlines()[:30]:
                    lines.append(f"    : {line}")
            lines.append("")
            continue
        if t == "finalize":
            lines.append(f"[FINALIZE_NODE — fallback after tool-call cap]")
            for line in (ev.get("content_text") or "").splitlines():
                lines.append(f"    > {line}")
            lines.append("")
            continue

    lines.append("=" * 100)
    lines.append("[FINAL ANSWER]")
    lines.append(trace["final_answer"])
    lines.append("=" * 100)
    return "\n".join(lines)


async def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(QUESTIONS_CSV)))
    logger.info(f"Diagnosing {len(rows)} questions from {QUESTIONS_CSV.name}")

    for i, row in enumerate(rows, 1):
        question = row["question"]
        expected = row.get("expected_answer") or row.get("expected") or ""
        logger.info(f"[{i}/{len(rows)}] {question[:80]}")
        try:
            trace = await diagnose_one(question, expected, i)
        except Exception as e:
            logger.exception(f"Failed: {e}")
            continue

        out_path = OUT_DIR / f"q{i}_trace.txt"
        out_path.write_text(render_trace(trace))
        logger.info(f"  saved {out_path} ({trace['wall_seconds']}s)")

        json_path = OUT_DIR / f"q{i}_trace.json"
        json_path.write_text(json.dumps(trace, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
