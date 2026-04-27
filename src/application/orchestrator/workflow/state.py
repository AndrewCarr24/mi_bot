from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


IntentType = Literal["rag_query", "simple", "off_topic"]


class AgentState(TypedDict):
    """State for the RAG agent graph (router + ReAct)."""

    messages: Annotated[list[BaseMessage], add_messages]
    customer_name: str
    intent: IntentType
    # Total number of individual dsrag_kb tool calls dispatched. Useful for
    # logging / observability. Increments by len(tool_calls) per agent_node.
    tool_call_count: int
    # Number of ReAct iterations that actually emitted tool_calls (i.e.
    # rounds of retrieval, regardless of how many parallel calls per round).
    # Bounded by MAX_ITERATIONS_PER_TURN in edges.should_continue.
    iteration_count: int
    cache_hit: bool
