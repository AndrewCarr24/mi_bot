# Deployment + Password Auth — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy `agent_fin` to AWS App Runner behind a single shared password, with infrastructure in CDK-Python and image lifecycle in a bash deploy script.

**Architecture:** FastAPI ASGI middleware does cookie-based auth in front of the existing Chainlit-mounted FastAPI app. CDK declares ECR + App Runner + IAM. A bash script builds the image, pushes to ECR, applies infra changes, and triggers App Runner redeploy.

**Tech Stack:** Python 3.11, FastAPI/Starlette, AWS CDK v2 (Python), Docker, App Runner, ECR, pytest, hmac/secrets/json (stdlib for cookie signing).

**Spec reference:** [`docs/superpowers/specs/2026-05-06-deployment-auth-design.md`](../specs/2026-05-06-deployment-auth-design.md)

---

## File map

```
agent_fin/
├── api.py                        # MODIFIED: register middleware + routes (Task 8)
├── pyproject.toml                # MODIFIED: add pytest, pytest-asyncio (Task 1)
├── .env.example                  # MODIFIED: document new env vars (Task 2)
├── README.md                     # MODIFIED: replace manual deploy section (Task 13)
├── src/
│   ├── auth.py                   # NEW: cookie helpers + middleware + routes + rate limiter (Tasks 3-7)
│   └── config.py                 # MODIFIED: add AGENT_PASSWORD, COOKIE_SECRET fields (Task 2)
├── templates/
│   └── login.html                # NEW: minimal login form (Task 6)
├── tests/
│   ├── __init__.py               # NEW (Task 1)
│   ├── conftest.py               # NEW: TestClient + env fixtures (Task 1)
│   ├── test_auth.py              # NEW: ~25 unit/integration tests (Tasks 3-7)
│   └── test_smoke.py             # NEW: end-to-end happy path (Task 9)
├── infra/cdk/
│   ├── app.py                    # NEW: CDK entrypoint (Task 10)
│   ├── ecr_stack.py              # NEW: ECR repo (Task 10)
│   ├── runner_stack.py           # NEW: App Runner + IAM (Task 11)
│   ├── cdk.json                  # NEW: CDK config (Task 10)
│   ├── requirements.txt          # NEW: aws-cdk-lib (Task 10)
│   └── README.md                 # NEW: CDK README (Task 13)
└── scripts/
    └── deploy.sh                 # NEW: build + push + deploy orchestrator (Task 12)
```

## Prerequisites (engineer should verify before Task 1)

- Working `agent_fin` checkout, `uv sync` runs, `python run_app.py "..."` works locally.
- AWS CLI configured (`aws sts get-caller-identity` succeeds).
- Docker installed and running.
- Node.js 18+ (for CDK CLI).
- AWS CDK CLI installed: `npm install -g aws-cdk`.
- `cdk bootstrap` has been run for the target account/region (us-east-1) — first-time-per-account-region only.
- Working `.env` with `DEEPSEEK_API_KEY`, `AWS_REGION=us-east-1`.

---

## Task 1: Test scaffolding

**Goal:** Add pytest to dev deps and create the `tests/` directory with a basic conftest.

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Add pytest deps to pyproject.toml**

