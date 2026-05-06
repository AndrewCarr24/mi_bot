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
    tampered = f"{body}.{sig[:-1]}A"
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
