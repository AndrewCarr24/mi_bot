"""Tests for src/auth.py — cookie helpers, middleware, login/logout."""

from __future__ import annotations

import time

import pytest


# ---------------------------------------------------------------- cookies --

def test_sign_verify_round_trip():
    from src.auth import sign_cookie, verify_cookie

    payload = {"exp": int(time.time()) + 100, "v": 1}
    cookie = sign_cookie(payload, secret="testsecret")
    assert verify_cookie(cookie, secret="testsecret") == payload


def test_verify_rejects_tampered_signature():
    from src.auth import sign_cookie, verify_cookie

    cookie = sign_cookie({"exp": int(time.time()) + 100, "v": 1}, secret="s")
    body, sig = cookie.split(".")
    # Flip a char in the middle of the signature, well away from base64
    # trailing-bit ambiguity. Pick a replacement different from current char.
    mid = len(sig) // 2
    replacement = "A" if sig[mid] != "A" else "B"
    tampered = f"{body}.{sig[:mid]}{replacement}{sig[mid+1:]}"
    assert verify_cookie(tampered, secret="s") is None


def test_verify_rejects_tampered_payload():
    from src.auth import sign_cookie, verify_cookie

    cookie = sign_cookie({"exp": int(time.time()) + 100, "v": 1}, secret="s")
    body, sig = cookie.split(".")
    # Replace last char of payload b64; signature now mismatches.
    tampered = f"{body[:-1]}A.{sig}"
    assert verify_cookie(tampered, secret="s") is None


def test_verify_rejects_expired():
    from src.auth import sign_cookie, verify_cookie

    cookie = sign_cookie({"exp": int(time.time()) - 1, "v": 1}, secret="s")
    assert verify_cookie(cookie, secret="s") is None


def test_verify_rejects_wrong_secret():
    from src.auth import sign_cookie, verify_cookie

    cookie = sign_cookie({"exp": int(time.time()) + 100, "v": 1}, secret="s1")
    assert verify_cookie(cookie, secret="s2") is None


def test_verify_rejects_malformed():
    from src.auth import verify_cookie

    assert verify_cookie("not.a.cookie", secret="s") is None
    assert verify_cookie("", secret="s") is None
    assert verify_cookie("nodot", secret="s") is None


# ---------------------------------------------------------------- rate limit --

def test_rate_limiter_allows_first_5():
    from src.auth import LoginRateLimiter

    rl = LoginRateLimiter(max_attempts=5, window_sec=60)
    for _ in range(5):
        assert rl.check_and_record("1.2.3.4") is True


def test_rate_limiter_blocks_6th():
    from src.auth import LoginRateLimiter

    rl = LoginRateLimiter(max_attempts=5, window_sec=60)
    for _ in range(5):
        rl.check_and_record("1.2.3.4")
    assert rl.check_and_record("1.2.3.4") is False


def test_rate_limiter_separates_ips():
    from src.auth import LoginRateLimiter

    rl = LoginRateLimiter(max_attempts=5, window_sec=60)
    for _ in range(5):
        rl.check_and_record("1.2.3.4")
    # Different IP starts fresh.
    assert rl.check_and_record("5.6.7.8") is True


def test_rate_limiter_window_expires(monkeypatch):
    from src.auth import LoginRateLimiter

    fake_time = [1000.0]
    monkeypatch.setattr("src.auth.time.monotonic", lambda: fake_time[0])

    rl = LoginRateLimiter(max_attempts=5, window_sec=60)
    for _ in range(5):
        rl.check_and_record("1.2.3.4")
    assert rl.check_and_record("1.2.3.4") is False

    fake_time[0] += 61  # past the window
    assert rl.check_and_record("1.2.3.4") is True


def test_rate_limiter_reset():
    from src.auth import LoginRateLimiter

    rl = LoginRateLimiter(max_attempts=5, window_sec=60)
    for _ in range(5):
        rl.check_and_record("1.2.3.4")
    rl.reset()
    assert rl.check_and_record("1.2.3.4") is True


# ---------------------------------------------------------------- middleware --

