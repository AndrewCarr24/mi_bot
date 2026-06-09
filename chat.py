"""Chainlit chat handler — pipes user messages into the LangGraph agent.

Mounted into the FastAPI app at /chat by api.py via
`chainlit.utils.mount_chainlit`. The Chainlit session id is used as the
LangGraph `conversation_id`, so each browser session retains its own
multi-turn history via the in-process MemorySaver checkpointer.

For rag_query intents we surface intermediate reasoning + tool-call
summaries into a collapsible cl.Step that's rendered above the answer
(via Chainlit's `async with` + thread-local step stack). For simple /
off_topic intents the agent never invokes a tool, so we skip the step
entirely — keeps chatty replies clean.

The intent is determined upfront by listening for the `intent` event
emitted by `streaming.get_streaming_events` after `router_node` finishes
classifying. That event always lands first in the stream (router runs
before any downstream node), so the step decision is made before any
answer tokens flow.
"""

from __future__ import annotations

import os
import re
import sys
import time
import tracemalloc
from http.cookies import SimpleCookie
from pathlib import Path

import chainlit as cl
import chainlit.data as cl_data
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from loguru import logger


# ── tracemalloc instrumentation ───────────────────────────────────────────
# Snapshot before/after each on_message handler so we can see which Python
# allocations grow during a turn. Enabled when TRACEMALLOC=true in env;
# disabled by default to avoid the ~10-30% memory overhead in production.
_TRACEMALLOC_ENABLED = os.environ.get("TRACEMALLOC", "").lower() == "true"
_TURN_COUNTER = 0
if _TRACEMALLOC_ENABLED:
    tracemalloc.start(10)
    logger.info("tracemalloc enabled — per-turn heap-delta logging is on")


def _log_tracemalloc_diff(snap_before, snap_after, turn_id: str) -> None:
    """Compare two tracemalloc snapshots and log the largest growers.

    Skips entries smaller than 50 KB so the output stays focused on the
    real hogs. Negative deltas (frees) are included so we can spot
    objects that grew earlier and got released this turn."""
    diff = snap_after.compare_to(snap_before, "lineno")
    total_growth_kb = sum(s.size_diff for s in diff) / 1024
    logger.info(
        f"tracemalloc[turn={turn_id}]: total heap Δ = {total_growth_kb:+.0f} KB "
        f"({total_growth_kb / 1024:+.2f} MB)"
    )
    sorted_diff = sorted(diff, key=lambda s: abs(s.size_diff), reverse=True)
    n_shown = 0
    for stat in sorted_diff:
        kb = stat.size_diff / 1024
        if abs(kb) < 50:
            break  # rest are < 50 KB, not interesting
        frames = stat.traceback.format() if stat.traceback else []
        loc = frames[-1].strip() if frames else "<unknown>"
        if len(loc) > 120:
            loc = loc[:117] + "..."
        logger.info(f"  Δ {kb:+8.0f} KB  count {stat.count_diff:+7d}  {loc}")
        n_shown += 1
        if n_shown >= 15:
            break
    if n_shown == 0:
        logger.info("  (no allocations >= 50 KB delta — turn was quiet)")


# Chainlit may exec this file from a different cwd than api.py — ensure
# the agent_fin root is importable either way.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.application.orchestrator.streaming import get_streaming_events  # noqa: E402
from src.data_layer import get_data_layer  # noqa: E402


def _get_data_layer_instance():
    """Indirection so tests can monkey-patch the data layer used by
    `_fetch_thread_messages` without touching the @cl.data_layer
    registration. Production callers go through chainlit.data._data_layer."""
    return cl_data._data_layer  # the layer registered by @cl_data.data_layer


