from typing import Literal

from langchain_core.messages import AIMessage
from loguru import logger

from src.application.orchestrator.workflow.state import AgentState

# Maximum number of ReAct iterations (rounds of agent_node → tool_node) per
# user turn. Each iteration can dispatch multiple tool_calls in parallel, so
# the effective parallelism budget is roughly 3 × (typical parallel width).
# After this cap is hit, the graph routes to finalize_node, which forces a
# text answer from whatever has been retrieved. Tighter than the previous
# tool-call-count cap (16 individual calls) — encourages decisive retrieval
# over slow drift across many sequential rounds.
MAX_ITERATIONS_PER_TURN = 3


def route_by_intent(state: AgentState) -> Literal["cache_check", "simple_response"]:
    """Route router output: rag_query -> cache_check, otherwise -> simple_response."""
    intent = state.get("intent", "rag_query")
    if intent == "rag_query":
        return "cache_check"
    return "simple_response"


def route_after_cache(state: AgentState) -> Literal["agent"]:
    """Always route to agent after cache check.
    On a hit the cached answer is injected as context for the agent to evaluate.
    On a miss the agent proceeds with normal RAG."""
    return "agent"


def should_continue(state: AgentState) -> Literal["tools", "finalize", "end"]:
    """ReAct loop decision:
    - last message has tool_calls and iteration budget remains → run tools
    - last message has tool_calls but iteration budget exhausted → finalize
    - last message is a plain AI text response → end
    """
    messages = state.get("messages", [])
    iteration_count = state.get("iteration_count", 0)

    if not messages:
        return "end"

    last = messages[-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        if iteration_count >= MAX_ITERATIONS_PER_TURN:
            logger.warning(
                f"Iteration cap ({MAX_ITERATIONS_PER_TURN}) reached, routing to finalize"
            )
            return "finalize"
        return "tools"
    return "end"
