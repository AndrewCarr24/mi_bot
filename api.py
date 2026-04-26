"""FastAPI wrapper around the LangGraph agent.

Endpoints:
    GET  /health  → {"status": "ok"}      (liveness/readiness for ECS/App Runner)
    POST /ask     → text/plain stream     (agent answer, chunk-by-chunk)

Run locally:
    cd agent_fin
    set -a && . .env && set +a
    uvicorn api:app --host 0.0.0.0 --port 8000

The streaming response is plain text (not SSE) so `curl -N` works without
extra parsing. Switch to SSE if/when a browser UI needs structured events.

Cold-start optimization: KB load is kicked off in a background thread on
startup (`lifespan`), but `/health` returns as soon as uvicorn binds —
so App Runner marks the service ready early, the user can connect to the
UI while the KB is still deserializing, and `/ask` simply awaits the
in-progress future before hitting the agent.
"""

from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.application.orchestrator.streaming import get_streaming_response  # noqa: E402
from src.infrastructure.dsrag_kb import get_kb  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Eager-start the KB load so its cost overlaps with the user loading
    # the UI and typing their first question. get_kb() is sync (pickle
    # deserialization), so run it in the default executor. The future is
    # shared via app.state and awaited by /ask before invoking the agent.
    loop = asyncio.get_running_loop()
    app.state.kb_future = loop.run_in_executor(None, get_kb)
    yield


app = FastAPI(title="agent_fin", version="0.1.0", lifespan=lifespan)

# Chainlit chat UI mounted at /chat. The handlers live in chat.py; the
# Chainlit session id maps onto our LangGraph conversation_id so each
# browser session keeps its own multi-turn history.
from chainlit.utils import mount_chainlit  # noqa: E402

mount_chainlit(app=app, target="chat.py", path="/chat")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_id: str | None = None
    customer_name: str = "User"


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask")
async def ask(req: AskRequest) -> StreamingResponse:
    # Block (briefly, on first cold request) until the KB is loaded.
    # On a warm container the future is already done, so this is a no-op.
    await app.state.kb_future

    async def stream():
        async for chunk in get_streaming_response(
            messages=req.question,
            customer_name=req.customer_name,
            conversation_id=req.conversation_id,
        ):
            yield chunk

    return StreamingResponse(stream(), media_type="text/plain")
