"""Chainlit chat handler — pipes user messages into the LangGraph agent.

Mounted into the FastAPI app at /chat by api.py via
`chainlit.utils.mount_chainlit`. The Chainlit session id is used as the
LangGraph `conversation_id`, so each browser session retains its own
multi-turn history via the in-process MemorySaver checkpointer.
"""

from __future__ import annotations

import sys
from pathlib import Path

import chainlit as cl


# Chainlit may exec this file from a different cwd than api.py — ensure
# the agent_fin root is importable either way.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.application.orchestrator.streaming import get_streaming_response  # noqa: E402


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content=(
            "Hi! I'm a SEC filings research assistant. Ask me about any of "
            "the indexed 10-K / 10-Q filings — financial figures, segment "
            "performance, MD&A commentary, or compare across companies."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    # Stable per-browser-session id → drives the LangGraph checkpointer's
    # thread_id, giving each tab its own multi-turn history.
    session_id = cl.context.session.id

    answer = cl.Message(content="")
    await answer.send()

    try:
        async for chunk in get_streaming_response(
            messages=message.content,
            customer_name="User",
            conversation_id=session_id,
        ):
            await answer.stream_token(chunk)
    except Exception as e:
        await answer.stream_token(f"\n\n[error: {type(e).__name__}: {e}]")

    await answer.update()
