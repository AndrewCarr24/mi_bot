# Deployment + Password Auth — Design

**Date:** 2026-05-06
**Status:** Design (pre-implementation)
**Owner:** Andrew Carr
**Skill flow:** brainstorming → writing-plans → executing-plans

## Problem

`agent_fin` runs locally and has been pushed to ECR once but is not currently a live HTTP service. The goal of this project is to deploy it to AWS so a small group of trusted people (anyone with a password) can use it — keeping the DeepSeek v4-flash orchestrator for cost reasons. Sessions and accuracy improvements are separate downstream projects (already scoped in the brainstorming session); they are out of scope here.

## Decisions

| # | Question | Choice |
|---|---|---|
| 1 | Auth model | Single shared password I distribute to trusted users. No accounts, no signup. |
| 2 | Auth mechanism | Custom `/login` page → HMAC-signed HTTP-only cookie. |
| 3 | Password storage | Plain env var on App Runner (matches existing `DEEPSEEK_API_KEY` pattern). Migrate to Secrets Manager only when ops friction justifies it. |
| 4 | IaC | AWS CDK in Python (`infra/cdk/`) for App Runner + ECR + IAM. |
| 5 | Image lifecycle | `scripts/deploy.sh` (bash) handles `docker build` → ECR push → App Runner redeploy. CDK declares the *destination*; the script *delivers* artifacts. |

**Defaults accepted without further debate:** App Runner as the host, App Runner default URL (`*.awsapprunner.com`), 30-day cookie lifetime, in-memory rate limit on `/login` (5 attempts/IP/min), HTTPS auto-provided by App Runner, single-instance deploy (min 1 / max 1).

## Architecture

Three tiers, two repos of code.

1. **AWS App Runner** hosts the existing FastAPI app (`api.py`), now wrapped in an auth middleware, plus the mounted Chainlit subapp at `/chat`. Container image lives in ECR.
2. **IaC stack at `infra/cdk/`** (CDK-Python). Declares: ECR repo, App Runner service, IAM roles, env-var configuration. `cdk deploy` creates/updates AWS resources.
3. **Deploy script at `scripts/deploy.sh`**. Bash. `docker build` → ECR push → App Runner image bump. Replaces the README's manual deploy loop.

### Request flow

1. Browser hits any URL on the App Runner endpoint.
2. `AuthMiddleware` on the FastAPI parent app intercepts before route dispatch.
3. Path allow-list passes through with no auth: `/health`, `/login` (GET + POST), `/logout`, `/static/*`.
4. Anything else: middleware verifies the signed cookie. If valid → request proceeds to `/ask`, `/chat`, etc. If invalid/missing → 302 redirect to `/login?next=<original-path>`.
5. `/login` POST: constant-time compare against `AGENT_PASSWORD` env var, sets HTTP-only signed cookie (30-day expiry), redirects to `next`.
6. `/logout`: clears the cookie, redirects to `/login`.

### Statelessness

The cookie carries its own auth assertion (HMAC of `{"exp": <unix_ts>, "v": 1}` using `COOKIE_SECRET`). No session DB, no in-memory cache. Multiple instances would all accept the same cookie. Logout is local-cookie-clearing only — no server-side revocation. Acceptable for the trusted-user shared-password model.

### Env vars on App Runner (set via CDK from local environment at deploy time)

- `AGENT_PASSWORD` — shared password
- `COOKIE_SECRET` — random 32+ byte hex string for HMAC (`openssl rand -hex 32`); regenerate to invalidate all live sessions
- `DEEPSEEK_API_KEY`, `LANGSMITH_API_KEY` (optional), `LANGSMITH_PROJECT` (optional), `LANGSMITH_TRACING` (optional), `AWS_REGION`

## Auth implementation

### File layout

```
agent_fin/
├── api.py                  (modified: register middleware + routes)
├── src/
│   ├── auth.py             (NEW: middleware + login/logout + cookie helpers, ~150 lines)
│   └── config.py           (modified: add AGENT_PASSWORD + COOKIE_SECRET fields)
└── templates/
    └── login.html          (NEW: minimal login form, ~30 lines)
```

### `src/auth.py` — four pieces

1. **Cookie helpers** (`sign_cookie`, `verify_cookie`):
   - HMAC-SHA256 over JSON payload using `COOKIE_SECRET`.
   - Format: `<base64-payload>.<base64-hmac>`.
   - Payload: `{"exp": <unix_ts>, "v": 1}` — minimal; no user info needed in single-password model.
   - Verify checks HMAC + expiry. Returns `None` on any failure.

