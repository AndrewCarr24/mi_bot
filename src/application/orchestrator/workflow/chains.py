"""Chains for the router, the RAG agent, and the simple-response path."""

import json
import os
from typing import Literal, Optional

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    RemoveMessage,
    SystemMessage,
    ToolMessage,
    trim_messages,
)
from langchain_core.messages.utils import count_tokens_approximately
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from loguru import logger
from pydantic import BaseModel, Field

from src.application.orchestrator.workflow.tools import get_tools
from src.domain.prompts import (
    AGENT_SYSTEM_PROMPT,
    MULTI_DOC_FILTER_SECTION,
    ROUTER_PROMPT,
    SIMPLE_RESPONSE_PROMPT,
)
from src.infrastructure.catalog import format_for_prompt as format_catalog
from src.infrastructure.model import extract_text_content, get_model, orchestrator_is_bedrock


class RouterOutput(BaseModel):
    """Structured router classification — intent + optional wiki slug."""

    intent: Literal["rag_query", "simple", "off_topic"] = Field(
        description="Intent category for the user's latest message."
    )
    wiki_slug: Optional[str] = Field(
        default=None,
        description=(
            "Slug of the wiki page whose primary topic matches the question "
            "(e.g. 'topics/pmiers', 'companies/mtg_mgic'), or null if no "
            "single page is a primary-topic match."
        ),
    )

# Token budget for history sent to the agent LLM. Bounded by DeepSeek v4
# Flash's 128K context, with headroom for: the system prompt + filings
# catalog (~1-2K), the current turn's tool calls/results (up to ~30K
# across a multi-iteration ReAct loop), and the model's output (~2K).
# 60K leaves ~70K headroom, comfortably accommodating a long session.
HISTORY_TOKEN_BUDGET = 60_000

# Quirk: finalize_node converts every ToolMessage in the trace into a
# HumanMessage prefixed with "[Tool result for '<name>']\n..." (this is a
# workaround for Bedrock Converse, which rejects tool-use blocks unless a
# matching toolConfig is supplied — finalize calls the LLM without tools).
# As a side effect, by the time trim_history runs inside finalize_node,
# the message list contains the original user question PLUS many
# synthesized "HumanMessages" that are really tool results in disguise.
# A naive "anchor on the most-recent HumanMessage" rule would latch onto
# the last tool result, and the original user question — being older —
# could then be evicted by the trim. We avoid this by anchoring on the
# most-recent ORIGINAL human message, recognized by the absence of the
# synthesizer's `[Tool result for ` prefix.
_TOOL_RESULT_PREFIX = "[Tool result for '"


def _is_original_user_message(msg: BaseMessage) -> bool:
    """True iff `msg` is a HumanMessage produced by the user (or upstream
    runner), as opposed to one synthesized from a ToolMessage by
    finalize_node. See the comment on _TOOL_RESULT_PREFIX above."""
    if not isinstance(msg, HumanMessage):
        return False
    content = msg.content
    if isinstance(content, str):
        return not content.startswith(_TOOL_RESULT_PREFIX)
    return True


def _turn_boundaries(messages: list[BaseMessage]) -> list[int]:
    """Indices of original HumanMessages — i.e., the start of each turn.
    A turn runs from index turn_starts[i] to turn_starts[i+1] (exclusive),
    or to len(messages) for the last turn."""
    return [i for i, m in enumerate(messages) if _is_original_user_message(m)]


def _final_text_ai(
    messages: list[BaseMessage], start: int, end: int
) -> int | None:
    """Index of the last AIMessage in messages[start:end] that has no
    tool_calls and non-empty text content. None if the turn doesn't
    have one (interrupted, errored, or still in flight)."""
    for i in range(end - 1, start - 1, -1):
        m = messages[i]
        if (
            isinstance(m, AIMessage)
            and not m.tool_calls
            and m.content
            and (extract_text_content(m.content).strip() if m.content else "")
        ):
            return i
    return None


