"""LangGraph nodes: router, cache check, agent (ReAct), simple response, memory post-hook."""

import uuid

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from loguru import logger

from src.application.orchestrator.workflow.chains import (
    RouterOutput,
    get_agent_chain,
    get_finalize_chain,
    get_router_chain,
    get_simple_response_chain,
    trim_history,
    with_cache_on_last,
)
from src.application.orchestrator.workflow.state import AgentState, IntentType
from src.application.orchestrator.workflow.tools import wiki_read_page
from src.config import settings
from src.infrastructure.model import extract_text_content


async def router_node(state: AgentState, config: RunnableConfig) -> dict:
    """Classify intent + pick a wiki slug (if the question primarily matches
    a wiki page). Stores both on state for downstream nodes.
    """
    messages = list(state["messages"])
    chain = get_router_chain()
    try:
        response: RouterOutput = await chain.ainvoke({"messages": messages}, config)
        intent: IntentType = response.intent
        wiki_slug = response.wiki_slug
    except Exception as e:
        logger.warning(f"Router structured-output failed ({e}); defaulting to rag_query")
        intent = "rag_query"
        wiki_slug = None

    logger.info(f"Router classified: intent={intent} wiki_slug={wiki_slug!r}")
    return {"intent": intent, "wiki_slug": wiki_slug}


async def wiki_preload_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the wiki_read_page tool on behalf of the agent and inject the
    result into the message list as if the agent had called it.

    The agent doesn't have wiki_read_page bound as a tool — this node is
    the only path through which a wiki page enters context. That's how
    we enforce the "wiki at most once per turn" constraint.

    To keep the message list valid for providers that require tool_calls
    pairing (Bedrock Converse rejects orphan ToolMessages), we emit:
      AIMessage(content="", tool_calls=[{...wiki_read_page call...}])
      ToolMessage(content=<page>, tool_call_id=...)

    The agent in the next node sees this pair as if it had made the call
    itself. (Some Bedrock variants require AIMessage content to be
    non-empty when tool_calls is present; we set a one-line placeholder
    there too.)
    """
    slug = state.get("wiki_slug")
    if not slug:
        # Should be unreachable because the conditional edge gates entry,
        # but defensive in case state mutates.
        return {}

    content = wiki_read_page.invoke({"slug": slug})
    if isinstance(content, str) and content.lstrip().startswith('{"error"'):
        logger.warning(
            f"wiki_preload: slug={slug!r} returned error → skipping preload. "
            f"Response: {content[:200]}"
        )
        return {}

    tool_call_id = f"wiki_preload_{uuid.uuid4().hex[:8]}"
    placeholder = (
        f"Reading the {slug} wiki page to ground the answer "
        f"before consulting filings."
    )
    ai_msg = AIMessage(
        content=placeholder,
        tool_calls=[
            {
                "name": "wiki_read_page",
                "args": {"slug": slug},
                "id": tool_call_id,
                "type": "tool_call",
            }
        ],
        # DeepSeek thinking-mode requires reasoning_content on every
        # assistant message it sees — including this synthetic one we
        # inject pre-agent. ChatDeepSeekRoundtrip reads it from
        # additional_kwargs and emits it back to the API on the next
        # call. A short stub is sufficient; DeepSeek doesn't validate
        # the content.
        additional_kwargs={
            "reasoning_content": (
                f"Question primary-topic matches the {slug} wiki page. "
                f"Reading the page to ground the answer before consulting filings."
            )
        },
    )
    tool_msg = ToolMessage(
        content=content,
        name="wiki_read_page",
        tool_call_id=tool_call_id,
    )
    logger.info(f"wiki_preload: injected slug={slug!r} ({len(content)} chars)")
    return {"messages": [ai_msg, tool_msg]}


async def cache_check_node(state: AgentState, config: RunnableConfig) -> dict:
    """No-op placeholder. The old embedding-based answer cache lived in
    the retired `rag_app` package; we kept the node in the graph so the
    topology stays stable while the facts-DB tool path matures."""
    return {"cache_hit": False}


async def agent_node(state: AgentState, config: RunnableConfig) -> dict:
    """Run the ReAct agent for rag_query intents."""
    messages = list(state["messages"])
    tool_call_count = state.get("tool_call_count", 0)

    configurable = config.get("configurable", {})
    customer_name = configurable.get("customer_name", "Guest")

    messages = trim_history(messages)
    chain = get_agent_chain(customer_name=customer_name)
    response = await chain.ainvoke(
        {"messages": with_cache_on_last(messages)}, config
    )

    has_tool_calls = bool(getattr(response, "tool_calls", None))
    new_count = tool_call_count + (len(response.tool_calls) if has_tool_calls else 0)
    logger.debug(
        f"agent_node: has_tool_calls={has_tool_calls}, tool_call_count={new_count}"
    )
    return {"messages": response, "tool_call_count": new_count}


async def finalize_node(state: AgentState, config: RunnableConfig) -> dict:
    """Force a text answer after the ReAct tool budget is exhausted.

    Collapses the tool-call/tool-result message pairs into plain
    HumanMessages so Bedrock doesn't require a toolConfig, then asks
    the model (without tools) to synthesize a final answer.
    """
    from langchain_core.messages import ToolMessage

    raw_messages = list(state["messages"])
    condensed = []
    for msg in raw_messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            continue
        if isinstance(msg, ToolMessage):
            condensed.append(HumanMessage(
                content=f"[Tool result for '{msg.name}']\n{msg.content}"
            ))
            continue
        condensed.append(msg)

    condensed = trim_history(condensed)
    logger.debug(f"finalize_node: condensed {len(raw_messages)} msgs → {len(condensed)}")

    configurable = config.get("configurable", {})
    customer_name = configurable.get("customer_name", "Guest")

    chain = get_finalize_chain(customer_name=customer_name)
    response = await chain.ainvoke({"messages": condensed}, config)
    logger.info("finalize_node: produced fallback answer")
    return {"messages": response}


async def simple_response_node(state: AgentState, config: RunnableConfig) -> dict:
    """Handle greetings/thanks/off-topic without tools."""
    messages = list(state["messages"])
    configurable = config.get("configurable", {})
    customer_name = configurable.get("customer_name", "Guest")

    chain = get_simple_response_chain(customer_name=customer_name)
    response = await chain.ainvoke({"messages": messages}, config)
    return {"messages": response}


async def memory_post_hook(state: AgentState, config: RunnableConfig) -> dict:
    """Save the user/agent turn to AgentCore Memory strategies."""
    if not settings.MEMORY_ID:
        return {}

    from src.infrastructure.memory import get_memory_instance

    configurable = config.get("configurable", {})
    actor_id = configurable.get("actor_id", "user:default")
    session_id = configurable.get("thread_id", "default_session")

    messages = state.get("messages", [])
    user_input = ""
    agent_response = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not agent_response:
            if msg.content and not msg.tool_calls:
                agent_response = extract_text_content(msg.content)
        elif isinstance(msg, HumanMessage) and not user_input:
            user_input = extract_text_content(msg.content)
        if user_input and agent_response:
            break

    if not user_input or not agent_response:
        logger.debug("memory_post_hook: missing input or response, skipping")
        return {}

    try:
        memory = get_memory_instance()
        result = memory.process_turn(
            actor_id=actor_id,
            session_id=session_id,
            user_input=user_input,
            agent_response=agent_response,
        )
        if not result.get("success"):
            logger.warning(f"memory process_turn error: {result.get('error')}")
    except Exception as e:
        logger.error(f"memory_post_hook failed: {e}")

    return {}
