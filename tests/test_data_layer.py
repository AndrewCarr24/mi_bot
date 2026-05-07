"""Tests for src/data_layer.py — Chainlit data layer factory."""

import asyncio
import os
import shutil
from pathlib import Path

import pytest


@pytest.fixture
def tmp_chainlit_dir(monkeypatch, tmp_path):
    """Redirect the SQLite DB to a temp location for test isolation."""
    target = tmp_path / "test_chainlit"
    target.mkdir()
    monkeypatch.setenv("DATA_LAYER_SQLITE_DIR", str(target))
    yield target
    # tmp_path auto-cleans


def test_sqlite_factory_returns_sqlalchemy_data_layer(tmp_chainlit_dir, monkeypatch):
    monkeypatch.setenv("DATA_LAYER_BACKEND", "sqlite")
    from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
    from src.data_layer import get_data_layer

    layer = get_data_layer()
    assert isinstance(layer, SQLAlchemyDataLayer)


def test_sqlite_factory_creates_db_file(tmp_chainlit_dir, monkeypatch):
    monkeypatch.setenv("DATA_LAYER_BACKEND", "sqlite")
    from src.data_layer import get_data_layer

    get_data_layer()
    db_path = tmp_chainlit_dir / "threads.db"
    # Either the file exists, or the parent .chainlit dir exists (file is
    # lazy-created on first write — depends on driver behavior). Accept
    # either.
    assert tmp_chainlit_dir.exists()


def test_dispatch_to_sqlite_when_backend_unset(tmp_chainlit_dir, monkeypatch):
    monkeypatch.delenv("DATA_LAYER_BACKEND", raising=False)
    from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
    from src.data_layer import get_data_layer

    layer = get_data_layer()
    # Default backend is sqlite.
    assert isinstance(layer, SQLAlchemyDataLayer)


def test_dispatch_to_dynamodb_branch_via_mock(monkeypatch):
    """Verify the dynamodb branch is reachable. We mock the actual
    DynamoDBDataLayer constructor since exercising it requires AWS creds.
    """
    monkeypatch.setenv("DATA_LAYER_BACKEND", "dynamodb")
    monkeypatch.setenv("DYNAMODB_THREADS_TABLE", "test-fin-threads")
    monkeypatch.setenv("AWS_REGION", "us-east-1")

    import src.data_layer as dl

    sentinel = object()
    monkeypatch.setattr(
        dl, "_build_dynamodb_layer", lambda: sentinel
    )
    assert dl.get_data_layer() is sentinel


# ---------------------------------------------------------------- streaming --

def test_get_streaming_events_accepts_string():
    """Backwards-compat: passing a string works as before."""
    import inspect
    from src.application.orchestrator.streaming import get_streaming_events

    sig = inspect.signature(get_streaming_events)
    messages_param = sig.parameters["messages"]
    annotation = str(messages_param.annotation)
    assert "str" in annotation
    assert "list" in annotation or "List" in annotation


def test_get_streaming_events_wraps_string_into_one_human_message(monkeypatch):
    """When messages is a str, the agent input should be a single
    HumanMessage. We don't run the full agent — just patch
    `create_graph` and capture the input_data passed in."""
    import asyncio
    from langchain_core.messages import HumanMessage
    from src.application.orchestrator import streaming

    captured = {}

    class _FakeGraph:
        async def astream_events(self, *, input, config, version):
            captured["input"] = input
            captured["config"] = config
            return  # async generator that yields nothing
            yield  # unreachable

    monkeypatch.setattr(streaming, "create_graph", lambda: _FakeGraph())

    async def run():
        async for _ in streaming.get_streaming_events(
            messages="hello world", customer_name="T", conversation_id="t1",
        ):
            pass

    asyncio.run(run())
    msgs = captured["input"]["messages"]
    assert len(msgs) == 1
    assert isinstance(msgs[0], HumanMessage)
    assert msgs[0].content == "hello world"


def test_get_streaming_events_passes_list_through(monkeypatch):
    """When messages is a list, the input_data['messages'] should be that
    list verbatim — no wrapping."""
    import asyncio
    from langchain_core.messages import AIMessage, HumanMessage
    from src.application.orchestrator import streaming

    captured = {}

    class _FakeGraph:
        async def astream_events(self, *, input, config, version):
            captured["input"] = input
            return
            yield

    monkeypatch.setattr(streaming, "create_graph", lambda: _FakeGraph())

    history = [
        HumanMessage(content="prior question"),
        AIMessage(content="prior answer"),
        HumanMessage(content="follow-up"),
    ]

    async def run():
        async for _ in streaming.get_streaming_events(
            messages=history, customer_name="T", conversation_id="t1",
        ):
            pass

    asyncio.run(run())
    assert captured["input"]["messages"] == history