def _compact_completed_turns(messages: list[BaseMessage]) -> list[BaseMessage]:
    """Replace each completed turn's body with just [Q, final_A].

    A "completed turn" is any turn before the most recent original
    HumanMessage — its body has been distilled into a final assistant
    answer, and the intermediate AIMessage(tool_calls=...) "thinking"
    messages and ToolMessage results are no longer load-bearing for
    future turns. Compacting them away saves 10-30x tokens on
    tool-heavy threads while preserving multi-turn coherence.

    The active turn (from the last original HumanMessage onward) is
    preserved verbatim — the ReAct loop needs to see its own in-flight
    tool calls and results.

    Turns without a final-A (interrupted / errored before producing a
    text answer) are dropped. Half a turn — a question with no answer,
    or tool blocks with no answer — would only confuse the model and
    break tool_use/tool_result pairing on Bedrock.
    """
    starts = _turn_boundaries(messages)
    if not starts:
        return list(messages)

    out: list[BaseMessage] = []
    # Anything before the first turn (rare/empty in practice) is
    # passed through unchanged.
    out.extend(messages[: starts[0]])

    # Completed turns: starts[0] .. starts[-1] (exclusive of the last).
    for i in range(len(starts) - 1):
        turn_start = starts[i]
        turn_end = starts[i + 1]
        final_idx = _final_text_ai(messages, turn_start, turn_end)
        if final_idx is None:
            continue
        out.append(messages[turn_start])  # the question
        out.append(messages[final_idx])  # the final answer

    # Active turn: preserve verbatim.
    out.extend(messages[starts[-1] :])
    return out


def trim_history(messages: list[BaseMessage]) -> list[BaseMessage]:
    """Two-stage history condensation:

    Stage 1 — Compact completed turns to [Q, final_A] pairs. Drops the
    intermediate AIMessage(tool_calls=...) "thinking" messages and the
    ToolMessage results that were folded into the final answer. The
    active (in-flight) turn is preserved verbatim so the ReAct loop
    can see its own tool results.

    Stage 2 — If still over HISTORY_TOKEN_BUDGET, evict completed
    (Q, A) pairs from the head, oldest-first. Pairs are evicted whole;
    a Q without its A leaves a dangling reference, and an A without
    its Q is incoherent.

    Stage 3 — If even with no completed pairs the active turn alone
    exceeds budget, trim within the active turn (drop oldest tool
    blocks first, keeping the question).

    Why this layered design exists:
      - The single-pass trim_messages with start_on/end_on constraints
        could return [] when no human-anchored window fit budget,
        leaving the LLM with only the bare current question (no prior
        turns to resolve follow-ups against). Compaction shrinks
        completed turns 10-30x so this rarely matters; eviction handles
        the residual case cleanly.
      - The active turn is structurally pinned (never compacted, never
        evicted as a whole) so the user's current question is always
        visible to the LLM.

    Why "original" HumanMessage matters: see the _TOOL_RESULT_PREFIX
    comment above. finalize_node converts ToolMessages to HumanMessages
    for its no-tools chain; without the `_is_original_user_message`
    filter, turn boundaries would land on tool-result-disguised-as-Human
    messages and compaction would mis-segment the conversation.
    """
    compacted = _compact_completed_turns(messages)

    last_human = next(
        (
            i
            for i in range(len(compacted) - 1, -1, -1)
            if _is_original_user_message(compacted[i])
        ),
        None,
    )
    if last_human is None:
        # No original HumanMessage at all — nothing to anchor.
        return trim_messages(
            compacted,
            max_tokens=HISTORY_TOKEN_BUDGET,
            strategy="last",
            token_counter=count_tokens_approximately,
            start_on="human",
            end_on=("human", "tool"),
            allow_partial=False,
        )

    head = compacted[:last_human]
    tail = compacted[last_human:]
    tail_tokens = count_tokens_approximately(tail)

    # Stage 3: active turn alone exceeds budget. Drop all of head and
    # trim within the active turn.
    if tail_tokens >= HISTORY_TOKEN_BUDGET:
        question = tail[0]
        rest = tail[1:]
        budget = max(0, HISTORY_TOKEN_BUDGET - count_tokens_approximately([question]))
        if budget == 0 or not rest:
            return [question]
        kept_rest = trim_messages(
            rest,
            max_tokens=budget,
            strategy="last",
            token_counter=count_tokens_approximately,
            # Must start on an AIMessage(tool_calls=...) — never on a
            # bare ToolMessage, which would orphan its parent. Providers
            # reject "Tool not preceded by tool_calls".
            start_on="ai",
            end_on=("human", "tool"),
            allow_partial=False,
        )
        return [question] + kept_rest

    # Stage 2: active turn fits. After compaction, head is structured
    # as [H, A, H, A, ...] (alternating Q/A pairs from completed turns).
    # Evict oldest pairs whole until under budget.
    budget = HISTORY_TOKEN_BUDGET - tail_tokens
    while head and count_tokens_approximately(head) > budget:
        # Drop the oldest pair: from head[0] (an H) up to and including
        # the next H's predecessor. With the post-compaction shape, the
        # next H lands at index 2; the safety net handles unexpected
        # shapes (e.g. a stray turn that didn't compact cleanly).
        next_h = next(
            (i for i in range(1, len(head)) if _is_original_user_message(head[i])),
            None,
        )
        head = head[next_h:] if next_h is not None else []

    return head + tail


