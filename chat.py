"""Chainlit chat handler — pipes user messages into the LangGraph agent.

Mounted into the FastAPI app at /chat by api.py via
`chainlit.utils.mount_chainlit`. The Chainlit session id is used as the
LangGraph `conversation_id`, so each browser session retains its own
multi-turn history via the in-process MemorySaver checkpointer.

While the agent is working, intermediate reasoning + tool-call summaries
are surfaced into a collapsible cl.Step ("Working..."). The final answer
streams into the main message. Tool *results* (raw chunks) are not shown.
"""

from __future__ import annotations

import sys
from pathlib import Path

import chainlit as cl


# Chainlit may exec this file from a different cwd than api.py — ensure
# the agent_fin root is importable either way.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.application.orchestrator.streaming import get_streaming_events  # noqa: E402


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content=(
            "Hi! I'm a SEC filings research assistant. Ask me about any of "
            "the indexed 10-K / 10-Q / 8-K filings or earnings call transcripts — "
            "financial figures, segment performance, MD&A commentary, or "
            "compare across companies."
        )
    ).send()


def _format_tool_call(tool: str, args: dict) -> str:
    """One-line summary of a tool invocation for display in the step."""
    if tool == "dsrag_kb":
        question = (args.get("question") or "").strip()
        doc_id = args.get("doc_id")
        if doc_id:
            return f"🔍 Searching {doc_id} for: {question!r}"
        return f"🔍 Searching all filings for: {question!r}"
    if tool == "memory_retrieval_tool":
        query = (args.get("query") or "").strip()
        return f"🧠 Recalling memory: {query!r}"
    # Fallback for any future tools
    arg_str = ", ".join(f"{k}={v!r}" for k, v in args.items()) or "(no args)"
    return f"🔧 {tool}({arg_str})"


@cl.on_message
async def on_message(message: cl.Message):
    """Stream the agent's response using Chainlit's recommended Step pattern.

    The step appears as a labeled box (with a Lucide search icon) that
    accumulates tool-call summaries and any reasoning text while the
    agent works. The answer message is created lazily on the first
    answer token so we never show an empty bubble. When the step's
    `async with` block exits, Chainlit folds the step down to a
    clickable summary the user can re-expand.
    """
    session_id = cl.context.session.id
    answer: cl.Message | None = None

    async with cl.Step(
        name="MI Knowledge Base Tool",
        default_open=True,
        show_input=False,
        icon="search",
    ) as step:
        try:
            async for event in get_streaming_events(
                messages=message.content,
                customer_name="User",
                conversation_id=session_id,
            ):
                kind = event.get("kind")

                if kind == "answer_token":
                    if answer is None:
                        answer = cl.Message(content="")
                        await answer.send()
                    await answer.stream_token(event["text"])

                elif kind == "rewind_to_thinking":
                    rewound = event["text"]
                    if answer and answer.content.endswith(rewound):
                        answer.content = answer.content[: -len(rewound)]
                        await answer.update()
                    step.output = (step.output or "") + rewound + "\n\n"
                    await step.update()

                elif kind == "tool_call":
                    summary = _format_tool_call(event["tool"], event.get("args", {}))
                    step.output = (step.output or "") + summary + "\n\n"
                    await step.update()

        except Exception as e:
            if answer is None:
                answer = cl.Message(content="")
                await answer.send()
            await answer.stream_token(f"\n\n[error: {type(e).__name__}: {e}]")

    if answer is not None:
        await answer.update()
