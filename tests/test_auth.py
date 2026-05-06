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