# ---------------------------------------------------------------------------
# Alternative history strategy: summarization
# ---------------------------------------------------------------------------
#
# When HISTORY_STRATEGY=summarize (env var), `summarize_history` replaces
# `trim_history` in agent_node and finalize_node. Behavior:
#
#   - Below HISTORY_TOKEN_BUDGET: identity (no LLM call, no rewrite).
#   - At/above HISTORY_TOKEN_BUDGET: summarize all messages after the
#     first HumanMessage. Returns:
#       (a) the condensed message list to feed the next LLM call:
#           [head, summary_msg]
#       (b) a list of state updates: RemoveMessage entries for every
#           removable message in `rest`, followed by the summary
#           message itself. The caller (agent_node / finalize_node)
#           passes these back through the messages reducer so the
#           summary actually persists in state and the original
#           tool/AI messages are removed. Without this, the summary
#           would be used for one LLM call and then discarded — the
#           next agent_node turn would re-summarize the same content
#           from scratch, compounding latency over a long ReAct loop.
#
# Bedrock note: a successful summarization eliminates AIMessage
# tool_calls and ToolMessages from the visible history, so the
# toolConfig validation Bedrock applies to those blocks no longer
# triggers. finalize_node can therefore call summarize_history directly
# on the raw state messages without first converting tool results to
# HumanMessages — the conversion is only needed in the trim path.

_SUMMARIZE_SYSTEM_PROMPT = """\
You are compressing a financial-research transcript into a structured \
summary.

The user's original question is shown below. Read the transcript that \
follows (agent reasoning, tool calls, and tool results) and produce a \
summary that distills it down to the information relevant to answering \
that question.

Use these structured headers:

## Facts retrieved
Per-entity / per-period facts that are directly relevant to the \
question, with source citations like (TICKER_FORM_PERIOD). Preserve \
all numerical figures and entity-specific values verbatim — do not \
paraphrase numbers, dates, or doc_ids. One bullet per fact.

## Tools called
List the dsrag_kb invocations already issued (question and doc_id) so \
the agent does not re-issue identical calls. One bullet per call.

## Open questions
Sub-questions or specific data points still missing that the agent \
needs to fill in to answer the original question. One bullet each. \
If no gaps remain, write "(none — sufficient to answer)".

Be terse but complete on facts. The agent will rely on this summary \
in lieu of the raw history; anything you omit is gone."""


def _serialize_messages_for_summary(messages: list[BaseMessage]) -> str:
    """Render a message list as a plain-text transcript for the summarizer.

    Tool calls and tool results are flattened into a readable form. We
    don't try to preserve LangChain message-type semantics — the
    summarizer doesn't need them.
    """
    parts: list[str] = []
    for msg in messages:
        if isinstance(msg, SystemMessage):
            text = extract_text_content(msg.content).strip()
            parts.append(f"[SYSTEM]\n{text}")
        elif isinstance(msg, HumanMessage):
            text = extract_text_content(msg.content).strip()
            parts.append(f"[USER]\n{text}")
        elif isinstance(msg, AIMessage):
            text = extract_text_content(msg.content).strip()
            block = f"[AGENT]\n{text}" if text else "[AGENT]"
            tool_calls = getattr(msg, "tool_calls", None) or []
            if tool_calls:
                tc_lines = [
                    f"  → {tc.get('name', '?')}({json.dumps(tc.get('args', {}), default=str)})"
                    for tc in tool_calls
                ]
                block += "\n" + "\n".join(tc_lines)
            parts.append(block)
        elif isinstance(msg, ToolMessage):
            name = getattr(msg, "name", "tool")
            text = extract_text_content(msg.content).strip()
            parts.append(f"[TOOL RESULT — {name}]\n{text}")
        else:
            parts.append(str(msg))
    return "\n\n".join(parts)


