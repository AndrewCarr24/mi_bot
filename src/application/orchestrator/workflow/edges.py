import os
from typing import Literal

from langchain_core.messages import AIMessage
from loguru import logger

from src.application.orchestrator.workflow.state import AgentState

MAX_TOOL_CALLS_PER_TURN = int(os.environ.get("MAX_TOOL_CALLS_PER_TURN", "16"))


def route_by_intent(state: AgentState) -> Literal["cache_check", "simple_response"]:
    """Route router output: rag_query -> cache_check, otherwise -> simple_response."""
    intent = state.get("intent", "rag_query")
    if intent == "rag_query":
        return "cache_check"
    return "simple_response"


def route_after_cache(state: AgentState) -> Literal["wiki_preload", "agent"]:
    """Route after cache check.

    If the router matched a wiki slug, run wiki_preload_node first (which
    injects the page into the message list); otherwise skip straight to
    the agent. This gives wiki-shaped questions a guaranteed wiki read
    before the ReAct loop starts.

    Env override `DISABLE_WIKI_PRELOAD=true` forces the agent path
    regardless of slug — used for A/B testing the wiki contribution.
    """
    if os.environ.get("DISABLE_WIKI_PRELOAD", "").lower() == "true":
        return "agent"
    if state.get("wiki_slug"):
        return "wiki_preload"
    return "agent"


def should_continue(state: AgentState) -> Literal["tools", "finalize", "end"]:
    """ReAct loop decision:
    - last message has tool_calls and budget remains → run tools
    - last message has tool_calls but budget exhausted → finalize (force text answer)
    - last message is a plain AI text response → end
    """
    messages = state.get("messages", [])
    tool_call_count = state.get("tool_call_count", 0)

    if not messages:
        return "end"

    last = messages[-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        if tool_call_count >= MAX_TOOL_CALLS_PER_TURN:
            logger.warning(
                f"Tool call limit ({MAX_TOOL_CALLS_PER_TURN}) reached, routing to finalize"
            )
            return "finalize"
        return "tools"
    return "end"
