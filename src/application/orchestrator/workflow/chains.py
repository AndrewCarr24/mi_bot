"""Chains for the router, the RAG agent, and the simple-response path."""

import json
import re
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
        # Pick start_on based on what's actually in `rest`:
        #   - If any AIMessage is present (normal mid-ReAct state), use
        #     start_on="ai" to never orphan a ToolMessage from its parent
        #     AIMessage(tool_calls). Providers reject that shape.
        #   - If `rest` is all Humans (the post-conversion state inside
        #     finalize_node, where _convert_tool_messages_to_human has
        #     already stripped every AIMessage(tool_calls) and replaced
        #     each ToolMessage with a synthesized HumanMessage carrying
        #     "[Tool result for ...]"), use start_on="human". Otherwise
        #     trim_messages returns [] and finalize loses every tool
        #     result the agent retrieved before the cap fired.
        has_ai = any(isinstance(m, AIMessage) for m in rest)
        start_on = "ai" if has_ai else "human"
        kept_rest = trim_messages(
            rest,
            max_tokens=budget,
            strategy="last",
            token_counter=count_tokens_approximately,
            start_on=start_on,
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
You are compressing a financial-research transcript into an internal \
research-state note. The agent will read this note (as part of its \
context) to continue working on the question; the note is NEVER \
shown to the user verbatim.

The user's original question is shown below. Read the transcript that \
follows (agent reasoning, tool calls, and tool results) and produce a \
note with three short paragraphs in this order — no markdown headers, \
no bullet lists, no section titles. Just prose, terse and dense.

First paragraph — facts retrieved so far that are relevant to the \
question. Preserve all numerical figures, dates, and doc_ids verbatim. \
Cite each fact inline like "MGIC FY2024 NIW = $55.7B (MTG_10-K_2024-12-31)". \
Pack facts as a single dense paragraph, separated by semicolons.

Second paragraph — dsrag_kb invocations already issued (question + \
doc_id), so the agent does not re-issue identical calls. Single \
sentence: "Already-called dsrag_kb: <doc_id_1>, <doc_id_2>, ..."

Third paragraph — gaps that still need to be filled to answer the \
original question. Single sentence; if no gaps, write "no further \
retrieval needed."

Output exactly those three paragraphs separated by blank lines, no \
headers, no bullets, no labels. The agent will reference this as \
context — do not format it in a way that invites being echoed to \
the user."""


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
    relevant to `question_text`. Uses the non-thinking DeepSeek variant
    (`deepseek-chat`) at T=0 for determinism — thinking-mode reasoning
    adds 10-25s of overhead that's wasted on a format-following task.

    Tagged `internal_llm` so the streaming layer suppresses these tokens
    instead of forwarding them to the user (this call's output is for
    the agent's context only, never for the user)."""
    from src.infrastructure.model import get_summary_model
    transcript = _serialize_messages_for_summary(messages)
    model = get_summary_model(temperature=0.0)
    prompt_messages = [
        SystemMessage(content=_SUMMARIZE_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"<question>\n{question_text}\n</question>\n\n"
            f"<transcript>\n{transcript}\n</transcript>"
        )),
    ]
    response = model.invoke(prompt_messages, config={"tags": ["internal_llm"]})
    return extract_text_content(response.content).strip()


# ---------------------------------------------------------------------------
# Question disambiguation (staging-node helper)
# ---------------------------------------------------------------------------
#
# `disambiguate_question` runs in `staging_node` — the first graph node.
# It resolves pronouns and implicit references in the user's current
# question using ONLY the immediately prior [Q, A] pair as context.
# The agent itself never sees conversation history; it always receives
# a single, self-contained HumanMessage.
#
# The prompt mirrors the pronoun-resolution language that previously
# lived inside AGENT_SYSTEM_PROMPT's <retrieval> section. By moving it
# to a dedicated node with limited context (one prior turn instead of
# the whole conversation), we avoid the "rewriter over-rewriting"
# failure mode where seeing many prior turns made the rewriter bake
# unrelated context into the question.

_DISAMBIGUATE_SYSTEM_PROMPT = """\
You receive the user's current input plus up to two prior \
[USER, ASSISTANT] turns (most recent last).

DEFAULT: return the input verbatim.

Rewrite ONLY if the input cannot be understood without the prior \
turns (pronouns, implicit period/scope, "what about X?" style \
substitution, or deictic phrases like "those companies"). Examples:

  - "how about its Q3?" after a turn about MGIC
    -> "What was MGIC's Q3 NIW?"
  - "what about essent?" after "What was Radian's 2024 NIW?"
    -> "What was Essent's 2024 NIW?"

When in doubt, return verbatim. Never turn an acknowledgement \
into a question, never invent specificity, never paraphrase a \
self-contained question.

Output ONLY the result on a single line. No preamble, no \
explanation, no quotes."""


