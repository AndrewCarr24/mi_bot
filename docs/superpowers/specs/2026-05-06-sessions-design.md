# Sessions UX — Design

**Date:** 2026-05-06
**Status:** Design (pre-implementation)
**Owner:** Andrew Carr
**Skill flow:** brainstorming → writing-plans → executing-plans

## Problem

The Chainlit chat UI today has no concept of *sessions* — every refresh / browser-restart starts the user back at the welcome message. There's no left-pane list of prior conversations, no "pick up where you left off" behavior, no auto-naming of threads. This makes the deployed app feel like a one-shot lookup tool rather than a research assistant the user comes back to.

This project adds that layer on top of the existing deployment, leveraging Chainlit's built-in chat-history feature so we don't have to write the session-pane UI from scratch.

## Decisions

| # | Question | Choice |
|---|---|---|
| 1 | How sessions map to users (with shared-password auth) | Per-browser sessions, identified by a long-lived `agent_browser_id` cookie distinct from the auth cookie. No cross-device sync. |
| 2 | Implementation approach | Use Chainlit's built-in chat-history UI via its `data_layer`. Accept Chainlit's UI design choices in exchange for ~1 day vs ~5 days. |
| 3 | Storage backend | SQLite locally (`agent_fin/.chainlit/threads.db`); DynamoDB in production. Single Chainlit `BaseDataLayer` interface, env-var-selected. |
| 4 | Agent context across container restarts | Replay full message history from Chainlit's data layer on each turn. Drop in-process `MemorySaver`. Single source of truth. |
| 5 | Data lifetime | Cookie 1 year; DynamoDB TTL 1 year, matching the cookie. SQLite local has no TTL (manually delete `.chainlit/threads.db` to reset). |

**Defaults accepted without further debate:** Chainlit's auto-naming, date grouping, rename / delete UX. App Runner remains the host. Existing auth cookie (`agent_session`, 30 days) unchanged.

## Architecture

Three things layered on top of the existing deployment:

1. **`browser_id` cookie**, set by a new `BrowserIdMiddleware` on first visit. Long-lived, HTTP-only, separate from the auth cookie so logout doesn't drop the session list.
2. **A Chainlit `data_layer`**, registered in `chat.py`. Backend chosen by env var (`sqlite` or `dynamodb`). The data layer keys threads by `user_id` — we map `user_id := <browser_id cookie value>`.
3. **Stateless agent invocation.** `chat.py:on_message` fetches the thread's prior messages from the data layer, prepends them to the new user message, passes the full list into `get_streaming_events`. The in-process `MemorySaver` checkpointer is removed.

### Request flow on a turn

```
Browser
  ├── auth cookie (verified by AuthMiddleware) → access granted
  └── browser_id cookie (set by BrowserIdMiddleware on first visit)
        │
        ▼
Chainlit /chat → on_message handler
        │
        ├── Fetch thread messages from data layer (keyed by browser_id via cl.User)
        ├── Prepend to new user message
        ├── Stream agent events (full history → LangGraph, stateless)
        └── Append new turn's messages back to data layer

Storage layer (chosen by env):
  Local: SQLite at agent_fin/.chainlit/threads.db
  Prod:  DynamoDB table provisioned by CDK (TTL = 1 year)
```

### What we do NOT build

