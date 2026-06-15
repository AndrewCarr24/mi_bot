"""LangGraph workflow: router + ReAct agent with RAG tool + memory post-hook."""

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from loguru import logger

from src.application.orchestrator.workflow.edges import (
    route_by_intent,
    should_continue,
)
from src.application.orchestrator.workflow.nodes import (
    agent_node,
    finalize_node,
    memory_post_hook,
    router_node,
    simple_response_node,
    staging_node,
    wiki_preload_node,
)
from src.application.orchestrator.workflow.state import AgentState
from src.application.orchestrator.workflow.tools import get_tools

_graph_instance = None


def create_graph(force_recreate: bool = False):
    """
    Build the agent graph.

        START -> staging_node -> router_node -> [intent? + wiki_slug?]
                                                  ├── rag_query + slug   -> wiki_preload_node -> agent_node <-> tool_node
                                                  ├── rag_query (no slug) -> agent_node                     <-> tool_node
                                                  └── simple/off          -> simple_response_node
                                                                           │
                                                                  memory_post_hook -> END

    staging_node is the seam between multi-turn UI and single-turn
    agent behavior. It disambiguates the current question against the
    immediately prior [Q, A] (using ONE LLM call) and wipes state
    down to a single HumanMessage. Router/agent/finalize never see
    conversation history. No-op for true first turns.
    """
    global _graph_instance
    if _graph_instance is not None and not force_recreate:
        return _graph_instance

    logger.info("Creating RAG agent graph (staging + router + ReAct + memory)")

    builder = StateGraph(AgentState)
    builder.add_node("staging_node", staging_node)
    builder.add_node("router_node", router_node)
    builder.add_node("wiki_preload_node", wiki_preload_node)
    builder.add_node("agent_node", agent_node)
    builder.add_node("simple_response_node", simple_response_node)
    builder.add_node("finalize_node", finalize_node)
    builder.add_node("tool_node", ToolNode(get_tools()))
    builder.add_node("memory_post_hook", memory_post_hook)

    builder.add_edge(START, "staging_node")
    builder.add_edge("staging_node", "router_node")
    builder.add_conditional_edges(
        "router_node",
        route_by_intent,
        {
            "wiki_preload": "wiki_preload_node",
            "agent": "agent_node",
            "simple_response": "simple_response_node",
        },
    )
    builder.add_edge("wiki_preload_node", "agent_node")
    builder.add_conditional_edges(
        "agent_node",
        should_continue,
        {
            "tools": "tool_node",
            "finalize": "finalize_node",
            "end": "memory_post_hook",
        },
    )
    builder.add_edge("tool_node", "agent_node")
    builder.add_edge("finalize_node", "memory_post_hook")
    builder.add_edge("simple_response_node", "memory_post_hook")
    builder.add_edge("memory_post_hook", END)

    # Per the sessions design (2026-05-06): the graph runs stateless.
    # Thread context is replayed on every turn from the Chainlit data
    # layer (chat.py:_fetch_thread_messages), so a checkpointer would
    # only duplicate that state. AgentCoreMemorySaver / MemorySaver
    # both removed.
    _graph_instance = builder.compile()
    logger.info("RAG agent graph compiled (stateless — no checkpointer)")
    return _graph_instance


def reset_graph() -> None:
    global _graph_instance
    _graph_instance = None
