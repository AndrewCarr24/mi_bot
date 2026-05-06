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
from collections import defaultdict
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


class LoginRateLimiter:
    """Per-IP sliding-window rate limiter. In-memory; single-instance only.

    Usage: call `check_and_record(ip)`; returns True if the request is
    within the limit (and records the attempt) or False if blocked.
    """

    def __init__(self, max_attempts: int = 5, window_sec: float = 60.0):
        self.max_attempts = max_attempts
        self.window_sec = window_sec
        self._attempts: dict[str, list[float]] = defaultdict(list)

    def check_and_record(self, ip: str) -> bool:
        # Check and record execute atomically — callers must not split them
        # with `await` between the two operations.
        now = time.monotonic()
        cutoff = now - self.window_sec
        recent = [t for t in self._attempts[ip] if t > cutoff]
        if not recent:
            # Drop the dict entry entirely so silent IPs don't accumulate.
            del self._attempts[ip]
            recent = []
        if len(recent) >= self.max_attempts:
            self._attempts[ip] = recent
            return False
        recent.append(now)
        self._attempts[ip] = recent
        return True

    def reset(self) -> None:
        self._attempts.clear()


# Module-level instance used by the login route. Tests should call `.reset()`
# in conftest's `auth_app` fixture so state doesn't leak across tests.
_rate_limiter = LoginRateLimiter()