2. **`AuthMiddleware`** (subclass of `BaseHTTPMiddleware`):
   - Allow-list: `/health`, `/login`, `/logout`, `/static/*`.
   - Otherwise: read `agent_session` cookie → `verify_cookie` → on success `call_next`; on failure `RedirectResponse('/login?next=<original-path>', status=302)`.
   - **Fail-closed on missing config**: if `AGENT_PASSWORD` or `COOKIE_SECRET` are unset, middleware returns 503 `"auth not configured"` for protected paths. Prevents accidental "deployed without auth" — a missing env var won't silently disable security.

3. **Login routes** (registered via `register_auth_routes(app)`):
   - `GET /login` → renders `login.html`, passes through `?next=`.
   - `POST /login` → form-parsed `password` and `next`. Constant-time compare (`hmac.compare_digest`) against `AGENT_PASSWORD`. On success: set cookie via `Response.set_cookie('agent_session', sign_cookie({...}), httponly=True, secure=True, samesite='lax', max_age=30*86400)`, redirect to `next`. On failure: re-render with error + record rate-limit hit.
   - `GET /logout` → clear cookie via `delete_cookie`, redirect to `/login`.

4. **`LoginRateLimiter`** (in-memory, per-IP):
   - Threshold: up to 5 POST attempts per IP per 60s rolling window. The 6th attempt within that window returns 429.
   - Implementation: `dict[str, list[float]]` of recent attempt timestamps; old entries pruned on each check.
   - Single-instance only — rate limit is per-container, not global. Fine for the min=max=1 instance config; flagged as a risk if scaling out.
   - On block: log a warning with IP + count.

### `templates/login.html`

Vanilla HTML, ~30 lines. Single `<input type=password>` + submit, hidden `next` field, optional error message slot. Minimal inline `<style>`. Looks intentional, not embarrassing.

### Wiring in `api.py`

```python
from src.auth import AuthMiddleware, register_auth_routes

app = FastAPI(..., lifespan=lifespan)
app.add_middleware(AuthMiddleware)
register_auth_routes(app)
mount_chainlit(app=app, target="chat.py", path="/chat")
```

Middleware is registered **before** the Chainlit mount, so all `/chat/*` traffic — including the WebSocket upgrade — passes through `AuthMiddleware` first. The browser sends the cookie on the WS upgrade request, so cookie auth carries through naturally; this is verified manually.

### `src/config.py` additions

```python
AGENT_PASSWORD: str = Field(default="", description="Shared password for the deployment gate.")
COOKIE_SECRET: str = Field(default="", description="HMAC secret for signed cookies. `openssl rand -hex 32`.")
```

Empty defaults. The middleware enforces fail-closed at runtime, so a missing value won't leak access — it returns 503 instead. Local dev sets both in `.env`; `.env.example` documents them.

## IaC stack

### Layout

```
agent_fin/
└── infra/
    └── cdk/
        ├── app.py              (CDK entrypoint, instantiates stacks)
        ├── ecr_stack.py        (ECR repo, separate so it can deploy first)
        ├── runner_stack.py     (App Runner + IAM, depends on ECR)
        ├── cdk.json            (CDK config)
        ├── requirements.txt    (aws-cdk-lib, constructs)
        └── README.md           (deploy steps + first-time bootstrap)
```

**Two stacks:** chicken-and-egg — App Runner needs an existing ECR image. Solution: deploy `EcrStack` first, push the image, then deploy `RunnerStack`. After bootstrap, ongoing image push and App Runner update are two steps in `deploy.sh` (no further multi-stack orchestration).

### `AgentFinEcrStack`

- ECR repo `agent-fin`
  - Image scanning: on-push
  - Lifecycle policy: retain last 10 images, expire older
  - Encryption: AES-256 (default)

### `AgentFinRunnerStack`

- **App Runner service `agent-fin`**:
  - Source: ECR image, tag = `latest` (deploy.sh updates this tag on each deploy)
  - Auto-deploy from ECR: **off** — explicit `start-deployment` from deploy.sh keeps control
  - CPU: 1 vCPU, Memory: 4 GB (KB pickle is ~350 MB; need headroom for in-flight tools + Python)
  - Port: 8080 (matches Dockerfile `EXPOSE`)
  - Health check: `GET /health`, interval 20s, timeout 5s, healthy threshold 2, unhealthy 3
  - Auto-scaling: min 1 / max 1 instance (single-instance keeps in-memory rate limiter and lifespan KB cache simple; revisit when traffic justifies it)
  - Network: public egress (DeepSeek + Bedrock + LangSmith are external)

- **Instance role** (attached to running container):
  - `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream` for: Titan v2 embeddings, Haiku (router/judge), Sonnet (orchestrator when `ORCHESTRATOR_PROVIDER=bedrock`)
  - CloudWatch logs write
  - Specific model ARNs only — not Bedrock-wide

- **Access role** (App Runner uses to pull from ECR):
  - `ecr:GetAuthorizationToken`, `ecr:BatchCheckLayerAvailability`, `ecr:GetDownloadUrlForLayer`, `ecr:BatchGetImage` on the `agent-fin` repo only