def disambiguate_question(
    prior_pairs: list[tuple[str, str]],
    current_question: str,
) -> tuple[str, bool]:
    """Single LLM call: turn `current_question` into a self-contained
    question using up to 2 prior [Q, A] pairs as context. `prior_pairs`
    is in chronological order (oldest first). If there are no prior
    pairs, returns `current_question` unchanged (no LLM call).

    Returns (question, guard_fallback). guard_fallback=True means the
    rewrite was REJECTED by a hallucination guard and the original
    question is being returned — the caller should pass the prior
    turns through to the agent so disambiguation can still happen
    downstream (the original question may not be self-contained)."""
    if not prior_pairs:
        return current_question.strip(), False

    from src.infrastructure.model import get_summary_model

    transcript_parts: list[str] = []
    for i, (q, a) in enumerate(prior_pairs):
        # Tag turns relative to the current question so the LLM can
        # see ordering clearly (N-2 older, N-1 immediately prior).
        offset = len(prior_pairs) - i  # 2, 1
        transcript_parts.append(
            f"<turn position=\"N-{offset}\">\n"
            f"[USER]\n{q.strip()}\n\n"
            f"[ASSISTANT]\n{a.strip()}\n"
            f"</turn>"
        )
    transcript = "\n\n".join(transcript_parts)

    model = get_summary_model(temperature=0.0)
    prompt_messages = [
        SystemMessage(content=_DISAMBIGUATE_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"<prior_turns>\n{transcript}\n</prior_turns>\n\n"
            f"[USER — latest, disambiguate this]\n{current_question.strip()}"
        )),
    ]
    # `internal_llm` tag: streaming layer suppresses these tokens so
    # disambiguation work never reaches the UI.
    response = model.invoke(prompt_messages, config={"tags": ["internal_llm"]})
    text = extract_text_content(response.content).strip()
    # Strip surrounding quotes or a leading "Question:" if the model
    # adds one despite the instructions.
    text = text.strip('"\'')
    if text.lower().startswith("question:"):
        text = text[len("question:"):].strip()
    if not text:
        return current_question.strip(), False

    # ── Deterministic guards against rewriter hallucination ──────────
    # Observed live failure: "how does Enact's 2025 persistency compare
    # to the other MI companies?" was rewritten into the STATEMENT
    # "Enact's 2025 persistency of 82% is higher than Radian's 78% and
    # MGIC's 79%, but lower than Essent's 84%" — Radian/MGIC/Essent
    # figures fabricated from model memory. Prompt rules alone don't
    # pin down the small non-thinking rewriter, so enforce in code:
    source_text = current_question + " " + " ".join(q + " " + a for q, a in prior_pairs)
    source_numbers = set(re.findall(r"\d{2,}(?:\.\d+)?", source_text))
    rewrite_numbers = set(re.findall(r"\d{2,}(?:\.\d+)?", text))
    invented = rewrite_numbers - source_numbers
    if invented:
        logger.warning(
            f"disambiguate: rewrite invented numbers {sorted(invented)} not present "
            f"in inputs — falling back to original question + context passthrough"
        )
        return current_question.strip(), True

    # A question must stay a question. If the user asked something
    # ("?") and the rewrite contains no question mark, the rewriter
    # answered instead of rewriting (the T27-class failure).
    if current_question.strip().endswith("?") and "?" not in text:
        logger.warning(
            "disambiguate: question rewritten into a statement — "
            "falling back to original question + context passthrough"
        )
        return current_question.strip(), True

    return text, False


def _ids_to_removals(messages: list[BaseMessage]) -> list[BaseMessage]:
    """RemoveMessage entries for every message in `messages` that has an id."""
    return [RemoveMessage(id=m.id) for m in messages if getattr(m, "id", None)]


def _diff_removals(
    before: list[BaseMessage], after: list[BaseMessage]
) -> list[BaseMessage]:
    """RemoveMessage entries for messages present in `before` but not in
    `after` (matched by LangChain message id). Used after compaction to
    persist its dropping of intermediate tool blocks."""
    after_ids = {m.id for m in after if getattr(m, "id", None)}
    return [
        RemoveMessage(id=m.id)
        for m in before
        if getattr(m, "id", None) and m.id not in after_ids
    ]