def test_health_bypasses_auth(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_login_get_bypasses_auth(client):
    r = client.get("/login", follow_redirects=False)
    assert r.status_code == 200  # login form rendered


def test_static_bypasses_auth(client):
    # The /static/* prefix is allow-listed. There's no actual static route
    # mounted in the test app, so we expect 404 — the key is that we get
    # 404 (router miss) and not 302 (middleware redirect).
    r = client.get("/static/app.js", follow_redirects=False)
    assert r.status_code != 302


def test_protected_path_redirects_when_no_cookie(client):
    r = client.get("/protected", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["location"]
    assert "next=%2Fprotected" in r.headers["location"]


def test_protected_path_next_includes_query_string(client):
    # Query-string portion of the original URL must be preserved (URL-encoded)
    # in the `next` redirect param so login can bounce back accurately.
    r = client.get("/protected?q=foo", follow_redirects=False)
    assert r.status_code == 302
    assert "next=%2Fprotected%3Fq%3Dfoo" in r.headers["location"]


def test_protected_path_passes_through_with_valid_cookie(client):
    from src.auth import sign_cookie
    cookie = sign_cookie({"exp": int(time.time()) + 100, "v": 1}, secret="a" * 64)
    r = client.get("/protected", cookies={"agent_session": cookie})
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_protected_path_redirects_when_invalid_cookie(client):
    r = client.get(
        "/protected",
        cookies={"agent_session": "garbage"},
        follow_redirects=False,
    )
    assert r.status_code == 302
    assert "/login" in r.headers["location"]


def test_protected_path_redirects_when_expired_cookie(client):
    from src.auth import sign_cookie
    cookie = sign_cookie({"exp": int(time.time()) - 1, "v": 1}, secret="a" * 64)
    r = client.get(
        "/protected",
        cookies={"agent_session": cookie},
        follow_redirects=False,
    )
    assert r.status_code == 302


def test_503_when_AGENT_PASSWORD_unset(monkeypatch):
    monkeypatch.setenv("AGENT_PASSWORD", "")
    monkeypatch.setenv("COOKIE_SECRET", "a" * 64)
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from src.auth import AuthMiddleware

    app = FastAPI()
    app.add_middleware(AuthMiddleware)

    @app.get("/x")
    def _x():
        return {"ok": True}

    c = TestClient(app)
    r = c.get("/x")
    assert r.status_code == 503
    assert "auth not configured" in r.text.lower()


def test_503_when_COOKIE_SECRET_unset(monkeypatch):
    monkeypatch.setenv("AGENT_PASSWORD", "x")
    monkeypatch.setenv("COOKIE_SECRET", "")
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from src.auth import AuthMiddleware

    app = FastAPI()
    app.add_middleware(AuthMiddleware)

    @app.get("/x")
    def _x():
        return {"ok": True}

    c = TestClient(app)
    r = c.get("/x")
    assert r.status_code == 503


# ---------------------------------------------------------------- login routes --

def test_login_post_correct_password_sets_cookie_and_redirects(client):
    r = client.post(
        "/login",
        data={"password": "test-password-123", "next": "/"},
        follow_redirects=False,
    )
    assert r.status_code == 302
    assert r.headers["location"] == "/"
    assert "agent_session" in r.cookies


def test_login_post_wrong_password_no_cookie(client):
    r = client.post(
        "/login",
        data={"password": "wrong", "next": "/"},
        follow_redirects=False,
    )
    assert r.status_code == 200  # re-renders form
    assert "agent_session" not in r.cookies
    assert "incorrect" in r.text.lower() or "wrong" in r.text.lower()


def test_login_post_respects_next_param(client):
    r = client.post(
        "/login",
        data={"password": "test-password-123", "next": "/chat"},
        follow_redirects=False,
    )
    assert r.status_code == 302
    assert r.headers["location"] == "/chat"


def test_login_post_rejects_absolute_next(client):
    r = client.post(
        "/login",
        data={"password": "test-password-123", "next": "https://evil.com/"},
        follow_redirects=False,
    )
    assert r.status_code == 302
    assert r.headers["location"] == "/"


def test_login_get_rejects_absolute_next(client):
    # The GET form should also sanitize: rendered hidden field should not
    # contain the malicious absolute URL.
    r = client.get("/login?next=https%3A%2F%2Fevil.com%2F")
    assert r.status_code == 200
    assert "evil.com" not in r.text


def test_login_post_rate_limits_after_5_attempts(client):
    for _ in range(5):
        client.post("/login", data={"password": "wrong", "next": "/"})
    r = client.post(
        "/login", data={"password": "wrong", "next": "/"},
        follow_redirects=False,
    )
    assert r.status_code == 429


def test_login_get_renders_form(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert "password" in r.text.lower()


def test_login_get_passes_next_to_form(client):
    r = client.get("/login?next=%2Fchat")
    assert r.status_code == 200
    assert "/chat" in r.text


def test_logout_clears_cookie(client):
    # Set the cookie first via login.
    client.post(
        "/login", data={"password": "test-password-123", "next": "/"},
        follow_redirects=False,
    )
    # Then logout.
    r = client.get("/logout", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["location"]
    # Cookie should be cleared (Set-Cookie with Max-Age=0 or expired).
    set_cookie = r.headers.get("set-cookie", "")
    assert "agent_session=" in set_cookie
    assert ("max-age=0" in set_cookie.lower()) or ("expires=" in set_cookie.lower())