async def _fetch_thread_messages(thread_id: str) -> list[BaseMessage]:
    """Read prior steps for the given thread and convert them into
    LangChain messages, ordered chronologically. Returns [] if the
    thread doesn't exist or has no messages.
    """
    layer = _get_data_layer_instance()
    if layer is None:
        logger.warning(
            "_fetch_thread_messages: no data layer registered; "
            "skipping replay for thread_id={}",
            thread_id,
        )
        return []
    try:
        thread = await layer.get_thread(thread_id)
    except Exception as e:
        logger.warning(
            "_fetch_thread_messages: get_thread failed for thread_id={}: {!r}",
            thread_id, e,
        )
        return []
    if not thread:
        return []

    steps = sorted(
        thread.get("steps", []) or [],
        key=lambda s: s.get("createdAt") or "",
    )

    out: list[BaseMessage] = []
    for step in steps:
        step_type = step.get("type", "")
        text = step.get("output") or step.get("input") or ""
        if not text:
            continue
        if step_type == "user_message":
            out.append(HumanMessage(content=text))
        elif step_type == "assistant_message":
            out.append(AIMessage(content=text))
        # Other step types (tool calls, etc.) are intermediate Chainlit
        # bookkeeping — skip them. The agent reconstructs tool context
        # from scratch each turn via wiki_preload + dsrag_kb.
    return out


@cl.data_layer
def _data_layer():
    """Tell Chainlit which BaseDataLayer to use for thread persistence.
    Backend chosen by DATA_LAYER_BACKEND env (sqlite locally, dynamodb in prod).
    """
    return get_data_layer()


@cl.header_auth_callback
def header_auth_callback(headers: dict) -> cl.User | None:
    """Map the agent_browser_id cookie to a cl.User identifier.

    Chainlit fires this on every HTTP and WebSocket request. The user_id
    we return is what Chainlit uses to scope threads in the data layer.
    Per Decision 1 in the spec, identity = the agent_browser_id cookie
    value (a UUID4 set by BrowserIdMiddleware on first visit).
    """
    cookie_str = headers.get("cookie") or headers.get("Cookie") or ""
    jar = SimpleCookie()
    try:
        jar.load(cookie_str)
    except Exception:
        return None
    bid = jar.get("agent_browser_id")
    if bid is None:
        # BrowserIdMiddleware should have set this on first request, but
        # if we somehow get here without it (e.g., a request that bypassed
        # middleware), fall back to anonymous — Chainlit will treat as a
        # fresh browser for this connection only, no persistence.
        return None
    return cl.User(identifier=bid.value)


@cl.on_chat_resume
async def on_chat_resume(thread):
    """Fired when a user re-opens a previous thread from the left pane.

    Empty body is sufficient — registering the hook tells Chainlit's
    frontend that thread continuation is supported, which enables the
    message composer in thread-view URLs (without it Chainlit shows
    the thread as read-only history). Our existing on_message handler
    handles agent context replay on every turn via
    _fetch_thread_messages, so no special resume logic is needed here.
    """
    return None


# NOTE: Chainlit starters (cl.set_starters) are mutually exclusive with
# sending a message in on_chat_start — the starter screen is replaced as
# soon as the welcome message lands (verified empirically on 2.11). We
# chose the rich welcome message: it carries the coverage dates and
# scope limits that clickable starter chips can't.
@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content=(
            "**Welcome — I'm a research assistant for the U.S. private mortgage "
            "insurance industry.**\n\n"
            "I answer questions from the SEC filings and earnings calls of the six "
            "public MIs — **Arch Capital (ACGL), Enact (ACT), Essent (ESNT), "
            "MGIC (MTG), NMI Holdings (NMIH), and Radian (RDN)** — plus industry "
            "references (PMIERs, FHFA reports, USMI papers).\n\n"
            "**Coverage:** 10-Ks FY2022-2025 · 10-Qs and earnings 8-Ks Q1 2022 → Q1 2026 · "
            "earnings call transcripts Q4 2022 → Q1 2026 (Radian back to Q1 2022).\n\n"
            "**Things you can ask:**\n"
            "- 📊 *Metric lookups* — \"What was NMI's PMIERs sufficiency ratio at year-end 2025?\"\n"
            "- ⚖️ *Cohort comparisons* — \"Compare NIW across all six MIs for 2024.\"\n"
            "- 📈 *Trends* — \"How did Enact's persistency evolve from 2022 to 2025?\"\n"
            "- 🎙️ *Call commentary* — \"What did MGIC say about cure rates last quarter?\"\n"
            "- 📖 *Concepts* — \"Why are MI loss ratios sometimes negative?\"\n\n"
            "Every answer cites the underlying filings. I only cover these six "
            "companies and this industry — other tickers are out of scope."
        )
    ).send()