def summarize_history(
    messages: list[BaseMessage],
    question_text: str,
) -> tuple[list[BaseMessage], list[BaseMessage]]:
    """Three-stage history condensation, mirroring trim_history's
    structure but replacing within-turn trim with an LLM summary.

    Returns (condensed_messages, state_updates) — feed condensed to the
    next LLM call, return state_updates through the messages reducer so
    the changes persist.

    Stage 1 — compact completed turns to [Q, final_A] pairs (cheap, no
    LLM). Drops the intermediate AIMessage(tool_calls) and ToolMessage
    chatter that's already folded into the final answer.

    Stage 2 — if the compacted total still exceeds HISTORY_TOKEN_BUDGET,
    evict completed [Q, A] pairs from the head, oldest-first.

    Stage 3 — if even the active turn alone exceeds budget (the cap+trim
    spiral that made `trim_history` lossy), drop all of head and replace
    the active turn's tool-call scratchwork with one LLM-authored
    SystemMessage that distills facts retrieved, tools called, and open
    questions. This is the only stage that incurs an LLM call; in
    normal multi-turn flow, Stages 1+2 keep state in budget without it.

    Anchoring on the LAST original HumanMessage is critical in
    multi-turn sessions: a first-anchor would swallow subsequent
    HumanMessages into the summary and the agent would answer turn 1
    instead of turn N.
    """
    # Stage 1: always compact (cheap, no LLM).
    compacted = _compact_completed_turns(messages)
    compaction_removals = _diff_removals(messages, compacted)

    if count_tokens_approximately(compacted) < HISTORY_TOKEN_BUDGET:
        if compaction_removals:
            logger.info(
                f"summarize_history Stage 1: compacted {len(messages)} → "
                f"{len(compacted)} msgs; under budget, no further work"
            )
        return compacted, compaction_removals

    last_human_idx = next(
        (
            i
            for i in range(len(compacted) - 1, -1, -1)
            if _is_original_user_message(compacted[i])
        ),
        None,
    )
    if last_human_idx is None:
        logger.warning(
            "summarize_history: no HumanMessage found; falling back to trim_history"
        )
        return trim_history(messages), []

    head = compacted[:last_human_idx]
    tail = compacted[last_human_idx:]   # [current_question, ...active scratchwork]
    tail_tokens = count_tokens_approximately(tail)

    # Stage 3: active turn alone exceeds budget. Drop head, summarize
    # active turn's scratchwork with the LLM.
    if tail_tokens >= HISTORY_TOKEN_BUDGET:
        question = tail[0]
        rest = tail[1:]
        head_removals = _ids_to_removals(head)
        if not rest:
            # Question alone is over budget — nothing to summarize.
            return [question], compaction_removals + head_removals

        logger.info(
            f"summarize_history Stage 3: compressing {len(rest)} active-turn "
            f"messages (~{count_tokens_approximately(rest):,} tokens) to a single summary"
        )
        summary_text = _llm_summarize(rest, question_text)
        summary_msg = SystemMessage(
            content=f"<prior_research_summary>\n{summary_text}\n</prior_research_summary>"
        )
        rest_removals = _ids_to_removals(rest)
        state_updates = compaction_removals + head_removals + rest_removals + [summary_msg]
        logger.info(
            f"summarize_history Stage 3: produced summary "
            f"(~{count_tokens_approximately([summary_msg]):,} tokens) — "
            f"removing {len(head_removals) + len(rest_removals)} msgs from state"
        )
        return [question, summary_msg], state_updates

    # Stage 2: active turn fits; evict oldest [Q, A] pairs from head until
    # compacted total fits budget.
    budget = HISTORY_TOKEN_BUDGET - tail_tokens
    evicted: list[BaseMessage] = []
    while head and count_tokens_approximately(head) > budget:
        next_h = next(
            (i for i in range(1, len(head)) if _is_original_user_message(head[i])),
            None,
        )
        if next_h is None:
            evicted.extend(head)
            head = []
        else:
            evicted.extend(head[:next_h])
            head = head[next_h:]

    eviction_removals = _ids_to_removals(evicted)
    if eviction_removals:
        logger.info(
            f"summarize_history Stage 2: evicted {len(evicted)} prior-turn "
            f"messages to fit budget"
        )
    return head + tail, compaction_removals + eviction_removals


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
    # Date anchor computed per call (this builder runs on every agent_node
    # invocation) so "most recent quarter" resolves against the real
    # current date, not a baked-in constant. kb_latest_summary is derived
    # from the loaded KB so corpus updates propagate automatically.
    from datetime import date

    from src.infrastructure.catalog import latest_periods_summary

    return (
        AGENT_SYSTEM_PROMPT
        .replace("{customer_name}", customer_name)
        .replace("{current_date}", date.today().strftime("%B %d, %Y"))
        .replace("{kb_latest_summary}", latest_periods_summary())
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
