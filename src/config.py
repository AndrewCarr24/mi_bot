from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Single source of truth for every tunable in the system.

    Two consumption patterns:
      - Static reads: import the singleton `settings` and read fields. Values
        are populated from `.env` + process env at import time.
      - Runtime-flip reads: a few prototyping knobs are read fresh from
        process env on each call (see callers in workflow/nodes.py,
        workflow/tools.py, workflow/edges.py). Those callers continue to
        use os.environ.get directly so mid-process A/B testing keeps
        working. The fields below document the full surface and provide
        the canonical default for each.

    Use `Settings().model_dump()` (or `runtime_snapshot()` below) to capture
    the current state for eval result sidecars / experiment logs.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Models / providers ─────────────────────────────────────────────
    ORCHESTRATOR_PROVIDER: Literal["bedrock", "deepseek"] = Field(
        default="deepseek",
        description=(
            "Which LLM provider serves the orchestrator (the ReAct agent). "
            "Router and judge stay on Bedrock Haiku regardless."
        ),
    )
    ORCHESTRATOR_MODEL_ID: str = Field(
        default="us.anthropic.claude-sonnet-4-6",
        description="Bedrock model ID for the main agent (used when provider=bedrock).",
    )
    ROUTER_MODEL_ID: str = Field(
        default="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        description="Bedrock model ID for intent classification.",
    )

    AWS_REGION: str = Field(
        default="us-east-1",
        description="AWS region for Bedrock embeddings + (optional) Bedrock orchestrator.",
    )

    DEEPSEEK_API_KEY: str = Field(
        default="",
        description="API key for DeepSeek (OpenAI-compatible endpoint).",
    )
    DEEPSEEK_MODEL_ID: str = Field(
        default="deepseek-v4-flash",
        description="DeepSeek model ID (used when provider=deepseek).",
    )
    DEEPSEEK_BASE_URL: str = Field(
        default="https://api.deepseek.com/v1",
        description="DeepSeek OpenAI-compatible API base URL.",
    )

    MEMORY_ID: str = Field(
        default="",
        description=(
            "AgentCore Memory ID. When unset, memory hooks are disabled and "
            "the agent runs stateless across requests."
        ),
    )

    # ── History condensation ───────────────────────────────────────────
    HISTORY_STRATEGY: Literal["trim", "summarize"] = Field(
        default="trim",
        description=(
            "How to condense conversation history. 'trim' compacts each "
            "completed turn to [Q, final_A] and evicts oldest pairs to fit "
            "budget. 'summarize' replaces older work with an LLM-authored "
            "structured summary. (Read fresh from env per call by "
            "workflow/nodes.py:_history_strategy.)"
        ),
    )
    HISTORY_TOKEN_BUDGET: int = Field(
        default=60_000,
        description=(
            "Token budget for the history passed to the agent LLM. Bounds "
            "the trim/summarize threshold."
        ),
    )

    # ── ReAct loop ─────────────────────────────────────────────────────
    MAX_TOOL_CALLS_PER_TURN: int = Field(
        default=12,
        description=(
            "Cap on cumulative tool calls per turn. The cap stops further "
            "ReAct iterations once exceeded; the current iteration's batch "
            "always executes (see edges.py:should_continue)."
        ),
    )

    # ── dsRAG retrieval ────────────────────────────────────────────────
    RRF_ALPHA: str = Field(
        default="0.4",
        description=(
            "BM25 weight in RRF fusion. Numeric value 0.0-1.0 (e.g. '0.4') "
            "or the literal 'smart' for per-question selection by DeepSeek. "
            "(Read fresh from env per call by workflow/tools.py:dsrag_kb.)"
        ),
    )
    DEDUP_CHUNKS: bool = Field(
        default=True,
        description=(
            "Exclude chunks already returned in earlier dsrag_kb calls within "
            "the same conversation thread. (Read fresh from env per call.)"
        ),
    )
    AUTO_QUERY_MAX: int = Field(
        default=3,
        description=(
            "Max number of search queries dsrag_kb's auto-query step "
            "decomposes a question into. (Read fresh from env per call.)"
        ),
    )

    MULTI_DOC_FILTER: Literal["off", "filter", "quota"] = Field(
        default="off",
        description=(
            "Multi-doc retrieval mode for dsrag_kb when `doc_id` is a list. "
            "'off': fan-out today (agent emits N parallel single-doc calls). "
            "'filter': single call with dsRAG `in` operator — top-K segments "
            "scored across the whole subset (recall risk on cohort sweeps). "
            "'quota': single call internally fanned out to N single-doc "
            "searches with top-K' per doc, then merged — preserves per-doc "
            "coverage. The prompt is updated to encourage list-form `doc_id` "
            "in 'filter' and 'quota' modes. Read fresh per call. "
            "(Backward compat: a literal 'true' is treated as 'filter'.)"
        ),
    )

    # ── Wiki preload ───────────────────────────────────────────────────
    DISABLE_WIKI_PRELOAD: bool = Field(
        default=False,
        description=(
            "When true, the router skips the wiki preload step regardless "
            "of slug. Used for A/B testing the wiki contribution. (Read "
            "fresh from env per call.)"
        ),
    )

    # ── Reranker (optional) ────────────────────────────────────────────
    RERANKER: str = Field(
        default="",
        description=(
            "Optional reranker after BM25/cosine fusion. 'flashrank' enables "
            "a local cross-encoder rerank; empty disables. (Read fresh.)"
        ),
    )
    FLASHRANK_MODEL: str = Field(
        default="ms-marco-TinyBERT-L-2-v2",
        description="FlashRank model name when RERANKER='flashrank'.",
    )

    @field_validator("MULTI_DOC_FILTER", mode="before")
    @classmethod
    def _normalize_multi_doc(cls, v):
        """Map legacy bool-style env values onto the new tri-state.
        true/1 → filter; false/0/empty → off; otherwise pass through
        for Literal validation."""
        if isinstance(v, str):
            v_low = v.strip().lower()
            if v_low in ("true", "1"):
                return "filter"
            if v_low in ("false", "0", ""):
                return "off"
            return v_low
        return v

    @classmethod
    def runtime_snapshot(cls) -> dict:
        """Capture all knob values as currently set in env (fresh re-read).

        Use this in eval result sidecars so future-you can answer
        'which config produced this CSV?' without guessing.
        """
        return cls().model_dump()


settings = Settings()
