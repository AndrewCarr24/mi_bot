"""Auth: cookie helpers, middleware, login/logout routes, rate limiter.

Single-shared-password gate. Cookie carries its own auth assertion
(HMAC of {"exp": ..., "v": 1}) — no server-side session store.
"""

from __future__ import annotations

import base64
import hmac
import hashlib
import json
import time
from typing import Optional


def _b64encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _b64decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def sign_cookie(payload: dict, secret: str) -> str:
    """HMAC-SHA256 sign a JSON payload. Returns `<b64-payload>.<b64-hmac>`."""
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    return f"{_b64encode(body)}.{_b64encode(sig)}"


def verify_cookie(value: str, secret: str) -> Optional[dict]:
    """Verify HMAC and expiry. Returns payload dict or None on any failure."""
    try:
        payload_b64, sig_b64 = value.split(".", 1)
        body = _b64decode(payload_b64)
        sig = _b64decode(sig_b64)
        expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(body.decode("utf-8"))
        if not isinstance(payload, dict):
            return None
        exp = payload.get("exp")
        if not isinstance(exp, int) or exp <= int(time.time()):
            return None
        return payload
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None