def _format_tool_call(tool: str, args: dict) -> str:
    """One-line summary of a tool invocation for display in the step."""
    if tool == "dsrag_kb":
        question = (args.get("question") or "").strip()
        doc_id = args.get("doc_id")
        if doc_id:
            return f"🔍 Searching {doc_id} for: {question!r}"
        return f"🔍 Searching all filings for: {question!r}"
    if tool == "wiki_read_page":
        slug = (args.get("slug") or "").strip()
        return f"📖 Reading wiki page: {slug}"
    if tool == "memory_retrieval_tool":
        query = (args.get("query") or "").strip()
        return f"🧠 Recalling memory: {query!r}"
    # Fallback for any future tools
    arg_str = ", ".join(f"{k}={v!r}" for k, v in args.items()) or "(no args)"
    return f"🔧 {tool}({arg_str})"


# Step name shown when a tool of a given kind fires. Set on the FIRST
# tool_call event of a turn — subsequent tool calls don't rename the step.
_STEP_NAME_BY_TOOL = {
    "dsrag_kb": "MI Knowledge Base Tool",
    "wiki_read_page": "Wiki Tool",
    "memory_retrieval_tool": "Memory Tool",
}


@cl.on_message
async def on_message(message: cl.Message):
    """Stream the agent's response.

    Two paths:
      - rag_query → wrap in `async with cl.Step(...)` so the step
        renders above the answer; rename the step on the first tool_call
        to reflect the actual tool used (KB vs wiki vs memory).
      - simple / off_topic → no step at all, just stream the answer.

    The intent event is read off the front of the stream before any
    answer tokens flow, so the branching decision is made up-front.
    """
    global _TURN_COUNTER
    _TURN_COUNTER += 1
    turn_id = f"{_TURN_COUNTER:03d}"
    snap_before = tracemalloc.take_snapshot() if _TRACEMALLOC_ENABLED else None
    t_turn_start = time.perf_counter()

    try:
        session_id = cl.context.session.id
        thread_id = getattr(cl.context.session, "thread_id", None) or session_id

        # Replay prior messages on this thread from the data layer so the
        # stateless agent has full context.
        prior = await _fetch_thread_messages(thread_id)
        full_messages = prior + [HumanMessage(content=message.content)]

        events = get_streaming_events(
            messages=full_messages,
            customer_name="User",
            conversation_id=thread_id,
        )

        # Read events until we see the intent event (always first under
        # normal operation — router_node ends before any downstream node
        # starts streaming). Buffer anything that comes before it just in
        # case, though we don't expect that to happen.
        intent = "rag_query"  # safe default if router somehow doesn't emit
        buffered: list[dict] = []
        async for event in events:
            if event.get("kind") == "intent":
                intent = event.get("intent", "rag_query")
                break
            buffered.append(event)

        if intent == "rag_query":
            await _handle_rag_query(events, buffered)
        else:
            await _handle_simple(events, buffered)
    finally:
        if _TRACEMALLOC_ENABLED and snap_before is not None:
            elapsed = time.perf_counter() - t_turn_start
            logger.info(f"tracemalloc[turn={turn_id}]: turn took {elapsed:.1f}s")
            snap_after = tracemalloc.take_snapshot()
            _log_tracemalloc_diff(snap_before, snap_after, turn_id)


