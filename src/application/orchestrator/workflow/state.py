from typing import Annotated, Literal, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


IntentType = Literal["rag_query", "simple", "off_topic"]


class AgentState(TypedDict):
    """State for the RAG agent graph (router + ReAct)."""

    messages: Annotated[list[BaseMessage], add_messages]
    customer_name: str
    intent: IntentType
    # Slug of the wiki page to pre-load before the agent runs (e.g.
    # "topics/pmiers"), or None if the question doesn't primarily map
    # to any wiki page. Set by the router; consumed by wiki_preload_node.
    wiki_slug: Optional[str]
    tool_call_count: int
    cache_hit: bool