- **Env vars on the App Runner service** (read from local environment at `cdk deploy` time):
  - `AGENT_PASSWORD`, `COOKIE_SECRET`, `DEEPSEEK_API_KEY`, `LANGSMITH_API_KEY` (optional), `LANGSMITH_PROJECT` (optional), `LANGSMITH_TRACING` (optional), `AWS_REGION`
  - Read via `os.environ.get(...)` in CDK app. User runs `set -a && . .env && set +a && cdk deploy AgentFinRunnerStack`.
  - **Caveat**: values get baked into the CloudFormation template stored in CDK's S3 staging bucket. Acceptable per Decision 3.
  - **Validation**: CDK fails fast if `AGENT_PASSWORD` or `COOKIE_SECRET` are unset locally.

- **Stack outputs**:
  - App Runner service URL
  - ECR repo URI

### CDK-specific notes

- `cdk bootstrap` is one-time per account/region (creates the CDK toolkit stack — staging bucket, deploy roles).
- Region pinned to `us-east-1` to match existing setup.
- `cdk.context.json` is gitignored to keep env-var values out of git.

## Deploy script

`scripts/deploy.sh` — Bash, ~80-100 lines. Single entrypoint for "deploy current code to AWS." Replaces the README's manual deploy loop.

### Pipeline (each step fails fast under `set -euo pipefail`)