def _llm_summarize(messages: list[BaseMessage], question_text: str) -> str:
    """One LLM call: compress the messages into a structured summary that's
    relevant to `question_text`. Uses the orchestrator model at T=0 for
    determinism."""
    transcript = _serialize_messages_for_summary(messages)
    model = get_model(temperature=0.0)
    prompt_messages = [
        SystemMessage(content=_SUMMARIZE_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"<question>\n{question_text}\n</question>\n\n"
            f"<transcript>\n{transcript}\n</transcript>"
        )),
    ]
    response = model.invoke(prompt_messages)
    return extract_text_content(response.content).strip()


def summarize_history(
    messages: list[BaseMessage],
    question_text: str,
) -> tuple[list[BaseMessage], list[BaseMessage]]:
    """Returns (condensed_messages, state_updates).

    If `messages` is under HISTORY_TOKEN_BUDGET, both elements are
    no-ops: condensed_messages == messages, state_updates == [].

    If over budget, summarize all messages after the first
    HumanMessage into one SystemMessage and return:

      condensed_messages = [head, summary_msg]   ← for the next LLM
                                                   call
      state_updates      = [RemoveMessage(id=…) for each msg in rest
                            that has an id,  + summary_msg]
                                                 ← for the caller to
                                                   return through the
                                                   messages reducer so
                                                   state actually
                                                   shrinks

    Without `state_updates` being applied, the summary lasts only one
    LLM call — the next agent turn would see the full uncompressed
    history again and have to re-summarize from scratch.

    The first HumanMessage (user's original question) is always
    preserved.
    """
    if count_tokens_approximately(messages) < HISTORY_TOKEN_BUDGET:
        return messages, []

    first_human_idx = next(
        (i for i, m in enumerate(messages) if isinstance(m, HumanMessage)),
        None,
    )
    if first_human_idx is None:
        # No user question to anchor on — fall through to the legacy
        # trim. Should be unreachable in normal flow.
        logger.warning(
            "summarize_history: no HumanMessage found; falling back to trim_history"
        )
        return trim_history(messages), []

    head = messages[:first_human_idx + 1]   # SystemPrompt(s) + original question
    rest = messages[first_human_idx + 1:]
    if not rest:
        return messages, []

    logger.info(
        f"summarize_history: compressing {len(rest)} messages "
        f"(~{count_tokens_approximately(rest):,} tokens) to a single summary"
    )
    summary_text = _llm_summarize(rest, question_text)
    summary_msg = SystemMessage(
        content=f"<prior_research_summary>\n{summary_text}\n</prior_research_summary>"
    )

    # Build the state-update list. Removing a message requires its id;
    # if any rest-message lacks an id (rare — LangGraph auto-assigns,
    # but our synthetic wiki_preload_node AIMessage is one we
    # construct manually), it stays in state and the next summarize
    # round will re-include it.
    removals: list[BaseMessage] = []
    skipped_no_id = 0
    for m in rest:
        msg_id = getattr(m, "id", None)
        if msg_id:
            removals.append(RemoveMessage(id=msg_id))
        else:
            skipped_no_id += 1
    if skipped_no_id:
        logger.warning(
            f"summarize_history: {skipped_no_id}/{len(rest)} messages had "
            f"no id and could not be removed from state — they will appear "
            f"in the next summarization input."
        )

    state_updates = removals + [summary_msg]
    condensed_messages = head + [summary_msg]

    logger.info(
        f"summarize_history: produced summary "
        f"(~{count_tokens_approximately([summary_msg]):,} tokens) — "
        f"will remove {len(removals)} messages from state"
    )
    return condensed_messages, state_updates


def _escape_braces(text: str) -> str:
    return text.replace("{", "{{").replace("}", "}}")


def _cached_system(text: str) -> SystemMessage:
    """Build the agent's system message.

    On Bedrock we append a cachePoint content block so Converse caches the
    prefix across ReAct turns. On OpenAI-compatible providers (DeepSeek)
    that content-block shape is unknown, so we emit a plain SystemMessage
    and rely on the provider's own prefix caching if any.
    """
    if not orchestrator_is_bedrock():
        return SystemMessage(content=text)
    return SystemMessage(
        content=[
            {"type": "text", "text": text},
            {"cachePoint": {"type": "default"}},
        ]
    )


