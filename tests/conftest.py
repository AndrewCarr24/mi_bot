"""Pytest fixtures for the auth test suite.

The `auth_app` fixture builds a minimal FastAPI app with our
AuthMiddleware + login routes mounted on top of two dummy endpoints
(/protected, /health). This keeps auth tests fast — they don't load
the dsRAG KB or the orchestrator graph that `api.py` lifespan brings up.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_env(monkeypatch):
    """Set the env vars our middleware requires before any import."""
    monkeypatch.setenv("AGENT_PASSWORD", "test-password-123")
    monkeypatch.setenv("COOKIE_SECRET", "a" * 64)
    return None


@pytest.fixture
def auth_app(test_env):
    """Minimal FastAPI app with auth wired in. No KB, no agent."""
    from fastapi import FastAPI
    from src.auth import AuthMiddleware, register_auth_routes, _rate_limiter

    _rate_limiter.reset()  # don't carry rate-limit state across tests

    app = FastAPI()
    app.add_middleware(AuthMiddleware)
    register_auth_routes(app)

    @app.get("/health")
    def _health():
        return {"status": "ok"}

    @app.get("/protected")
    def _protected():
        return {"ok": True}

    return app


@pytest.fixture
def client(auth_app):
    return TestClient(auth_app)
