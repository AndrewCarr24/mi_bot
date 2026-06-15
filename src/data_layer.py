"""Chainlit data layer factory — picks SQLite (local) or DynamoDB (prod)
based on the DATA_LAYER_BACKEND env var.

Threads and messages are persisted via Chainlit's BaseDataLayer
interface, keyed by `cl.User.identifier` (which we set to the
`agent_browser_id` cookie value via @cl.header_auth_callback in
chat.py). On every page load Chainlit hydrates the left-pane session
list from this layer; on every on_message we read prior messages out
of it (via `_fetch_thread_messages`, in chat.py) so the agent has
full context across container restarts.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from chainlit.data.base import BaseDataLayer
from loguru import logger


_DEFAULT_SQLITE_DIR = Path(__file__).resolve().parents[1] / ".chainlit"


# Chainlit's SQLAlchemyDataLayer expects these tables to exist already —
# the library doesn't ship a migration / create_all path. Schema mirrors
# what Chainlit 2.11.1 reads in `chainlit/data/sql_alchemy.py`. Pinned in
# pyproject.toml (chainlit>=2.11.1,<3); revisit on major upgrade.
SQLITE_SCHEMA_DDL = """
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
    "command" TEXT,
    "modes" TEXT,
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
    "defaultOpen" INTEGER,
    "autoCollapse" INTEGER,
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


def _ensure_sqlite_schema(db_path: Path) -> None:
    """Idempotently create Chainlit's SQLite schema. Safe to call repeatedly
    thanks to `IF NOT EXISTS`. Uses sync sqlite3 — runs once at factory time
    before the SQLAlchemyDataLayer (which is async) takes over."""
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(SQLITE_SCHEMA_DDL)
        conn.commit()


def _build_sqlite_layer() -> BaseDataLayer:
    """SQLAlchemy-backed data layer over a local aiosqlite file.

    Used for local development. Path can be overridden via the
    `DATA_LAYER_SQLITE_DIR` env var (used by tests).
    """
    from chainlit.data.sql_alchemy import SQLAlchemyDataLayer

    db_dir_env = os.environ.get("DATA_LAYER_SQLITE_DIR")
    db_dir = Path(db_dir_env) if db_dir_env else _DEFAULT_SQLITE_DIR
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "threads.db"
    _ensure_sqlite_schema(db_path)
    conninfo = f"sqlite+aiosqlite:///{db_path}"
    return SQLAlchemyDataLayer(conninfo=conninfo)


def _build_dynamodb_layer() -> BaseDataLayer:
    """DynamoDB-backed data layer. Used in production (App Runner).

    Reads:
      - DYNAMODB_THREADS_TABLE — table name (default "agent-fin-threads",
        usually overridden by CDK at deploy time).
      - AWS_REGION — region for the boto3 session.

    Auth comes from the App Runner instance role (see CDK runner_stack.py).
    """
    from chainlit.data.dynamodb import DynamoDBDataLayer

    table_name = os.environ.get("DYNAMODB_THREADS_TABLE", "agent-fin-threads")
    return DynamoDBDataLayer(table_name=table_name)


def get_data_layer() -> BaseDataLayer:
    """Return the data layer matching the current DATA_LAYER_BACKEND env."""
    backend = os.environ.get("DATA_LAYER_BACKEND", "sqlite").lower()
    if backend == "dynamodb":
        table = os.environ.get("DYNAMODB_THREADS_TABLE", "agent-fin-threads")
        logger.info("Data layer: DynamoDB (table={})", table)
        return _build_dynamodb_layer()
    db_dir_env = os.environ.get("DATA_LAYER_SQLITE_DIR")
    db_dir = Path(db_dir_env) if db_dir_env else _DEFAULT_SQLITE_DIR
    logger.info("Data layer: SQLite (path={}/threads.db)", db_dir)
    return _build_sqlite_layer()