def with_cache_on_last(messages: list[BaseMessage]) -> list[BaseMessage]:
    """Append a Bedrock cachePoint to the content of the last message.

    On each ReAct turn, the agent node calls the LLM with a growing list
    of messages. By marking the end of the current history as a cache
    point, Bedrock caches the prefix; the next turn reads the same prefix
    at ~10% of input-token price.

    No-op for non-Bedrock orchestrators — DeepSeek applies prefix caching
    server-side with no client-side markers required.
    """
    if not orchestrator_is_bedrock():
        return messages
    if not messages:
        return messages
    last = messages[-1]
    content = last.content
    cp_block = {"cachePoint": {"type": "default"}}
    if isinstance(content, str):
        new_content = [{"type": "text", "text": content}, cp_block]
    elif isinstance(content, list):
        if any(isinstance(b, dict) and "cachePoint" in b for b in content):
            return messages
        new_content = list(content) + [cp_block]
    else:
        return messages
    new_last = last.model_copy(update={"content": new_content})
    return list(messages[:-1]) + [new_last]


def _multi_doc_mode() -> str:
    """Read MULTI_DOC_FILTER fresh per call. Returns 'off' | 'filter' | 'quota'.
    Tolerates legacy 'true'/'false' values (true → filter)."""
    raw = os.environ.get("MULTI_DOC_FILTER", "off").strip().lower()
    if raw in ("true", "1"):
        return "filter"
    if raw in ("filter", "quota"):
        return raw
    return "off"


def _build_agent_system(customer_name: str) -> str:
    # MULTI_DOC_FILTER mode read fresh per call so the same Python process
    # can serve different arms of an A/B/C comparison without restart.
    mode = _multi_doc_mode()
    multi_doc_section = MULTI_DOC_FILTER_SECTION if mode in ("filter", "quota") else ""
    return (
        AGENT_SYSTEM_PROMPT
        .replace("{customer_name}", customer_name)
        .replace("{filings_catalog}", format_catalog())
        .replace("{multi_doc_filter_section}", multi_doc_section)
    )


def get_agent_chain(customer_name: str = "Guest") -> Runnable:
    model = get_model(temperature=0.35).bind_tools(get_tools())
    system = _build_agent_system(customer_name)
    prompt = ChatPromptTemplate.from_messages(
        [_cached_system(system), MessagesPlaceholder(variable_name="messages")]
    )
    return prompt | model


def get_finalize_chain(customer_name: str = "Guest") -> Runnable:
    """Agent chain WITHOUT tools bound — used to force a text answer
    when the ReAct tool-call budget is exhausted."""
    model = get_model(temperature=0.35)
    system = _build_agent_system(customer_name) + (
        "\n\nYou have already gathered research via tool calls and your tool "
        "budget is now exhausted. Do NOT attempt any more tool calls. Produce "
        "the best final answer you can from the tool results already in the "
        "conversation history. If the information is insufficient, say so "
        "clearly and explain what is missing."
    )
    prompt = ChatPromptTemplate.from_messages(
        [_cached_system(system), MessagesPlaceholder(variable_name="messages")]
    )
    return prompt | model


def get_router_chain() -> Runnable:
    """Router classifier chain.

    Returns a `RouterOutput` (intent + wiki_slug). Uses LangChain's
    `with_structured_output` which routes through Bedrock Converse's
    tool-use machinery — same model call as before, just with a
    schema enforced on the response.

    The router prompt contains JSON examples with curly braces, which
    ChatPromptTemplate's tuple-form would parse as template variables.
    We pass a SystemMessage directly to skip that templating.
    """
    model = get_model(temperature=0.0, router=True).with_structured_output(
        RouterOutput
    )
    prompt = ChatPromptTemplate.from_messages(
        [SystemMessage(content=ROUTER_PROMPT), MessagesPlaceholder(variable_name="messages")]
    )
    return prompt | model


def get_simple_response_chain(customer_name: str = "Guest") -> Runnable:
    model = get_model(temperature=0.7)
    system = SIMPLE_RESPONSE_PROMPT.replace(
        "{customer_name}", _escape_braces(customer_name)
    )
    prompt = ChatPromptTemplate.from_messages(
        [("system", system), MessagesPlaceholder(variable_name="messages")]
    )
    return prompt | model
