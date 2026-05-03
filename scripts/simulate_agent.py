"""Fast deterministic harness for agent-state behavior checks.

Lets you verify how the agent's prompt-construction pipeline (history
condensation, prompt-cache placement, system prompt rendering) handles a
given message list — without making LLM calls.

Typical use: when iterating on trim_history / summarize_history / prompt
templates, build a synthetic state, run inspect_agent_input on it, and
assert the message list looks right. Sub-second feedback vs. ~30-60s
per real eval question.

CLI:
    cd agent_fin
    python scripts/simulate_agent.py            # built-in 4-turn fixture
    python scripts/simulate_agent.py --json path/to/state.json

Library:
    from scripts.simulate_agent import inspect_agent_input
    out = inspect_agent_input(messages)
    assert len(out["llm_messages"]) == ...
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[1]))

from langchain_core.messages import (  # noqa: E402
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.messages.utils import count_tokens_approximately  # noqa: E402

from src.application.orchestrator.workflow.chains import (  # noqa: E402
    HISTORY_TOKEN_BUDGET,
    _compact_completed_turns,
    _is_original_user_message,
    _turn_boundaries,
    trim_history,
    with_cache_on_last,
)


def inspect_agent_input(
    messages: list[BaseMessage],
) -> dict[str, Any]:
    """Return what the agent's pipeline would feed the LLM, plus diagnostics.

    Pure function. No env reads. No LLM calls. Deterministic.

    Returns a dict with:
      - input_messages_count, input_tokens
      - turn_boundaries: indices of original HumanMessages
      - compacted_messages_count, compacted_tokens (after Stage 1)
      - llm_messages, llm_tokens (after full trim_history)
      - prior_final_a_present: True if the last completed turn's final
        A is present in the LLM-bound list (key signal for follow-up
        disambiguation working)
    """
    in_count = len(messages)
    in_tokens = count_tokens_approximately(messages)

    boundaries = _turn_boundaries(messages)
    compacted = _compact_completed_turns(messages)
    comp_count = len(compacted)
    comp_tokens = count_tokens_approximately(compacted)

    trimmed = trim_history(list(messages))
    cache_marked = with_cache_on_last(trimmed)
    out_tokens = count_tokens_approximately(cache_marked)

    # Disambiguation signal: is the prior turn's final-A in the LLM input?
    prior_final_a_present = False
    if len(boundaries) >= 2:
        prior_turn_start = boundaries[-2]
        prior_turn_end = boundaries[-1]
        for i in range(prior_turn_end - 1, prior_turn_start - 1, -1):
            m = messages[i]
            if isinstance(m, AIMessage) and not m.tool_calls and m.content:
                prior_final_a_present = m in trimmed
                break

    return {
        "input_messages_count": in_count,
        "input_tokens": in_tokens,
        "turn_boundaries": boundaries,
        "compacted_messages_count": comp_count,
        "compacted_tokens": comp_tokens,
        "llm_messages_count": len(cache_marked),
        "llm_tokens": out_tokens,
        "history_budget": HISTORY_TOKEN_BUDGET,
        "fits_budget": out_tokens <= HISTORY_TOKEN_BUDGET,
        "prior_final_a_present": prior_final_a_present,
        "llm_messages": cache_marked,
    }


def _msg_summary(m: BaseMessage) -> str:
    name = type(m).__name__
    content = m.content if isinstance(m.content, str) else str(m.content)
    L = len(content)
    if isinstance(m, AIMessage) and m.tool_calls:
        tc_names = [tc.get("name", "?") for tc in m.tool_calls]
        return f"{name}(len={L}, tool_calls={tc_names})"
    if isinstance(m, ToolMessage):
        return f"{name}(name={m.name!r}, len={L})"
    return f"{name}(len={L})"


def _builtin_fixture() -> list[BaseMessage]:
    """The 4-turn 'Inigo / new entrant / Radian calls' conversation that
    exposed the trim_history bug — useful as a default sanity probe."""
    def H(c): return HumanMessage(content=c)
    def A(c): return AIMessage(content=c)
    def AT(c, name): return AIMessage(
        content=c,
        tool_calls=[{"name": name, "args": {}, "id": "tc", "type": "tool_call"}],
    )
    def T(c, name): return ToolMessage(content=c, name=name, tool_call_id="tc")
    pad = "x" * 100  # filler
    return [
        H("Q1: Inigo at Radian / time period?"),
        AT("reading wiki", "wiki_read_page"), T("[wiki content " + pad * 100 + "]", "wiki_read_page"),
        AT("checking transcripts", "dsrag_kb"), T("[seg " + pad * 50 + "]", "dsrag_kb"),
        A("A1: Yes, analysts asked extensively..." + pad * 5),
        H("Q2: Inigo at other MIs?"),
        AT("checking", "dsrag_kb"),
        T("[mtg]" + pad * 30, "dsrag_kb"), T("[esnt]" + pad * 30, "dsrag_kb"),
        T("[ngmi]" + pad * 30, "dsrag_kb"), T("[acgl]" + pad * 30, "dsrag_kb"),
        T("[act]" + pad * 30, "dsrag_kb"),
        A("A2: No, none of the others mentioned Inigo" + pad * 3),
        H("Q3: was a possible new entrant mentioned in any of the calls?"),
        AT("searching", "dsrag_kb"),
        T("[mtg q4]" + pad * 30, "dsrag_kb"), T("[act q4]" + pad * 30, "dsrag_kb"),
        T("[esnt q4]" + pad * 30, "dsrag_kb"), T("[acgl q4]" + pad * 30, "dsrag_kb"),
        T("[nmih q4]" + pad * 30, "dsrag_kb"),
        A("A3: Yes — MGIC Q3 2025 mentioned new MI entrant." + pad * 3),
        H("Q4: okay. what about Radian calls? you didn't mention those"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json",
        type=Path,
        help="Path to a JSON file with serialized messages (LangChain dict format).",
    )
    parser.add_argument("--show-llm-messages", action="store_true")
    args = parser.parse_args()

    if args.json:
        from langchain_core.load import load
        data = json.loads(args.json.read_text())
        messages = [load(d) for d in data]
        print(f"Loaded {len(messages)} messages from {args.json}")
    else:
        messages = _builtin_fixture()
        print(f"Using built-in 4-turn fixture ({len(messages)} messages)")

    out = inspect_agent_input(messages)
    print(f"\nState in:    {out['input_messages_count']} msgs / ~{out['input_tokens']:,} tok")
    print(f"Turn starts: {out['turn_boundaries']}")
    print(f"After Stage 1 compaction: {out['compacted_messages_count']} msgs / ~{out['compacted_tokens']:,} tok")
    print(f"LLM-bound messages:       {out['llm_messages_count']} msgs / ~{out['llm_tokens']:,} tok "
          f"(budget={out['history_budget']:,}, fits={out['fits_budget']})")
    print(f"Prior turn's final A in LLM input? {out['prior_final_a_present']}")

    if args.show_llm_messages:
        print("\nLLM-bound messages:")
        for i, m in enumerate(out["llm_messages"]):
            print(f"  [{i}] {_msg_summary(m)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