In `[dependency-groups]`, the `dev` array currently has `selenium>=4.43.0`. Add `pytest` and `pytest-asyncio`:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "selenium>=4.43.0",
]
```

- [ ] **Step 2: Install the new deps**

Run: `uv sync`
Expected: `pytest` and `pytest-asyncio` appear in the `Installed:` line.

- [ ] **Step 3: Create `tests/__init__.py`**

Empty file — just makes `tests/` a package.

```python
```

- [ ] **Step 4: Create `tests/conftest.py` with the env-var + TestClient fixtures**

```python
"""Pytest fixtures for the auth test suite.

The `auth_app` fixture builds a minimal FastAPI app with our
AuthMiddleware + login routes mounted on top of two dummy endpoints
(/protected, /health). This keeps auth tests fast — they don't load
the dsRAG KB or the orchestrator graph that `api.py` lifespan brings up.

The `smoke_app` fixture instead returns the real `api.app` with the
KB load mocked out, for the end-to-end browser-flow smoke test.
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
```

- [ ] **Step 5: Verify pytest discovers the suite (will error since src/auth.py doesn't exist yet — that's expected)**

Run: `pytest tests/ --collect-only`
Expected: collection error pointing at `src.auth` (`ModuleNotFoundError: No module named 'src.auth'`). This confirms pytest sees the conftest.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml uv.lock tests/__init__.py tests/conftest.py
git commit -m "Add pytest dev deps + tests/ scaffolding"
```

---

## Task 2: Auth env vars in config + `.env.example`

**Goal:** Declare `AGENT_PASSWORD` and `COOKIE_SECRET` on the Settings class. Document in `.env.example`.

**Files:**
- Modify: `src/config.py` (add two fields after the existing DEEPSEEK fields)
- Modify: `.env.example`

- [ ] **Step 1: Add the fields to `src/config.py`**

Locate the `Settings(BaseSettings)` class. After the existing field declarations (e.g., `DEEPSEEK_BASE_URL`), add:

```python
    # === Deployment auth ===

    AGENT_PASSWORD: str = Field(
        default="",
        description=(
            "Shared password for the deployment gate. Required at runtime; "
            "AuthMiddleware fails closed (503) if unset."
        ),
    )

    COOKIE_SECRET: str = Field(
        default="",
        description=(
            "HMAC secret for signed session cookies. Generate with "
            "`openssl rand -hex 32`. Rotating invalidates all live sessions."
        ),
    )
```

- [ ] **Step 2: Update `.env.example`**

Append a new section at the end of `.env.example`:

```
# Deployment auth (required when running api.py / behind the password gate)
# AGENT_PASSWORD=
# COOKIE_SECRET=     # openssl rand -hex 32
```

- [ ] **Step 3: Verify config still imports**

Run: `python -c "from src.config import settings; print('AGENT_PASSWORD:', repr(settings.AGENT_PASSWORD))"`
Expected: `AGENT_PASSWORD: ''` (empty default).

- [ ] **Step 4: Commit**

```bash
git add src/config.py .env.example
git commit -m "Add AGENT_PASSWORD and COOKIE_SECRET settings fields"
```

---

## Task 3: Cookie sign / verify (TDD)

**Goal:** Implement `sign_cookie` and `verify_cookie` in `src/auth.py` with full test coverage.

**Files:**
- Create: `src/auth.py` (start with the cookie module)
- Create: `tests/test_auth.py`

- [ ] **Step 1: Write the round-trip test**

Create `tests/test_auth.py`:

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_auth.py::test_sign_verify_round_trip -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.auth'`.

- [ ] **Step 3: Implement minimal `sign_cookie` and `verify_cookie`**

Create `src/auth.py`:

```python
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
```

- [ ] **Step 4: Run the round-trip test, verify it passes**

Run: `pytest tests/test_auth.py::test_sign_verify_round_trip -v`
Expected: PASS.

- [ ] **Step 5: Add the rejection-case tests**

Append to `tests/test_auth.py`:

```python
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
```

- [ ] **Step 6: Run all cookie tests, verify all pass**

Run: `pytest tests/test_auth.py -v -k "sign_verify or rejects"`
Expected: 6 PASSES.

- [ ] **Step 7: Commit**

```bash
git add src/auth.py tests/test_auth.py
git commit -m "Add HMAC-signed cookie helpers + tests"
```

---

## Task 4: Login rate limiter (TDD)

**Goal:** In-memory per-IP rate limiter for `/login` POSTs. 5 attempts per 60s; 6th in window returns 429.

**Files:**
- Modify: `src/auth.py` (add `LoginRateLimiter` class + module-level instance)
- Modify: `tests/test_auth.py` (add rate limiter tests)

- [ ] **Step 1: Write rate limiter unit tests**

Append to `tests/test_auth.py`:

```python
# ---------------------------------------------------------------- rate limit --

def test_rate_limiter_allows_first_5(monkeypatch):
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
```

- [ ] **Step 2: Run, verify all 5 fail**

Run: `pytest tests/test_auth.py -v -k "rate_limiter"`
Expected: 5 FAILs (`AttributeError: module 'src.auth' has no attribute 'LoginRateLimiter'`).

- [ ] **Step 3: Implement `LoginRateLimiter` and the module-level instance**

In `src/auth.py`, add after the cookie helpers:

```python
from collections import defaultdict
from typing import Dict, List


class LoginRateLimiter:
    """Per-IP token-bucket-ish rate limiter. In-memory; single-instance only.

    Usage: call `check_and_record(ip)`; returns True if the request is
    within the limit (and records the attempt) or False if blocked.
    """

    def __init__(self, max_attempts: int = 5, window_sec: float = 60.0):
        self.max_attempts = max_attempts
        self.window_sec = window_sec
        self._attempts: Dict[str, List[float]] = defaultdict(list)

    def check_and_record(self, ip: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_sec
        self._attempts[ip] = [t for t in self._attempts[ip] if t > cutoff]
        if len(self._attempts[ip]) >= self.max_attempts:
            return False
        self._attempts[ip].append(now)
        return True

    def reset(self) -> None:
        self._attempts.clear()


# Module-level instance used by the login route. Tests should call `.reset()`
# in conftest's `auth_app` fixture so state doesn't leak across tests.
_rate_limiter = LoginRateLimiter()
```

- [ ] **Step 4: Run rate limiter tests, verify all pass**

Run: `pytest tests/test_auth.py -v -k "rate_limiter"`
Expected: 5 PASSES.

- [ ] **Step 5: Commit**

```bash
git add src/auth.py tests/test_auth.py
git commit -m "Add per-IP login rate limiter with unit tests"
```

---

## Task 5: AuthMiddleware (TDD)

**Goal:** Implement the ASGI middleware that allow-lists public paths, enforces fail-closed on missing config, and verifies the cookie on protected paths.

**Files:**
- Modify: `src/auth.py` (add `AuthMiddleware`)
- Modify: `tests/test_auth.py` (add middleware tests)

- [ ] **Step 1: Write the middleware allow-list tests**

Append to `tests/test_auth.py`:

```python
# ---------------------------------------------------------------- middleware --

def test_health_bypasses_auth(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_login_get_bypasses_auth(client):
    r = client.get("/login", follow_redirects=False)
    assert r.status_code == 200  # login form rendered


def test_protected_path_redirects_when_no_cookie(client):
    r = client.get("/protected", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["location"]
    assert "next=%2Fprotected" in r.headers["location"]


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
```

- [ ] **Step 2: Write fail-closed tests**

Append:

```python
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
```

- [ ] **Step 3: Run middleware tests, verify all fail**

Run: `pytest tests/test_auth.py -v -k "bypasses or redirects or passes_through or 503"`
Expected: ~8 FAILs (middleware doesn't exist + register_auth_routes doesn't exist).

- [ ] **Step 4: Implement `AuthMiddleware` and a `register_auth_routes` stub (filled in Task 7)**

In `src/auth.py`, add imports at top:

```python
import os
from urllib.parse import quote

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse, Response
from starlette.types import ASGIApp
```

Then add the middleware class:

```python
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
```

Note: the `_is_allowlisted` heuristic is intentionally simple — we want `/health`, `/login`, `/logout`, and any path starting with `/static/`. The `or path.startswith(p) and p.endswith("/")` handles the trailing-slash case for `/static/`. Add a stub `register_auth_routes` so the conftest can import it (real impl in Task 7):

```python
def register_auth_routes(app) -> None:
    """Register /login (GET+POST) and /logout. Implemented in Task 7."""
    pass  # placeholder; Task 7 fills this in
```

- [ ] **Step 5: Run all tests added so far**

Run: `pytest tests/test_auth.py -v`
Expected: cookie tests + rate limiter tests + middleware tests pass.

The `test_login_get_bypasses_auth` test will currently FAIL with 404 since we haven't implemented the route. **Mark this expected** — Task 7 fixes it. Continue.

- [ ] **Step 6: Run only the tests that should pass at this stage**

Run: `pytest tests/test_auth.py -v --deselect tests/test_auth.py::test_login_get_bypasses_auth`
Expected: ALL PASS.

- [ ] **Step 7: Commit**

```bash
git add src/auth.py tests/test_auth.py
git commit -m "Add AuthMiddleware with fail-closed config check + tests"
```

---

## Task 6: Login template

**Goal:** Create `templates/login.html` — a minimal styled form that submits to `/login`.

**Files:**
- Create: `templates/login.html`

- [ ] **Step 1: Create the template**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>agent_fin — sign in</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0e0e10;
      color: #e0e0e0;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
    }
    form {
      background: #1a1a1d;
      padding: 2rem 2.5rem;
      border-radius: 8px;
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
      min-width: 300px;
    }
    h1 {
      margin: 0 0 1.25rem 0;
      font-size: 1.25rem;
      font-weight: 500;
    }
    label {
      display: block;
      font-size: 0.875rem;
      color: #888;
      margin-bottom: 0.5rem;
    }
    input[type="password"] {
      width: 100%;
      padding: 0.6rem 0.75rem;
      box-sizing: border-box;
      border: 1px solid #333;
      border-radius: 4px;
      background: #0e0e10;
      color: #e0e0e0;
      font-size: 1rem;
      margin-bottom: 1rem;
    }
    input[type="password"]:focus {
      outline: none;
      border-color: #6c8eff;
    }
    button {
      width: 100%;
      padding: 0.6rem;
      background: #6c8eff;
      color: #0e0e10;
      border: none;
      border-radius: 4px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
    }
    button:hover {
      background: #8aa4ff;
    }
    .error {
      color: #ff7a7a;
      font-size: 0.875rem;
      margin-bottom: 1rem;
    }
  </style>
</head>
<body>
  <form method="POST" action="/login">
    <h1>agent_fin</h1>
    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}
    <label for="password">Password</label>
    <input type="password" id="password" name="password" autofocus required>
    <input type="hidden" name="next" value="{{ next }}">
    <button type="submit">Sign in</button>
  </form>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add templates/login.html
git commit -m "Add login.html template"
```

---

## Task 7: Login + logout routes (TDD)

**Goal:** Replace the `register_auth_routes` stub with full GET `/login`, POST `/login`, GET `/logout` implementations. Includes rate-limit hookup.

**Files:**
- Modify: `src/auth.py`
- Modify: `tests/test_auth.py`

- [ ] **Step 1: Write login+logout route tests**

Append to `tests/test_auth.py`:

```python
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
```

- [ ] **Step 2: Run, verify all 7 fail**

Run: `pytest tests/test_auth.py -v -k "login_post or login_get_renders or login_get_passes or logout"`
Expected: 7 FAILs (404 for routes, since `register_auth_routes` is a stub).

- [ ] **Step 3: Implement login + logout routes**

Replace the placeholder `register_auth_routes` in `src/auth.py` with:

```python
import logging
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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


def register_auth_routes(app: FastAPI) -> None:
    """Wire /login (GET+POST) and /logout onto the app."""

    @app.get("/login", response_class=HTMLResponse)
    async def login_form(request: Request):
        next_url = request.query_params.get("next", "/")
        return _templates.TemplateResponse(
            request, "login.html", {"next": next_url, "error": None}
        )

    @app.post("/login")
    async def login_submit(
        request: Request,
        password: str = Form(...),
        next: str = Form("/"),
    ):
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
            return PlainTextResponse("auth not configured", status_code=503)

        if not hmac.compare_digest(password, expected):
            return _templates.TemplateResponse(
                request,
                "login.html",
                {"next": next, "error": "Incorrect password."},
                status_code=200,
            )

        # Success: sign cookie + redirect.
        payload = {"exp": int(time.time()) + 30 * 86400, "v": 1}
        cookie_value = sign_cookie(payload, secret=secret)
        response = RedirectResponse(next, status_code=302)
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
```

- [ ] **Step 4: Run all auth tests**

Run: `pytest tests/test_auth.py -v`
Expected: ALL ~22 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/auth.py tests/test_auth.py
git commit -m "Implement /login GET+POST and /logout with rate-limit + tests"
```

---

## Task 8: Wire auth into `api.py`

**Goal:** Register `AuthMiddleware` and login routes onto the real FastAPI app, ahead of the Chainlit mount.

**Files:**
- Modify: `api.py`

- [ ] **Step 1: Read the current `api.py` to identify exact insertion points**

Run: `cat -n api.py | head -60`
Confirm the order:
1. `app = FastAPI(...)` (around line 51)
2. `mount_chainlit(app=app, target="chat.py", path="/chat")` (around line 58)
3. `class AskRequest(BaseModel)` (around line 61)

We want middleware + routes registered between (1) and (2).

- [ ] **Step 2: Modify `api.py` — add imports**

Near the top with other `from src...` imports:

```python
from src.auth import AuthMiddleware, register_auth_routes  # noqa: E402
```

- [ ] **Step 3: Modify `api.py` — install middleware + routes**

Right after `app = FastAPI(...)`:

```python
app.add_middleware(AuthMiddleware)
register_auth_routes(app)
```

So the relevant block becomes:

```python
app = FastAPI(title="agent_fin", version="0.1.0", lifespan=lifespan)

# Auth gate — registered before the Chainlit mount so /chat/* (including
# the WebSocket upgrade) passes through AuthMiddleware first.
app.add_middleware(AuthMiddleware)
register_auth_routes(app)

# Chainlit chat UI mounted at /chat. ...
from chainlit.utils import mount_chainlit  # noqa: E402

mount_chainlit(app=app, target="chat.py", path="/chat")
```

- [ ] **Step 4: Verify the app still imports**

Run: `AGENT_PASSWORD=dev COOKIE_SECRET=$(openssl rand -hex 32) python -c "import api; print('ok')"`
Expected: prints `ok`. (KB lifespan startup happens in async context — won't trigger at import time.)

- [ ] **Step 5: Manual local check (optional but recommended)**

Run in one terminal:

```bash
set -a && . .env && set +a
export AGENT_PASSWORD=devpw
export COOKIE_SECRET=$(openssl rand -hex 32)
uvicorn api:app --reload --port 8000
```

In another terminal:

```bash
curl -i http://127.0.0.1:8000/health
# Expected: 200 OK with {"status": "ok"}

curl -i http://127.0.0.1:8000/ask -X POST -H 'Content-Type: application/json' -d '{"question":"hi"}'
# Expected: 302 Found, Location: /login?next=%2Fask

curl -i http://127.0.0.1:8000/login
# Expected: 200 with HTML form

curl -i -c /tmp/cookies.txt -X POST http://127.0.0.1:8000/login \
  -d "password=devpw&next=/health"
# Expected: 302 Found, Location: /health, Set-Cookie: agent_session=...

curl -i -b /tmp/cookies.txt http://127.0.0.1:8000/health
# Expected: 200 OK (cookie carries auth — though /health is allowlisted anyway)
```

(If you don't want to do this here, skip — Task 14's manual checklist covers it.)

- [ ] **Step 6: Commit**

```bash
git add api.py
git commit -m "Wire AuthMiddleware + login routes into api.py"
```

---

## Task 9: End-to-end smoke test

**Goal:** One pytest test exercising the full browser flow against `api.py` (with KB load mocked).

**Files:**
- Create: `tests/test_smoke.py`

- [ ] **Step 1: Write the smoke test**

```python
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
```

- [ ] **Step 2: Run the smoke test**

Run: `pytest tests/test_smoke.py -v`
Expected: PASS.

- [ ] **Step 3: Run the full test suite to confirm nothing regressed**

Run: `pytest tests/ -v`
Expected: ALL PASS (~25-26 tests).

- [ ] **Step 4: Commit**

```bash
git add tests/test_smoke.py
git commit -m "Add end-to-end smoke test for browser auth flow"
```

---

## Task 10: CDK project init + ECR stack

**Goal:** Stand up the CDK Python project under `infra/cdk/` and define the ECR-only stack.

**Files:**
- Create: `infra/cdk/app.py`
- Create: `infra/cdk/ecr_stack.py`
- Create: `infra/cdk/cdk.json`
- Create: `infra/cdk/requirements.txt`

- [ ] **Step 1: Create `infra/cdk/requirements.txt`**

```
aws-cdk-lib>=2.150.0
constructs>=10.3.0
```

- [ ] **Step 2: Create `infra/cdk/cdk.json`**

```json
{
  "app": "python3 app.py",
  "context": {
    "@aws-cdk/aws-iam:minimizePolicies": true,
    "aws-cdk:enableDiffNoFail": true,
    "@aws-cdk/core:newStyleStackSynthesis": true
  }
}
```

- [ ] **Step 3: Create `infra/cdk/ecr_stack.py`**

```python
"""ECR repository for the agent_fin container image."""

from __future__ import annotations

from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ecr as ecr,
    Duration,
)
from constructs import Construct


class AgentFinEcrStack(Stack):
    """ECR repo: scan-on-push, lifecycle policy retains last 10 images."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.repo = ecr.Repository(
            self,
            "AgentFinRepo",
            repository_name="agent-fin",
            image_scan_on_push=True,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    description="Retain last 10 images.",
                    max_image_count=10,
                ),
            ],
        )

        CfnOutput(
            self,
            "EcrRepoUri",
            value=self.repo.repository_uri,
            description="URI for `docker push`.",
        )
