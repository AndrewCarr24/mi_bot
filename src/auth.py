"""Auth: cookie helpers, middleware, login/logout routes, rate limiter.

Single-shared-password gate. Cookie carries its own auth assertion
(HMAC of {"exp": ..., "v": 1}) — no server-side session store.
"""

from __future__ import annotations

import base64
import hmac
import hashlib
import json
import logging
import os
import time
from collections import defaultdict
from typing import Optional
from urllib.parse import quote

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse, RedirectResponse
from starlette.types import ASGIApp


logger = logging.getLogger(__name__)

# Jinja2 templates directory; resolved relative to the agent_fin/ root.
_TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
_templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


def _client_ip(request: Request) -> str:
    """Best-effort client IP. App Runner sets X-Forwarded-For."""
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _safe_next(value: str) -> str:
    """Allow only relative paths in the `next` redirect target.
    Anything with a scheme or netloc is rejected and falls back to '/'.
    """
    from urllib.parse import urlparse
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        return "/"
    return value or "/"


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


ALLOWLIST_EXACT = ("/health", "/login", "/logout")
ALLOWLIST_PREFIXES = ("/static/",)


def _is_allowlisted(path: str) -> bool:
    if path in ALLOWLIST_EXACT:
        return True
    return any(path.startswith(p) for p in ALLOWLIST_PREFIXES)


class AuthMiddleware(BaseHTTPMiddleware):
    """Cookie-gated middleware. Fail-closed if env not configured."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if _is_allowlisted(path):
            return await call_next(request)

        password = os.environ.get("AGENT_PASSWORD", "")
        secret = os.environ.get("COOKIE_SECRET", "")
        if not password or not secret:
            logger.error(
                "AuthMiddleware: AGENT_PASSWORD or COOKIE_SECRET not set; "
                "returning 503 for path=%s",
                path,
            )
            return PlainTextResponse(
                "auth not configured", status_code=503
            )

        cookie = request.cookies.get("agent_session")
        if cookie and verify_cookie(cookie, secret=secret) is not None:
            return await call_next(request)

        # Redirect to /login with the original path preserved.
        next_url = request.url.path
        if request.url.query:
            next_url = f"{next_url}?{request.url.query}"
        return RedirectResponse(
            f"/login?next={quote(next_url, safe='')}",
            status_code=302,
        )


def register_auth_routes(app: FastAPI) -> None:
    """Wire /login (GET+POST) and /logout onto the app."""

    @app.get("/login", response_class=HTMLResponse)
    async def login_form(request: Request):
        next_url = _safe_next(request.query_params.get("next", "/"))
        return _templates.TemplateResponse(
            request, "login.html", {"next": next_url, "error": None}
        )

    @app.post("/login")
    async def login_submit(
        request: Request,
        password: str = Form(...),
        next_url: str = Form("/", alias="next"),
    ):
        next_url = _safe_next(next_url)
        ip = _client_ip(request)
        if not _rate_limiter.check_and_record(ip):
            logger.warning(f"login rate limit hit for ip={ip}")
            return PlainTextResponse(
                "Too many attempts. Try again in a minute.",
                status_code=429,
            )

        expected = os.environ.get("AGENT_PASSWORD", "")
        secret = os.environ.get("COOKIE_SECRET", "")
        if not expected or not secret:
            logger.error("login_submit: AGENT_PASSWORD or COOKIE_SECRET not set; returning 503")
            return PlainTextResponse("auth not configured", status_code=503)

        if not hmac.compare_digest(password, expected):
            logger.warning("login failed for ip=%s", ip)
            return _templates.TemplateResponse(
                request,
                "login.html",
                {"next": next_url, "error": "Incorrect password."},
                status_code=200,
            )

        # Success: sign cookie + redirect.
        logger.info("login succeeded for ip=%s", ip)
        payload = {"exp": int(time.time()) + 30 * 86400, "v": 1}
        cookie_value = sign_cookie(payload, secret=secret)
        response = RedirectResponse(next_url, status_code=302)
        response.set_cookie(
            key="agent_session",
            value=cookie_value,
            max_age=30 * 86400,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        return response

    @app.get("/logout")
    async def logout():
        response = RedirectResponse("/login", status_code=302)
        response.delete_cookie("agent_session")
        return response
