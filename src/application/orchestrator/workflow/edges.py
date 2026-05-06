import os
from typing import Literal

from langchain_core.messages import AIMessage
from loguru import logger

from src.application.orchestrator.workflow.state import AgentState

MAX_TOOL_CALLS_PER_TURN = int(os.environ.get("MAX_TOOL_CALLS_PER_TURN", "12"))


def route_by_intent(state: AgentState) -> Literal["wiki_preload", "agent", "simple_response"]:
    """Dispatch from router_node:
    - non-rag intents -> simple_response
    - rag_query with a wiki_slug -> wiki_preload (injects the page before the ReAct loop)
    - rag_query without a slug -> agent

    Env override `DISABLE_WIKI_PRELOAD=true` forces rag_query straight to agent
    regardless of slug — used for A/B testing the wiki contribution.
    """
    intent = state.get("intent", "rag_query")
    if intent != "rag_query":
        return "simple_response"
    if os.environ.get("DISABLE_WIKI_PRELOAD", "").lower() == "true":
        return "agent"
    if state.get("wiki_slug"):
        return "wiki_preload"
    return "agent"


def should_continue(state: AgentState) -> Literal["tools", "finalize", "end"]:
    """ReAct loop decision:
    - last message has tool_calls and prior count under cap → run tools
    - last message has tool_calls but PRIOR count >= cap → finalize
    - last message is a plain AI text response → end

    Cap semantics: the cap stops further loop iterations, not the current
    batch of tool calls. We compare `tool_call_count - len(last.tool_calls)`
    (i.e., the count *before* this iteration's emission) against the cap.
    A single oversized fan-out (e.g., 12 calls when prior count was 0)
    therefore executes in full instead of being aborted with zero
    executed calls — the cap kicks in on the NEXT iteration if the agent
    tries to fan out again.
    """
    messages = state.get("messages", [])
    tool_call_count = state.get("tool_call_count", 0)

    if not messages:
        return "end"

    last = messages[-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        prior_count = tool_call_count - len(last.tool_calls)
        if prior_count >= MAX_TOOL_CALLS_PER_TURN:
            logger.warning(
                f"Tool call limit ({MAX_TOOL_CALLS_PER_TURN}) reached "
                f"(prior_count={prior_count}); routing to finalize"
            )
            return "finalize"
        return "tools"
    return "end"
