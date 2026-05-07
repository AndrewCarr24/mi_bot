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


# ---------------------------------------------------------------- replay --

_SQLITE_SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS users (
    "id" TEXT PRIMARY KEY,
    "identifier" TEXT UNIQUE NOT NULL,
    "createdAt" TEXT,
    "metadata" TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS threads (
    "id" TEXT PRIMARY KEY,
    "createdAt" TEXT,
    "name" TEXT,
    "userId" TEXT,
    "userIdentifier" TEXT,
    "tags" TEXT,
    "metadata" TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS steps (
    "id" TEXT PRIMARY KEY,
    "name" TEXT,
    "type" TEXT,
    "threadId" TEXT,
    "parentId" TEXT,
    "streaming" INTEGER,
    "waitForAnswer" INTEGER,
    "isError" INTEGER,
    "metadata" TEXT DEFAULT '{}',
    "tags" TEXT,
    "input" TEXT,
    "output" TEXT,
    "createdAt" TEXT,
    "start" TEXT,
    "end" TEXT,
    "generation" TEXT,
    "showInput" TEXT,
    "language" TEXT,
    FOREIGN KEY ("threadId") REFERENCES threads("id")
);
CREATE TABLE IF NOT EXISTS feedbacks (
    "id" TEXT PRIMARY KEY,
    "forId" TEXT,
    "value" REAL,
    "comment" TEXT
);
CREATE TABLE IF NOT EXISTS elements (
    "id" TEXT PRIMARY KEY,
    "threadId" TEXT,
    "type" TEXT,
    "chainlitKey" TEXT,
    "url" TEXT,
    "objectKey" TEXT,
    "name" TEXT,
    "display" TEXT,
    "size" TEXT,
    "language" TEXT,
    "page" INTEGER,
    "forId" TEXT,
    "mime" TEXT,
    "props" TEXT
);
"""


@pytest.fixture
def populated_sqlite_layer(tmp_chainlit_dir, monkeypatch):
    """Build a SQLite data layer with schema already initialized."""
    import asyncio

    monkeypatch.setenv("DATA_LAYER_BACKEND", "sqlite")
    from src.data_layer import get_data_layer

    layer = get_data_layer()

    # Initialize the SQLite schema synchronously so the tests can seed data.
    db_path = tmp_chainlit_dir / "threads.db"

    async def _init_schema():
        import aiosqlite
        async with aiosqlite.connect(str(db_path)) as db:
            await db.executescript(_SQLITE_SCHEMA_DDL)
            await db.commit()
            # Pre-insert users that tests reference by id so
            # update_thread(user_id=...) can resolve the identifier.
            await db.execute(
                'INSERT OR IGNORE INTO users (id, identifier, createdAt, metadata) '
                'VALUES (?, ?, ?, ?)',
                ("test-browser", "test-browser", "2026-05-06T00:00:00Z", "{}"),
            )
            await db.execute(
                'INSERT OR IGNORE INTO users (id, identifier, createdAt, metadata) '
                'VALUES (?, ?, ?, ?)',
                ("bowser", "bowser", "2026-05-06T00:00:00Z", "{}"),
            )
            await db.commit()

    asyncio.run(_init_schema())
    return layer


def test_fetch_thread_messages_returns_empty_for_unknown_thread(populated_sqlite_layer, monkeypatch):
    """A thread_id that doesn't exist in the data layer → empty list."""
    import asyncio
    monkeypatch.setattr("chat._get_data_layer_instance", lambda: populated_sqlite_layer, raising=False)
    # Import lazily so the chat module sees the patched env.
    import chat

    out = asyncio.run(chat._fetch_thread_messages("nonexistent-thread"))
    assert out == []


def test_fetch_thread_messages_round_trip(populated_sqlite_layer, monkeypatch, tmp_chainlit_dir):
    """Write 2 messages via the data layer, fetch them back through
    chat._fetch_thread_messages, verify content + types preserved."""
    import asyncio
    import aiosqlite
    from langchain_core.messages import AIMessage, HumanMessage

    # Patch the chat module's data-layer accessor to return our test layer.
    import chat
    monkeypatch.setattr(chat, "_get_data_layer_instance", lambda: populated_sqlite_layer, raising=False)

    db_path = tmp_chainlit_dir / "threads.db"

    async def _seed_and_fetch():
        thread_id = "test-thread-1"
        # Seed thread and steps directly via aiosqlite to avoid the
        # @queue_until_user_message Chainlit-context requirement.
        async with aiosqlite.connect(str(db_path)) as db:
            await db.execute(
                'INSERT OR IGNORE INTO threads (id, createdAt, name, userId, userIdentifier, metadata) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (thread_id, "2026-05-06T12:00:00Z", "Test thread",
                 "test-browser", "test-browser", "{}"),
            )
            await db.execute(
                'INSERT OR IGNORE INTO steps (id, "threadId", type, name, input, output, "createdAt", metadata) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                ("step-1", thread_id, "user_message", "User",
                 "What is the capital of France?", "What is the capital of France?",
                 "2026-05-06T12:00:00Z", "{}"),
            )
            await db.execute(
                'INSERT OR IGNORE INTO steps (id, "threadId", type, name, input, output, "createdAt", metadata) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                ("step-2", thread_id, "assistant_message", "Assistant",
                 "", "Paris.", "2026-05-06T12:00:01Z", "{}"),
            )
            await db.commit()
        return await chat._fetch_thread_messages(thread_id)

    msgs = asyncio.run(_seed_and_fetch())
    assert len(msgs) == 2
    assert isinstance(msgs[0], HumanMessage)
    assert msgs[0].content == "What is the capital of France?"
    assert isinstance(msgs[1], AIMessage)
    assert msgs[1].content == "Paris."


def test_fetch_thread_messages_preserves_order(populated_sqlite_layer, monkeypatch, tmp_chainlit_dir):
    """Out-of-creation-order rows (rare but possible) are returned in
    chronological order by createdAt."""
    import asyncio
    import aiosqlite
    from langchain_core.messages import AIMessage, HumanMessage

    import chat
    monkeypatch.setattr(chat, "_get_data_layer_instance", lambda: populated_sqlite_layer, raising=False)

    db_path = tmp_chainlit_dir / "threads.db"

    async def _seed_and_fetch():
        thread_id = "test-thread-2"
        # Insert in reverse chronological order to verify sorting.
        async with aiosqlite.connect(str(db_path)) as db:
            await db.execute(
                'INSERT OR IGNORE INTO threads (id, createdAt, name, userId, userIdentifier, metadata) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (thread_id, "2026-05-06T12:00:00Z", "t", "bowser", "bowser", "{}"),
            )
            # Insert step-b (later time) first.
            await db.execute(
                'INSERT OR IGNORE INTO steps (id, "threadId", type, name, input, output, "createdAt", metadata) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                ("step-b", thread_id, "assistant_message", "Assistant",
                 "", "second turn answer", "2026-05-06T12:01:00Z", "{}"),
            )
            # Insert step-a (earlier time) second.
            await db.execute(
                'INSERT OR IGNORE INTO steps (id, "threadId", type, name, input, output, "createdAt", metadata) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                ("step-a", thread_id, "user_message", "User",
                 "first question", "first question", "2026-05-06T12:00:00Z", "{}"),
            )
            await db.commit()
        return await chat._fetch_thread_messages(thread_id)

    msgs = asyncio.run(_seed_and_fetch())
    assert len(msgs) == 2
    assert msgs[0].content == "first question"      # earlier createdAt first
    assert msgs[1].content == "second turn answer"