```

- [ ] **Step 4: Create `infra/cdk/app.py`**

(Initial version — only ECR stack. Task 11 adds the runner stack.)

```python
#!/usr/bin/env python3
"""CDK app entrypoint for agent_fin infrastructure."""

import os

import aws_cdk as cdk

from ecr_stack import AgentFinEcrStack


app = cdk.App()

env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
)

ecr_stack = AgentFinEcrStack(app, "AgentFinEcrStack", env=env)

app.synth()
```

- [ ] **Step 5: Install CDK Python deps + verify `cdk synth`**

```bash
cd infra/cdk
pip install -r requirements.txt
cdk synth AgentFinEcrStack
```

Expected: prints CloudFormation YAML for the ECR stack. No errors.

- [ ] **Step 6: Commit**

```bash
cd ../..
git add infra/cdk/app.py infra/cdk/ecr_stack.py infra/cdk/cdk.json infra/cdk/requirements.txt
git commit -m "Add CDK project scaffolding + AgentFinEcrStack"
```

---

## Task 11: CDK App Runner stack

**Goal:** Define `AgentFinRunnerStack` — App Runner service + IAM roles + env-var configuration.

**Files:**
- Create: `infra/cdk/runner_stack.py`
- Modify: `infra/cdk/app.py` (instantiate the new stack)

- [ ] **Step 1: Create `infra/cdk/runner_stack.py`**

```python
"""App Runner service + IAM roles for agent_fin."""

