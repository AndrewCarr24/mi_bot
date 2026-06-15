"""Tests for src/auth.BrowserIdMiddleware."""

import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def app_with_browser_id():
    """Minimal FastAPI app with only BrowserIdMiddleware installed.

    Includes a /probe route that echoes request.state.browser_id back so
    tests can verify downstream-readability without going through the
    real auth/agent stack.
    """
    from fastapi import Request
    from src.auth import BrowserIdMiddleware

    app = FastAPI()
    app.add_middleware(BrowserIdMiddleware)

    @app.get("/probe")
    def probe(request: Request):
        return {"browser_id": getattr(request.state, "browser_id", None)}

    return app


@pytest.fixture
def client(app_with_browser_id):
    # base_url="https://..." ensures the Secure cookie attribute is honoured
    # and the cookie is sent back on subsequent requests.
    return TestClient(app_with_browser_id, base_url="https://testserver")


def test_browser_id_set_on_first_request(client):
    r = client.get("/probe", cookies={})
    assert r.status_code == 200
    set_cookie = r.headers.get("set-cookie", "")
    assert "agent_browser_id=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Secure" in set_cookie
    assert "SameSite=lax" in set_cookie.lower() or "samesite=lax" in set_cookie.lower()
    assert "Max-Age=31536000" in set_cookie  # 365 * 86400
    assert "Path=/" in set_cookie


def test_browser_id_value_is_uuid4(client):
    r = client.get("/probe", cookies={})
    body = r.json()
    bid = body["browser_id"]
    assert bid is not None
    # UUID4 regex (relaxed: 8-4-4-4-12 hex)
    assert re.match(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        bid,
        re.IGNORECASE,
    )


def test_browser_id_persists_across_requests(client):
    # First request: no existing cookie — server mints a new one.
    r1 = client.get("/probe")
    bid1 = r1.json()["browser_id"]
    # Subsequent request: TestClient automatically holds the cookie.
    r2 = client.get("/probe")
    bid2 = r2.json()["browser_id"]
    assert bid1 == bid2
    # No new Set-Cookie on the second request.
    assert "set-cookie" not in {h.lower() for h in r2.headers.keys()} or "agent_browser_id=" not in r2.headers.get("set-cookie", "")


def test_browser_id_distinct_per_client(app_with_browser_id):
    c1 = TestClient(app_with_browser_id, base_url="https://testserver")
    c2 = TestClient(app_with_browser_id, base_url="https://testserver")
    bid1 = c1.get("/probe").json()["browser_id"]
    bid2 = c2.get("/probe").json()["browser_id"]
    assert bid1 != bid2


def test_browser_id_not_overwritten_when_cookie_already_present(client):
    existing = "deadbeef-1111-2222-3333-444455556666"
    r = client.get("/probe", cookies={"agent_browser_id": existing})
    assert r.json()["browser_id"] == existing
    # No new Set-Cookie since the cookie was already present.
    sc = r.headers.get("set-cookie", "")
    assert "agent_browser_id=" not in sc


def test_browser_id_available_on_request_state(client):
    r = client.get("/probe", cookies={})
    assert r.json()["browser_id"] is not None  # i.e. request.state was populated