1. **Preflight**: verify cwd is `agent_fin/`, required env vars are loaded (`AGENT_PASSWORD`, `COOKIE_SECRET`, `DEEPSEEK_API_KEY`, `AWS_REGION`), AWS auth works (`aws sts get-caller-identity`). Warn on uncommitted changes (don't block). Resolve `IMAGE_TAG=$(git rev-parse --short HEAD)`.

2. **Bootstrap ECR if needed**: `aws ecr describe-repositories --repository-names agent-fin` → if missing, run `cdk deploy AgentFinEcrStack`. Idempotent; usually a no-op after first deploy.

3. **Build + tag + push**:
   ```bash
   docker build --platform=linux/amd64 -t agent-fin:$IMAGE_TAG -t agent-fin:latest .
   aws ecr get-login-password | docker login --username AWS --password-stdin <ecr-uri>
   docker tag agent-fin:$IMAGE_TAG <ecr-uri>:$IMAGE_TAG
   docker tag agent-fin:latest    <ecr-uri>:latest
   docker push <ecr-uri>:$IMAGE_TAG
   docker push <ecr-uri>:latest
   ```

4. **Apply infra**: `cdk deploy AgentFinRunnerStack --require-approval never`. First run creates the App Runner service. Subsequent runs no-op unless infra changed (env-var rotation, instance size, IAM tweak).

5. **Force redeploy**: `aws apprunner start-deployment --service-arn <arn>`. Necessary because if only the image tag changed (not infra), CDK won't trigger App Runner. This step ensures the new image rolls out.

6. **Wait + report**: poll `aws apprunner describe-service` every 10s; print the URL once `Status=RUNNING`. Timeout 5 min with a clear error if exceeded.

### Error model

- `set -euo pipefail` at top — fail on any command error, undefined var, or pipe failure.
- Each step has a clear error message before exit.
- Rollback handled by App Runner: if the new container fails health checks, App Runner keeps the previous image live. No explicit rollback code.

### Logging

- Every step prints `[deploy] <step>` to stdout for grep-friendly logs.
- Final output: service URL, deploy duration, image tag deployed.

### Optional flags (deferred — ship without them initially)

- `--skip-build` — env-var-only redeploys (rotate password).
- `--skip-cdk` — code-only changes when no infra diff exists.
- `--tag <tag>` — deploy a specific image (rollback to known-good).

### README updates

- `agent_fin/README.md`: replace the multi-step ECR/App Runner block with `./scripts/deploy.sh`. Reference `infra/cdk/README.md` for first-time setup.
- `infra/cdk/README.md`: prerequisites (Node, CDK CLI, AWS CLI, `cdk bootstrap`), what the two stacks do, how to destroy.

### First-time-ever deploy

```bash
cd agent_fin
uv sync
cd infra/cdk && pip install -r requirements.txt && cd ../..
cdk bootstrap                          # one-time per account/region
set -a && . .env && set +a             # loads AGENT_PASSWORD, COOKIE_SECRET, etc.
./scripts/deploy.sh                    # ~5-7 min cold
# → prints https://xxx.us-east-1.awsapprunner.com
```

### Subsequent deploys

```bash
set -a && . .env && set +a
./scripts/deploy.sh                    # ~3-4 min warm
```

## Testing strategy

This is the project's first test scaffolding. Auth code is well-bounded and pure-ish — a good starter.

### Layout

```
agent_fin/
├── pyproject.toml          (add pytest + pytest-asyncio to dev deps)
└── tests/
    ├── __init__.py
    ├── conftest.py         (fixtures: env var setup, TestClient)
    ├── test_auth.py        (cookie helpers, middleware, login/logout routes)
    └── test_smoke.py       (end-to-end happy path through TestClient)
```

### `tests/test_auth.py` — three groups (~25 cases, ~150 lines)

**Cookie helpers** (pure functions):
- `test_sign_verify_round_trip`
- `test_verify_rejects_tampered_payload`
- `test_verify_rejects_tampered_signature`
- `test_verify_rejects_expired`
- `test_verify_rejects_wrong_secret`
- `test_verify_rejects_malformed`

**AuthMiddleware** (FastAPI `TestClient`):
- `test_health_bypasses_auth`
- `test_login_get_bypasses_auth`
- `test_static_bypasses_auth`
- `test_protected_path_redirects_when_no_cookie`
- `test_protected_path_redirects_when_invalid_cookie`
- `test_protected_path_redirects_when_expired_cookie`
- `test_protected_path_passes_through_with_valid_cookie`
- `test_redirect_preserves_next_param`
- `test_503_when_AGENT_PASSWORD_unset`
- `test_503_when_COOKIE_SECRET_unset`

**Login/logout routes**:
- `test_login_post_correct_password_sets_cookie_and_redirects`
- `test_login_post_wrong_password_no_cookie`
- `test_login_post_uses_constant_time_compare` (smoke check; not a true side-channel test)
- `test_login_post_respects_next_param`
- `test_login_post_rate_limits_after_5_attempts`
- `test_login_rate_limit_resets_after_window`
- `test_logout_clears_cookie`

### `tests/test_smoke.py` — one happy-path test

```python
def test_full_browser_flow(client):
    # 1. Hit / unauthenticated → redirected to /login
    # 2. POST /login with correct password → cookie set + redirect
    # 3. Hit / with cookie → 200
    # 4. Hit /logout → cookie cleared
    # 5. Hit / again → redirected to /login
```

### `tests/conftest.py`

```python
@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AGENT_PASSWORD", "test123")
    monkeypatch.setenv("COOKIE_SECRET", "a" * 64)
    from src.auth import _rate_limiter
    _rate_limiter.reset()
    from api import app
    return TestClient(app)
```

### Out of scope

- WebSocket auth for Chainlit (verified manually; `TestClient` doesn't easily exercise WS upgrade with cookies)
- End-to-end browser tests (Selenium/Playwright)
- Load / rate-limit stress tests
- CDK tests beyond `cdk synth` running cleanly
- Tests for the existing agent code (separate effort; reliability work for a different design)

### Manual verification checklist

Run before merging:

- [ ] Local: `AGENT_PASSWORD=dev uvicorn api:app` → browse `localhost:8000`, redirected to `/login`.
- [ ] Wrong password → error message, stays on `/login`.
- [ ] Correct password → redirected, cookie set.
- [ ] `/chat` loads Chainlit; chat works (verifies WebSocket carries cookie).
- [ ] `/logout` clears cookie; next request redirects to `/login`.
- [ ] Hammer `/login` with 6 wrong passwords from one IP → 429 on the 6th.
- [ ] Server restart → cookie still valid (HMAC self-validating).
- [ ] After deploy: same flow against App Runner URL.

## Out of scope (for this design)

- Sessions UX (left pane, multi-session history) — separate brainstorming target.
- Accuracy/latency improvements — separate design(s).
- Per-user accounts / OAuth / multi-tenant — explicitly traded against in Decision 1.
- Secrets Manager / Parameter Store migration — Decision 3 defers to "when ops friction justifies."
- Custom domain + Route 53 + ACM — App Runner default URL is fine for v1.
- Multi-region / multi-instance scaling — single-instance is sufficient for trusted-user traffic.
- CI/CD pipeline (GitHub Actions auto-deploy) — manual `./scripts/deploy.sh` is sufficient.

## Open questions / risks

- **CloudFormation env-var bake-in.** Plain-text env values transit through CDK's S3 staging bucket. Acceptable for now; flagged for revisit if a real security review happens.
- **Single-instance assumption.** In-memory rate limiter and lifespan KB cache assume one container. If we ever scale to N>1, both need redesigning.
- **Chainlit WebSocket cookie behavior.** Standard Starlette/Chainlit behavior should propagate the cookie on WS upgrade, but this needs manual verification — it's the only piece that can't be unit-tested.
- **DEEPSEEK_API_KEY in CloudFormation template.** Same caveat as `AGENT_PASSWORD`. Same mitigation: defer to Secrets Manager when justified.

## Implementation handoff

Next step: invoke `superpowers:writing-plans` to produce a step-by-step implementation plan from this spec.
