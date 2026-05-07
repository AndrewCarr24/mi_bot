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
from pathlib import Path

from chainlit.data.base import BaseDataLayer


_DEFAULT_SQLITE_DIR = Path(__file__).resolve().parents[1] / ".chainlit"


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
        return _build_dynamodb_layer()
    return _build_sqlite_layer()