async def _handle_rag_query(events, buffered: list[dict]):
    """Stream a rag_query response with a Working step rendered above the answer.

    `events` is a partially-consumed async generator (the intent event
    was already read by the caller). `buffered` holds any pre-intent
    events we accidentally received before intent landed.
    """
    answer: cl.Message | None = None

    # Track unique doc_ids the agent retrieved from, in first-seen order,
    # so we can list them under the answer as plain text.
    source_doc_ids: list[str] = []
    seen_doc_ids: set[str] = set()

    # Has any tool fired this turn? Drives the step rename.
    tool_used = False

    async with cl.Step(
        name="Working...",
        default_open=True,
        show_input=False,
        icon="search",
    ) as step:
        try:
            # Drain anything we buffered before the intent event, then
            # continue with the rest of the stream.
            for event in buffered:
                answer = await _process_event(event, step, answer, source_doc_ids, seen_doc_ids)
            async for event in events:
                kind = event.get("kind")
                if kind == "tool_call" and not tool_used:
                    # First tool of the turn — rename from "Working..."
                    # to the tool-specific label.
                    step.name = _STEP_NAME_BY_TOOL.get(
                        event["tool"], event["tool"]
                    )
                    tool_used = True
                answer = await _process_event(event, step, answer, source_doc_ids, seen_doc_ids)

        except Exception as e:
            if answer is None:
                answer = cl.Message(content="")
                await answer.send()
            await answer.stream_token(f"\n\n[error: {type(e).__name__}: {e}]")

    # Append the unique doc_ids the agent searched from as a plain-text
    # source line under the answer — but ONLY if the agent didn't
    # already write its own Sources/Source section. (Detection: a line
    # starting with "Source:" or "Sources:", optionally bolded. Avoids
    # matching inline parenthetical citations like "(MTG_10-Q_...)".)
    if answer is not None and source_doc_ids:
        content = answer.content or ""
        agent_wrote_sources = bool(
            re.search(r"(?im)^\s*\*{0,2}\s*sources?\s*\*{0,2}\s*[:—\-]", content)
        )
        if not agent_wrote_sources:
            answer.content = content + "\n\nSource: " + ", ".join(source_doc_ids)

    if answer is not None:
        await answer.update()


async def _handle_simple(events, buffered: list[dict]):
    """Stream a simple / off_topic response with no step.

    The agent's response goes straight into a `cl.Message`, no working
    box, no tool summaries, no source list (simple replies don't pull
    from the KB).
    """
    answer: cl.Message | None = None
    try:
        for event in buffered:
            answer = await _process_simple_event(event, answer)
        async for event in events:
            answer = await _process_simple_event(event, answer)
    except Exception as e:
        if answer is None:
            answer = cl.Message(content="")
            await answer.send()
        await answer.stream_token(f"\n\n[error: {type(e).__name__}: {e}]")

    if answer is not None:
        await answer.update()


async def _process_event(
    event: dict,
    step: cl.Step,
    answer: cl.Message | None,
    source_doc_ids: list[str],
    seen_doc_ids: set[str],
) -> cl.Message | None:
    """Process one streaming event in the rag_query path. Returns the
    (possibly newly-created) answer message so the caller can keep its
    reference."""
    kind = event.get("kind")

    if kind == "answer_token":
        if answer is None:
            answer = cl.Message(content="")
            await answer.send()
        await answer.stream_token(event["text"])

    elif kind == "rewind_to_thinking":
        rewound = event["text"]
        if answer and answer.content.endswith(rewound):
            answer.content = answer.content[: -len(rewound)]
            await answer.update()
        step.output = (step.output or "") + rewound + "\n\n"
        await step.update()

    elif kind == "tool_call":
        summary = _format_tool_call(event["tool"], event.get("args", {}))
        step.output = (step.output or "") + summary + "\n\n"
        await step.update()

    elif kind == "tool_result_segment":
        doc_id = event.get("doc_id", "")
        if doc_id and doc_id not in seen_doc_ids:
            seen_doc_ids.add(doc_id)
            source_doc_ids.append(doc_id)

    # intent events are consumed in on_message before we get here; no-op
    # if one slips through.

    return answer


async def _process_simple_event(event: dict, answer: cl.Message | None) -> cl.Message | None:
    """Process one streaming event in the simple-intent path. Only
    answer_tokens matter — simple replies don't have tool calls or
    rewinds."""
    if event.get("kind") == "answer_token":
        if answer is None:
            answer = cl.Message(content="")
            await answer.send()
        await answer.stream_token(event["text"])
    return answer