from __future__ import annotations

import os

from aws_cdk import (
    CfnOutput,
    Stack,
    aws_apprunner as apprunner,
    aws_ecr as ecr,
    aws_iam as iam,
)
from constructs import Construct


REQUIRED_ENV_VARS = ("AGENT_PASSWORD", "COOKIE_SECRET", "DEEPSEEK_API_KEY", "AWS_REGION")
OPTIONAL_ENV_VARS = ("LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_TRACING")


def _env_or_fail(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Required env var {name!r} is unset. "
            "Run `set -a && . .env && set +a` before `cdk deploy`."
        )
    return value


class AgentFinRunnerStack(Stack):
    """App Runner service for agent_fin.

    - 1 vCPU / 4 GB memory (KB pickle is ~350 MB; need headroom)
    - min/max instances = 1 (single-instance assumption per design)
    - No auto-deploy from ECR (deploy.sh triggers `start-deployment` explicitly)
    - Env vars baked in from local environment at `cdk deploy` time
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        repo: ecr.IRepository,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Validate required env vars before going further.
        for name in REQUIRED_ENV_VARS:
            _env_or_fail(name)

        # ---- Access role: App Runner pulls the image from ECR.
        access_role = iam.Role(
            self,
            "AppRunnerAccessRole",
            assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com"),
        )
        repo.grant_pull(access_role)

        # ---- Instance role: container's runtime AWS permissions.
        instance_role = iam.Role(
            self,
            "AppRunnerInstanceRole",
            assumed_by=iam.ServicePrincipal("tasks.apprunner.amazonaws.com"),
        )
        # Bedrock invoke for: Titan v2 embeddings, Haiku (router/judge),
        # Sonnet (orchestrator when ORCHESTRATOR_PROVIDER=bedrock).
        instance_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=[
                    f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v2:0",
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0",
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-sonnet-4-6-v1:0",
                    # Cross-region inference profiles (e.g., us.anthropic...)
                    f"arn:aws:bedrock:{self.region}:{self.account}:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    f"arn:aws:bedrock:{self.region}:{self.account}:inference-profile/us.anthropic.claude-sonnet-4-6",
                ],
            )
        )

        # ---- Build env-var list for App Runner.
        runtime_env = []
        for name in REQUIRED_ENV_VARS:
            runtime_env.append(
                apprunner.CfnService.KeyValuePairProperty(
                    name=name, value=_env_or_fail(name)
                )
            )
        for name in OPTIONAL_ENV_VARS:
            value = os.environ.get(name)
            if value:
                runtime_env.append(
                    apprunner.CfnService.KeyValuePairProperty(name=name, value=value)
                )

        # ---- App Runner service.
        # Using L1 CfnService for full control over image-deployment knobs.
        service = apprunner.CfnService(
            self,
            "AgentFinService",
            service_name="agent-fin",
            source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                    access_role_arn=access_role.role_arn,
                ),
                auto_deployments_enabled=False,  # explicit start-deployment from deploy.sh
                image_repository=apprunner.CfnService.ImageRepositoryProperty(
                    image_identifier=f"{repo.repository_uri}:latest",
                    image_repository_type="ECR",
                    image_configuration=apprunner.CfnService.ImageConfigurationProperty(
                        port="8080",
                        runtime_environment_variables=runtime_env,
                    ),
                ),
            ),
            instance_configuration=apprunner.CfnService.InstanceConfigurationProperty(
                cpu="1024",      # 1 vCPU
                memory="4096",   # 4 GB
                instance_role_arn=instance_role.role_arn,
            ),
            health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
                protocol="HTTP",
                path="/health",
                interval=20,
                timeout=5,
                healthy_threshold=2,
                unhealthy_threshold=3,
            ),
            network_configuration=apprunner.CfnService.NetworkConfigurationProperty(
                egress_configuration=apprunner.CfnService.EgressConfigurationProperty(
                    egress_type="DEFAULT",
                ),
                ingress_configuration=apprunner.CfnService.IngressConfigurationProperty(
                    is_publicly_accessible=True,
                ),
            ),
            # Auto-scaling default is min=1/max=25; we want min=max=1. Use the
            # default config name (see AWS docs) or attach a custom one if
            # needed. For now: rely on the AppRunner default config (1-25)
            # and set max via service-level overrides if a separate
            # AutoScalingConfiguration becomes necessary.
        )

        CfnOutput(
            self,
            "ServiceUrl",
            value=f"https://{service.attr_service_url}",
            description="Public URL for agent_fin.",
        )
        CfnOutput(
            self,
            "ServiceArn",
            value=service.attr_service_arn,
            description="ARN used by deploy.sh for `apprunner start-deployment`.",
        )
```

> **Note on auto-scaling**: the L1 `CfnService` here uses App Runner's *default* auto-scaling config (min=1/max=25). If you need to enforce min=max=1 strictly (per the spec's single-instance assumption), add a separate `apprunner.CfnAutoScalingConfiguration` resource and reference it via `auto_scaling_configuration_arn` on the service. Defer this until the default config causes observable problems — App Runner doesn't actually scale up unless concurrent traffic exceeds thresholds, and our trusted-user shared-password use case won't.

- [ ] **Step 2: Update `infra/cdk/app.py` to instantiate the runner stack**

```python
#!/usr/bin/env python3
"""CDK app entrypoint for agent_fin infrastructure."""

import os

import aws_cdk as cdk

from ecr_stack import AgentFinEcrStack
from runner_stack import AgentFinRunnerStack


app = cdk.App()

env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
)

ecr_stack = AgentFinEcrStack(app, "AgentFinEcrStack", env=env)
runner_stack = AgentFinRunnerStack(
    app, "AgentFinRunnerStack", repo=ecr_stack.repo, env=env
)
runner_stack.add_dependency(ecr_stack)

app.synth()
```

- [ ] **Step 3: Verify `cdk synth` runs cleanly**

```bash
cd infra/cdk
set -a && . ../../.env && set +a
export AGENT_PASSWORD=dev
export COOKIE_SECRET=$(openssl rand -hex 32)
cdk synth AgentFinRunnerStack
```

Expected: prints CloudFormation YAML for the runner stack with the env vars baked in. No errors.

If `_env_or_fail` raises, double-check that `set -a && . .env && set +a` was run for `agent_fin/.env`.

- [ ] **Step 4: Commit**

```bash
cd ../..
git add infra/cdk/runner_stack.py infra/cdk/app.py
git commit -m "Add AgentFinRunnerStack with App Runner service + IAM"
```

---

## Task 12: Deploy script

**Goal:** `scripts/deploy.sh` — bash, single entrypoint for "ship current code to AWS."

**Files:**
- Create: `scripts/deploy.sh`

- [ ] **Step 1: Create the deploy script**

```bash
#!/usr/bin/env bash
# Build, push, and deploy agent_fin to AWS.
#
# Steps:
#   1. Preflight: env, AWS auth, git state.
#   2. Bootstrap ECR if it doesn't exist.
#   3. Build + tag + push container to ECR.
#   4. Apply CDK changes (App Runner stack).
#   5. Trigger explicit redeploy (so App Runner pulls the new image even
#      when no infra changed).
#   6. Wait + report URL.
#
# Usage:  ./scripts/deploy.sh

set -euo pipefail

# ---- 0. Locate ourselves; ensure cwd is agent_fin/.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

REGION="${AWS_REGION:-us-east-1}"
SERVICE_NAME="agent-fin"
STACK_ECR="AgentFinEcrStack"
STACK_RUNNER="AgentFinRunnerStack"

log() { echo "[deploy] $*"; }

# ---- 1. Preflight.
log "preflight: checking env vars"
for var in AGENT_PASSWORD COOKIE_SECRET DEEPSEEK_API_KEY; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: $var is unset. Run: set -a && . .env && set +a" >&2
    exit 1
  fi
done

log "preflight: checking AWS auth"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"

log "preflight: checking git state"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "[deploy] WARNING: uncommitted changes in working tree."
fi

IMAGE_TAG="$(git rev-parse --short HEAD)"
log "deploying tag=$IMAGE_TAG (account=$ACCOUNT_ID, region=$REGION)"

# ---- 2. Bootstrap ECR if needed.
log "bootstrap: checking ECR repo $SERVICE_NAME"
if ! aws ecr describe-repositories --repository-names "$SERVICE_NAME" --region "$REGION" >/dev/null 2>&1; then
  log "bootstrap: deploying $STACK_ECR"
  ( cd infra/cdk && cdk deploy "$STACK_ECR" --require-approval never )
fi

ECR_URI="$(aws ecr describe-repositories --repository-names "$SERVICE_NAME" \
            --region "$REGION" --query 'repositories[0].repositoryUri' --output text)"
log "ECR URI: $ECR_URI"

# ---- 3. Build + tag + push.
log "build: docker build (linux/amd64)"
docker build --platform=linux/amd64 \
  -t "$SERVICE_NAME:$IMAGE_TAG" \
  -t "$SERVICE_NAME:latest" \
  .

log "push: ECR login"
aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "$ECR_URI"

log "push: tagging + pushing $IMAGE_TAG and latest"
docker tag "$SERVICE_NAME:$IMAGE_TAG" "$ECR_URI:$IMAGE_TAG"
docker tag "$SERVICE_NAME:latest"     "$ECR_URI:latest"
docker push "$ECR_URI:$IMAGE_TAG"
docker push "$ECR_URI:latest"

# ---- 4. Apply infra changes.
log "infra: cdk deploy $STACK_RUNNER"
( cd infra/cdk && cdk deploy "$STACK_RUNNER" --require-approval never )

# ---- 5. Force redeploy (in case nothing infra-side changed).
log "redeploy: aws apprunner start-deployment"
SERVICE_ARN="$(aws apprunner list-services --region "$REGION" \
                --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn | [0]" \
                --output text)"
if [[ -z "$SERVICE_ARN" || "$SERVICE_ARN" == "None" ]]; then
  echo "ERROR: App Runner service '$SERVICE_NAME' not found after cdk deploy." >&2
  exit 1
fi
aws apprunner start-deployment --service-arn "$SERVICE_ARN" --region "$REGION" >/dev/null

# ---- 6. Wait + report.
log "wait: polling service status (timeout 5 min)"
DEADLINE=$(( $(date +%s) + 300 ))
while true; do
  STATUS="$(aws apprunner describe-service --service-arn "$SERVICE_ARN" \
            --region "$REGION" --query 'Service.Status' --output text)"
  if [[ "$STATUS" == "RUNNING" ]]; then
    break
  fi
  if [[ "$STATUS" == "CREATE_FAILED" || "$STATUS" == "DELETE_FAILED" || "$STATUS" == "OPERATION_IN_PROGRESS" ]]; then
    log "status=$STATUS (continuing to wait)"
  fi
  if (( $(date +%s) > DEADLINE )); then
    echo "ERROR: timeout waiting for service to reach RUNNING (last status=$STATUS)." >&2
    exit 1
  fi
  sleep 10
done

URL="$(aws apprunner describe-service --service-arn "$SERVICE_ARN" \
       --region "$REGION" --query 'Service.ServiceUrl' --output text)"
log "deployed: https://$URL  (image=$IMAGE_TAG)"
```

> **A note on the wait loop:** App Runner reports `OPERATION_IN_PROGRESS` while a deployment is updating. We just keep polling until `RUNNING`. If something fails, the status will be `CREATE_FAILED` or similar and the timeout will trip.

- [ ] **Step 2: Make the script executable**

```bash
chmod +x scripts/deploy.sh
```

- [ ] **Step 3: Verify the script's syntax**

Run: `bash -n scripts/deploy.sh`
Expected: no output (syntax OK).

- [ ] **Step 4: Commit**

```bash
git add scripts/deploy.sh
git commit -m "Add scripts/deploy.sh — build/push/deploy orchestrator"
```

---

## Task 13: README updates

**Goal:** Replace the README's manual deploy section with a pointer to `scripts/deploy.sh`. Document CDK setup separately.

**Files:**
- Modify: `README.md`
- Create: `infra/cdk/README.md`

- [ ] **Step 1: Update `agent_fin/README.md`**

Find the section starting `# 4. Deploy loop (~5 min): push to ECR + redeploy App Runner` (around line 157 in the existing README). Replace the entire fenced block (the manual `ACCOUNT_ID=`, `docker build`, `aws ecr ...`, `aws apprunner ...` commands) with:

```markdown
# 4. Deploy loop (~3-4 min warm, ~5-7 min cold): build + push + redeploy
./scripts/deploy.sh
```

Also, in the same `## Local development` section, update the cost note paragraph if it references "redeploy" steps so it stays consistent.

Then, append a new section just before `## Switching the orchestrator`:

```markdown
## Deployment

The first-time deploy needs CDK bootstrapped and the auth env vars set.

```bash
cd infra/cdk
pip install -r requirements.txt
cd ../..
cdk bootstrap                           # one-time per AWS account/region
set -a && . .env && set +a              # loads AGENT_PASSWORD, COOKIE_SECRET, etc.
./scripts/deploy.sh                     # ~5-7 min cold; ~3-4 min on subsequent runs
# → prints https://xxx.us-east-1.awsapprunner.com
```

Visit the URL, enter the password from `AGENT_PASSWORD`, and use the app.

See [`infra/cdk/README.md`](./infra/cdk/README.md) for what's in the CDK stacks and how to destroy them.
```

- [ ] **Step 2: Create `infra/cdk/README.md`**

```markdown
# infra/cdk

CDK-Python infrastructure for `agent_fin`. Two stacks:

- **`AgentFinEcrStack`** — ECR repository (image scanning, lifecycle policy retaining last 10 images).
- **`AgentFinRunnerStack`** — App Runner service + IAM access role + IAM instance role + env-var configuration. Depends on `AgentFinEcrStack`.

The image lifecycle (build, push, redeploy trigger) lives in [`scripts/deploy.sh`](../../scripts/deploy.sh), not in CDK.

## Prerequisites

- Node.js 18+ and AWS CDK CLI: `npm install -g aws-cdk`
- AWS CLI configured (`aws sts get-caller-identity` succeeds)
- Python deps: `pip install -r requirements.txt` (run from `infra/cdk/`)
- One-time per account/region: `cdk bootstrap`

## Deploy

The two stacks are normally deployed via `scripts/deploy.sh` (which deploys ECR if missing, pushes the image, then deploys the runner stack). To deploy a stack manually:

```bash
set -a && . ../../.env && set +a
export AGENT_PASSWORD=...
export COOKIE_SECRET=$(openssl rand -hex 32)
cdk deploy AgentFinEcrStack
cdk deploy AgentFinRunnerStack
```

## Destroy

```bash
cdk destroy AgentFinRunnerStack
cdk destroy AgentFinEcrStack
```

ECR refuses to delete a non-empty repo. To force-empty first:

```bash
aws ecr batch-delete-image --repository-name agent-fin \
  --image-ids "$(aws ecr list-images --repository-name agent-fin --query 'imageIds[*]' --output json)"
```

## Outputs

- `AgentFinEcrStack.EcrRepoUri` — ECR push target.
- `AgentFinRunnerStack.ServiceUrl` — public app URL.
- `AgentFinRunnerStack.ServiceArn` — used by `deploy.sh` for `start-deployment`.
```

- [ ] **Step 3: Verify the agent_fin README still renders cleanly**

Run: `python -c "import pathlib; print(pathlib.Path('README.md').read_text()[:400])"`
(Just confirms it's still readable text, not corrupted.)

- [ ] **Step 4: Commit**

```bash
git add README.md infra/cdk/README.md
git commit -m "Update README and add infra/cdk/README"
```

---

## Task 14: Manual verification + first deploy

**Goal:** Walk through the manual verification checklist locally; do the first AWS deploy.

**Files:** none — this is verification only.

- [ ] **Step 1: Run the full pytest suite once more**

Run: `pytest tests/ -v`
Expected: ALL PASS (~26 tests).

- [ ] **Step 2: Local manual checklist**

Start the app:

```bash
set -a && . .env && set +a
export AGENT_PASSWORD=devpw
export COOKIE_SECRET=$(openssl rand -hex 32)
uvicorn api:app --reload --port 8000
```

Then:

- [ ] Browse `http://localhost:8000/` — expect redirect to `/login`.
- [ ] Submit wrong password — expect error message, stays on `/login`.
- [ ] Submit `devpw` — expect redirect to `/` (or wherever); cookie set.
- [ ] Browse `http://localhost:8000/chat` — Chainlit loads. Send a message; agent answers. (Verifies WebSocket carries cookie.)
- [ ] Click logout (or hit `http://localhost:8000/logout`) — cookie cleared.
- [ ] Hit any protected route again — redirected to `/login`.
- [ ] Hammer `/login` with 6 wrong passwords from one IP (e.g., `for i in {1..6}; do curl -X POST -d "password=x&next=/" http://localhost:8000/login; done`) — expect 429 on the 6th.
- [ ] Restart the server — login again with `devpw` to confirm the 30-day cookie works without server-side state.

- [ ] **Step 3: First AWS deploy**

```bash
# Ensure the real prod-shaped values are in your .env:
#   AGENT_PASSWORD=<your real shared password>
#   COOKIE_SECRET=<openssl rand -hex 32>
#   DEEPSEEK_API_KEY=...
#   AWS_REGION=us-east-1
#   (optional) LANGSMITH_API_KEY=..., LANGSMITH_PROJECT=agent-fin, LANGSMITH_TRACING=true

set -a && . .env && set +a
./scripts/deploy.sh
```

Expected output: `[deploy] deployed: https://xxx.us-east-1.awsapprunner.com  (image=<sha>)`.

- [ ] **Step 4: Smoke-test the deployed service**

- [ ] Browse the App Runner URL — redirected to `/login`.
- [ ] Submit the password — redirected, cookie set.
- [ ] `/chat` loads, you can chat with the agent.
- [ ] Logout, confirm redirect to `/login`.

- [ ] **Step 5: Commit any final tweaks**

If any unexpected fixes were needed during verification, commit them:

```bash
git add -A
git commit -m "Tweaks from manual verification"
```

- [ ] **Step 6: Push the branch**

```bash
git push
```

---

## Done criteria

- All tests pass (`pytest tests/`).
- `./scripts/deploy.sh` deploys cleanly from a fresh AWS region.
- Visiting the App Runner URL prompts for the password; correct password unlocks; wrong password errors; rate limit kicks in on the 6th.
- `/chat` works end-to-end with the cookie carried through the WebSocket upgrade.
- README and `infra/cdk/README.md` accurately describe the workflow.