- Session pane UI (Chainlit renders it).
- Auto-titles (Chainlit derives from first user message).
- Rename / delete (Chainlit handles via right-click menu).
- New-chat button (top of left pane, by default).
- Date grouping (Today / Yesterday / Last 7 days — Chainlit's default).

## Browser identity & cookie semantics

**Two cookies, two responsibilities:**

| Cookie | Purpose | Lifetime | Cleared on logout |
|---|---|---|---|
| `agent_session` (existing) | Auth — proves you know the password | 30 days | Yes |
| `agent_browser_id` (new) | Identity — "this browser" | 1 year | No |

Cookie lifetime here means **how long the browser keeps the cookie before expiring**, not how long data lives in storage. Storage TTL is governed separately (Decision 5: 1 year DynamoDB TTL matches the cookie).

### `BrowserIdMiddleware` (new, in `src/auth.py`)

```python
class BrowserIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        existing = request.cookies.get("agent_browser_id")
        new_cookie = existing is None
        browser_id = existing or str(uuid.uuid4())
        request.state.browser_id = browser_id
        response = await call_next(request)
        if new_cookie:
            response.set_cookie(
                key="agent_browser_id",
                value=browser_id,
                max_age=365 * 86400,
                httponly=True,
                secure=True,
                samesite="lax",
                path="/",
            )
        return response
```

### Registration order (in `api.py`)

```python
app.add_middleware(AuthMiddleware)         # existing
app.add_middleware(BrowserIdMiddleware)    # new — added LAST so it runs FIRST
register_auth_routes(app)
```

Starlette's middleware stack is built outside-in: the last `add_middleware` call wraps everything before it. We want `BrowserIdMiddleware` to run before `AuthMiddleware` (so even unauthenticated visitors at `/login` get a browser_id), so it must be added *after*.

### Bridging to Chainlit via `@cl.header_auth_callback`

```python
from http.cookies import SimpleCookie

@cl.header_auth_callback
def header_auth_callback(headers: dict) -> cl.User | None:
    cookie_str = headers.get("cookie", "")
    jar = SimpleCookie(); jar.load(cookie_str)
    browser_cookie = jar.get("agent_browser_id")
    if browser_cookie is None:
        return None  # shouldn't happen — middleware sets it before reaching here
    return cl.User(identifier=browser_cookie.value)
```

This fires on every Chainlit HTTP request and WebSocket connect. Chainlit threads `user_id` through to the data layer automatically; no manual plumbing.

### Edge cases

- **First-ever visit:** browser_id missing → middleware mints UUID4 → `Set-Cookie` on response → `/login` page renders → user logs in. Browser is identified from first visit on.
- **Cookie cleared:** acts as a brand new browser. Old threads still exist in the data layer keyed by the old UUID, but the user can't see them. (Could add a "recover sessions by id" flow later — out of scope.)
- **Multiple tabs same browser:** all share the cookie → all see the same session list.
- **Different devices:** different cookies → different session lists. Acceptable per Decision 1.
- **Auth logout:** `agent_session` cookie cleared, `agent_browser_id` persists. Re-login picks up the same threads.

## Data layer setup

### `@cl.data_layer` registration in `chat.py`

```python
import chainlit.data as cl_data

@cl_data.data_layer
def get_data_layer():
    backend = os.environ.get("DATA_LAYER_BACKEND", "sqlite").lower()
    if backend == "dynamodb":
        return _build_dynamodb_layer()
    return _build_sqlite_layer()
```

Both backends implement Chainlit's `BaseDataLayer` interface. All of `cl.Message`, `cl.Step`, the session pane, thread switching, etc. work identically against either.

### SQLite (local dev)

- Path: `agent_fin/.chainlit/threads.db` (auto-created on first run).
- Backend: `chainlit.data.sql_alchemy.SQLAlchemyDataLayer` with `aiosqlite` driver.
- TTL: not enforced. Local dev data accumulates. `rm .chainlit/threads.db` to reset. Acceptable for dev-only.

### DynamoDB (production)

- Backend: `chainlit.data.dynamodb.DynamoDBDataLayer`.
- One table, name from env var `DYNAMODB_THREADS_TABLE` (default `agent-fin-threads`).
- **TTL: 1 year**, native DynamoDB feature. Matches the `agent_browser_id` cookie lifetime.
- Schema:
  ```
  Table: agent-fin-threads
    Hash key: PK (string)
    Sort key: SK (string)
    TTL attribute: expires_at (number, epoch seconds)
    Billing: PAY_PER_REQUEST
  ```
- Auth: App Runner instance role gets `dynamodb:Query/PutItem/UpdateItem/DeleteItem/GetItem` scoped to this table only.

### Stateless agent — `chat.py:on_message` modifications

```python
@cl.on_message
async def on_message(message: cl.Message):
    thread_id = cl.context.session.thread_id
    prior = await _fetch_thread_messages(thread_id)  # returns list[BaseMessage]
    full_messages = prior + [HumanMessage(content=message.content)]
    async for event in get_streaming_events(
        messages=full_messages,
        customer_name="User",
        conversation_id=thread_id,
    ):
        ...
```

`_fetch_thread_messages(thread_id)` reads from Chainlit's data layer and converts each persisted message to a LangChain message type. The conversion is straightforward (Chainlit stores role + content; LangChain has `HumanMessage`/`AIMessage`/`ToolMessage` for each).

### `streaming.get_streaming_events` extension

Today it accepts `messages: str` and constructs `[HumanMessage(content=messages)]`. We change the signature to `messages: str | list[BaseMessage]` — if a string is passed, wrap as before; if a list, pass through. One-line change. List input is what LangGraph natively expects, so this is a simplification.

### Effect

- The `MemorySaver` in-process checkpointer is removed entirely. `graph.compile()` is called without any checkpointer (LangGraph runs stateless).
- Each turn, the agent sees the full conversation history (trimmed by the existing `trim_history` function before LLM call — same per-turn token bound as today).
- Container restart: data layer survives, agent context replays. User picks up exactly where they left off.

### Settings additions (`src/config.py`)

```python
DATA_LAYER_BACKEND: Literal["sqlite", "dynamodb"] = Field(
    default="sqlite",
    description="Chainlit data layer backend. 'sqlite' for local dev, 'dynamodb' for App Runner.",
)
DYNAMODB_THREADS_TABLE: str = Field(
    default="agent-fin-threads",
    description="DynamoDB table name for Chainlit thread storage.",
)
```

`.env.example` gets a corresponding section showing both vars commented out (defaults handle local dev).

## IaC additions

The DynamoDB table is the only new AWS resource. Added to the existing `AgentFinRunnerStack` (one stack remains cleaner than splitting data into a third stack at this scale).

### `infra/cdk/runner_stack.py` additions

```python
from aws_cdk import aws_dynamodb as dynamodb

# ... inside AgentFinRunnerStack.__init__, after instance_role.add_to_policy(bedrock):

threads_table = dynamodb.Table(
    self,
    "AgentFinThreadsTable",
    table_name="agent-fin-threads",
    partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
    sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
    billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
    time_to_live_attribute="expires_at",
    removal_policy=cdk.RemovalPolicy.RETAIN,
    point_in_time_recovery=True,
)

threads_table.grant_read_write_data(instance_role)
```

### Env-var passthrough

Production-only settings injected directly by CDK (not from the developer's local `.env`):

```python
runtime_env.append(apprunner.CfnService.KeyValuePairProperty(
    name="DATA_LAYER_BACKEND", value="dynamodb"
))
runtime_env.append(apprunner.CfnService.KeyValuePairProperty(
    name="DYNAMODB_THREADS_TABLE", value=threads_table.table_name
))
```

Locally, `.env` doesn't set these → `Settings` defaults take over → SQLite is used. In production, CDK sets them on the App Runner service → DynamoDB is used.

### New CDK output

```python
CfnOutput(self, "ThreadsTableName", value=threads_table.table_name,
          description="DynamoDB table holding Chainlit thread + message history.")
```

### Notes

- **`removal_policy=RETAIN`**: `cdk destroy AgentFinRunnerStack` orphans the table rather than deleting it. Protects against accidental data loss while iterating on the stack. Manual `aws dynamodb delete-table` if removal is intentional.
- **`point_in_time_recovery=True`**: continuous backups for the last 35 days at no extra base cost (you only pay for restores).
- **No new ECR work**: image stays in the existing `agent-fin` repo.
- **Cost**: DynamoDB pay-per-request is essentially free at low traffic — first 25 GB storage free, ~$1.25 per million writes.
- **Deploy script unchanged**: `cdk deploy AgentFinRunnerStack` picks up the new table on the next apply.

## Testing strategy

Extends the existing pytest scaffolding (33 tests from the deployment+auth project).

### Layout

```
tests/
├── conftest.py             (existing)
├── test_auth.py            (existing)
├── test_smoke.py           (existing)
├── test_browser_id.py      (NEW)
└── test_data_layer.py      (NEW)
```

### `test_browser_id.py` — ~10 tests

- `test_browser_id_set_on_first_request` — no cookie in → `Set-Cookie: agent_browser_id=<uuid>` out, with all attributes (`HttpOnly`, `Secure`, `SameSite=Lax`, `Max-Age=31536000`, `Path=/`).
- `test_browser_id_persists_across_requests` — TestClient holds the cookie; second request has no `Set-Cookie` (already present).
- `test_browser_id_value_is_uuid4` — minted value matches UUID4 regex.
- `test_browser_id_distinct_per_client` — fresh TestClient → different UUID.
- `test_browser_id_available_on_request_state` — a route can read `request.state.browser_id`.
- `test_browser_id_set_on_unauth_paths` — `GET /login` (allowlisted) also gets the cookie.
- `test_browser_id_set_on_503_path` — even when AuthMiddleware fail-closes, browser_id is still set.
- `test_browser_id_not_overwritten_when_cookie_already_present` — incoming cookie kept, no new `Set-Cookie`.
- `test_browser_id_cookie_attributes` — explicit attribute check against design values.
- `test_browser_id_independent_of_auth_session` — clearing `agent_session` doesn't affect `agent_browser_id`.

### `test_data_layer.py` — ~8 tests

All using the SQLite backend. DynamoDB is verified manually post-deploy.

- `test_sqlite_data_layer_creates_db_file` — first call creates `.chainlit/threads.db`.
- `test_sqlite_data_layer_persists_thread_across_factory_calls` — write a thread, throw away the layer, build a fresh one pointing at the same path, read the thread back.
- `test_thread_message_round_trip` — write Human + AI messages, read them back, verify content + role.
- `test_message_replay_fetches_in_order` — write 5 messages, fetch via `_fetch_thread_messages`, verify chronological order.
- `test_message_replay_converts_to_langchain_types` — fetch returns `HumanMessage`/`AIMessage`/`ToolMessage`.
- `test_threads_isolated_by_user_id` — two `user_id`s don't see each other's threads.
- `test_data_layer_backend_env_switch` — `DATA_LAYER_BACKEND=sqlite` → `SQLAlchemyDataLayer`; `dynamodb` branch tested via mock.
- `test_get_streaming_events_accepts_message_list` — pass a 3-message list to `get_streaming_events`, verify the agent input shape.

### Manual verification checklist

Run before merging:

- [ ] First visit: cookie `agent_browser_id` set, value is a UUID. Inspect via DevTools → Application → Cookies.
- [ ] Send a message in a thread. Refresh. Thread appears in left pane, click it → message history rendered.
- [ ] Restart `uvicorn`. Re-open the same browser. Thread still listed. Click in. Type a follow-up: agent recalls prior context (no "what number?" amnesia).
- [ ] Click `+ New chat`. New thread starts empty. Old thread still visible.
- [ ] Right-click a thread → Rename. Confirm.
- [ ] Right-click a thread → Delete. Confirm gone.
- [ ] Open a different browser (or incognito): empty session list. Confirms per-browser isolation.
- [ ] Logout, log back in: same `agent_browser_id` cookie persists, threads still there.
- [ ] Clear cookies: fresh browser_id minted, empty session list.
- [ ] *Post-deploy only:* same flow against the App Runner URL, with DynamoDB as the backend.

### Out of scope

- DynamoDB integration tests with DynamoDB Local — overkill for the scale; manual post-deploy verification is sufficient.
- TTL expiry tests — would require advancing time; rely on DynamoDB's native TTL behavior.
- Concurrency / multi-tab tests — Chainlit handles its own WebSocket fanout.
- Migration tests — first deploy creates the table; no migration story until schema changes.

## Out of scope (for this design)

- Cross-device session sync (would need real per-user accounts; explicitly traded against in Decision 1).
- "Recover sessions by id" flow when a user clears cookies (could be added later if requested).
- Persistent LangGraph checkpointer (AgentCoreMemorySaver, etc.) — Decision 4 picks message replay instead.
- Custom session-pane UI (Decision 2 picks Chainlit's built-in).
- Per-thread sharing or collaboration (single-user model only).
- Migration of any existing in-process MemorySaver state to the data layer (no production state exists to migrate).

## Open questions / risks

- **Chainlit's data-layer API stability across versions.** We're on Chainlit 2.11.1. If the data-layer interface changes in a future version, the SQLite/DynamoDB integration may need updates. Pin Chainlit version in `pyproject.toml` to control this.
- **DynamoDB schema is determined by Chainlit's `DynamoDBDataLayer` impl.** We don't control table layout details (PK/SK formats); Chainlit does. If Chainlit changes the schema, existing data may not be readable. Mitigated by `point_in_time_recovery` for rollback.
- **Per-browser identity is recoverable only via the cookie.** If a user clears cookies, their session list is unreachable. Documented; not a bug, an expected consequence of Decision 1.
- **WebSocket cookie behavior** — the `agent_browser_id` cookie is sent on the WS upgrade just like the auth cookie. Verified the same way as in the deployment+auth project (manual checklist). If Chainlit's WS handshake somehow strips the cookie, `header_auth_callback` would return `None` and the session would be anonymous — would require investigation.
- **DynamoDB TTL is configured but does not fire today.** The CDK table has `time_to_live_attribute="expires_at"`, but Chainlit's stock `DynamoDBDataLayer` never writes that attribute on items — items therefore live indefinitely. To enforce the 1-year cookie/data alignment per Decision 5, we'd need to wrap the data layer to inject `expires_at = int(time.time()) + 365*86400` on `create_step`/`update_thread`, or use a DynamoDB Streams + Lambda stamper. Tracked as a follow-up; not blocking deploy at low traffic since DynamoDB pay-per-request storage cost is essentially free.

## Implementation handoff

Next step: invoke `superpowers:writing-plans` to produce a step-by-step implementation plan from this spec.
