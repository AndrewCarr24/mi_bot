"""End-to-end smoke test: full browser flow against the real api.py app.

Mocks `get_kb` so the lifespan doesn't load the dsRAG store during tests.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def smoke_client(monkeypatch):
    monkeypatch.setenv("AGENT_PASSWORD", "smoke-pw")
    monkeypatch.setenv("COOKIE_SECRET", "b" * 64)
    # @cl.header_auth_callback causes Chainlit to enable auth, which requires
    # CHAINLIT_AUTH_SECRET. Set a dummy value for tests.
    monkeypatch.setenv("CHAINLIT_AUTH_SECRET", "c" * 64)

    # Mock KB loader so lifespan doesn't try to open the pickle.
    def _stub_get_kb():
        class _K:
            pass
        return _K()

    monkeypatch.setattr("src.infrastructure.dsrag_kb.get_kb", _stub_get_kb)

    # Reset rate limiter so we don't carry state.
    from src.auth import _rate_limiter
    _rate_limiter.reset()

    # Import lazily — env vars must be set first.
    from api import app
    return TestClient(app)


def test_full_browser_flow(smoke_client):
    # 1. Hit a protected URL unauthenticated → redirected to /login.
    r = smoke_client.get("/ask", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["location"]

    # 2. POST /login with correct password → 302 + cookie.
    r = smoke_client.post(
        "/login",
        data={"password": "smoke-pw", "next": "/health"},
        follow_redirects=False,
    )
    assert r.status_code == 302
    assert r.headers["location"] == "/health"
    assert "agent_session" in r.cookies

    # 3. Hit a protected URL with cookie → passes through.
    # /health is allow-listed, but use it as a smoke check that the cookie
    # is present and didn't break anything.
    r = smoke_client.get("/health")
    assert r.status_code == 200

    # 4. Logout → cookie cleared.
    r = smoke_client.get("/logout", follow_redirects=False)
    assert r.status_code == 302

    # 5. Hit a protected URL again → redirected (cookie no longer valid for
    # the new client; cookies dict is fresh in the next request).
    r = smoke_client.get("/ask", cookies={}, follow_redirects=False)
    assert r.status_code == 302
