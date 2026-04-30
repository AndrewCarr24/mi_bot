"""Lazy singleton access to the dsRAG KnowledgeBase + auto-query helper.

Pointed at the KB built by `pipelines/build_kb.py`. Sets up environment
variables so dsRAG's OpenAI client (used at query time for auto-query and
any in-tree LLM calls) routes to DeepSeek's OpenAI-compatible endpoint,
matching the rest of the stack.

`get_search_queries` is our own implementation of dsRAG's auto-query
helper. The upstream `dsrag.auto_query.get_search_queries` is marked
legacy in dsRAG's source and is hardcoded to Claude Sonnet 3.5 via the
Anthropic API; we replicate the small logic here so it routes through
our DeepSeek client. The `AUTO_QUERY_GUIDANCE` prompt is taken from
dsRAG's published FinanceBench eval script.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

from langsmith import traceable
from langsmith.wrappers import wrap_openai
from loguru import logger
from pydantic import BaseModel


_REPO_ROOT = Path(__file__).resolve().parents[2]
DSRAG_STORE_DIR = _REPO_ROOT / "data" / "dsrag_store"
# Single multi-document KB. Filings are distinguished by their `doc_id`
# metadata (TICKER_FORM_PERIOD, matching data/parsed/<stem>.md). The agent
# passes `doc_id` as a metadata filter when scoping retrieval to one filing.
DSRAG_KB_ID = "filings_kb"
# The pipeline code registers BedrockTitanEmbedding as an Embedding subclass
# at import time — dsRAG's from_dict deserialization needs that class
# registered before KB load.
_PIPELINE_DIR = _REPO_ROOT / "pipelines"


_kb = None


def _ensure_imports_registered() -> None:
    if str(_PIPELINE_DIR) not in sys.path:
        sys.path.insert(0, str(_PIPELINE_DIR))
    import bedrock_embedding  # noqa: F401 — registers subclass with dsRAG


def _configure_deepseek_as_openai() -> None:
    """dsRAG's AutoContext / auto-query LLMs route through its OpenAI client;
    point that client at DeepSeek's OpenAI-compatible endpoint.

    Pydantic Settings reads `.env` into the in-memory settings object but
    does not re-export back to os.environ. The raw OpenAI client used by
    smart_rrf_alpha and auto_query reads from os.environ directly, so we
    prime os.environ from settings here to keep both paths consistent."""
    from src.config import settings

    api_key = os.environ.get("DEEPSEEK_API_KEY") or settings.DEEPSEEK_API_KEY
    if not api_key:
        return
    os.environ.setdefault("DEEPSEEK_API_KEY", api_key)
    # Don't stomp a real OPENAI_API_KEY if the caller set one explicitly.
    os.environ.setdefault("OPENAI_API_KEY", api_key)
    os.environ.setdefault(
        "DSRAG_OPENAI_BASE_URL",
        os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    )


def _rewrite_kb_paths_if_needed() -> None:
    """dsRAG bakes absolute paths for chunk_db / vector_db / file_system
    into the metadata JSON at build time. When the KB folder moves
    (container, fork, fresh checkout), those paths are stale and
    BasicChunkDB.__init__ tries to mkdir at the old location.

    Patch the metadata in-place so paths track DSRAG_STORE_DIR. Idempotent.
    """
    import json

    meta_path = DSRAG_STORE_DIR / "metadata" / f"{DSRAG_KB_ID}.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    components = meta.get("components", {})
    target_dir = str(DSRAG_STORE_DIR)
    target_images = str(DSRAG_STORE_DIR / "page_images")
    changed = False
    for key in ("chunk_db", "vector_db"):
        if components.get(key, {}).get("storage_directory") != target_dir:
            components.setdefault(key, {})["storage_directory"] = target_dir
            changed = True
    fs = components.get("file_system", {})
    if fs.get("base_path") != target_images:
        fs["base_path"] = target_images
        components["file_system"] = fs
        changed = True
    if changed:
        meta_path.write_text(json.dumps(meta, indent=2))
        logger.info(f"Patched KB metadata paths → {target_dir}")


def get_kb():
    """Load the persisted KB wrapped in HybridKnowledgeBase.

    HybridKnowledgeBase subclasses dsRAG's KnowledgeBase and overrides
    `_search` to combine semantic (cosine) and lexical (BM25) retrieval
    via RRF fusion. It also applies the metadata_filter ourselves —
    BasicVectorDB silently drops it.
    """
    global _kb
    if _kb is not None:
        return _kb
    _ensure_imports_registered()
    _configure_deepseek_as_openai()
    _rewrite_kb_paths_if_needed()
    from src.infrastructure.hybrid_kb import HybridKnowledgeBase

    logger.info(f"Loading hybrid KB '{DSRAG_KB_ID}' from {DSRAG_STORE_DIR}")
    _kb = HybridKnowledgeBase(
        DSRAG_KB_ID,
        storage_directory=str(DSRAG_STORE_DIR),
        exists_ok=True,
    )

    # Optional FlashRank cross-encoder reranker. Enabled via env var so
    # we can A/B test latency vs accuracy without a code change. Off by
    # default (NoReranker baked into KB metadata).
    if os.environ.get("RERANKER", "").lower() == "flashrank":
        from src.infrastructure.flashrank_reranker import FlashRankReranker
        model = os.environ.get("FLASHRANK_MODEL", "ms-marco-TinyBERT-L-2-v2")
        _kb.reranker = FlashRankReranker(model_name=model)
        logger.info(f"FlashRank reranker active (model={model})")

    return _kb


# ---------------------------------------------------------------------------
# Query expansion (auto-query)
# ---------------------------------------------------------------------------

AUTO_QUERY_GUIDANCE = """
The knowledge base contains SEC filings for publicly traded companies, like 10-Ks, 10-Qs, and 8-Ks. Keep this in mind when generating search queries. The things you search for should be things that are likely to be found in these documents.

When deciding what to search for, first consider the pieces of information that will be needed to answer the question. Then, consider what to search for to find those pieces of information. For example, if the question asks what the change in revenue was from 2019 to 2020, you would want to search for the 2019 and 2020 revenue numbers in two separate search queries, since those are the two separate pieces of information needed. You should also think about where you are most likely to find the information you're looking for. If you're looking for assets and liabilities, you may want to search for the balance sheet, for example.
""".strip()


_AUTO_QUERY_SYSTEM = """\
You are a query generation system. Please generate one or more search queries (up to a maximum of {max_queries}) based on the provided user input. DO NOT generate the answer, just queries.

Each of the queries you generate will be used to search a knowledge base for information that can be used to respond to the user input. Make sure each query is specific enough to return relevant information. If multiple pieces of information would be useful, you should generate multiple queries, one for each specific piece of information needed.

{auto_query_guidance}"""


class _Queries(BaseModel):
    queries: List[str]


_auto_query_client = None


def _get_auto_query_client():
    """Cached instructor client routed at DeepSeek's OpenAI-compatible API.

    Uses `deepseek-chat` (not v4-flash) because instructor's default
    Mode.TOOLS sends a forced `tool_choice` that v4-flash's default thinking
    mode rejects.
    """
    global _auto_query_client
    if _auto_query_client is not None:
        return _auto_query_client
    _configure_deepseek_as_openai()
    import instructor
    from openai import OpenAI

    oa = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY") or os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("DSRAG_OPENAI_BASE_URL", "https://api.deepseek.com/v1"),
        timeout=60.0,
    )
    # Wrap so the auto-query LLM round-trip (prompt, completion, tokens)
    # appears in LangSmith as a child run when LANGSMITH_TRACING=true.
    # No-op when tracing is disabled.
    oa = wrap_openai(oa)
    _auto_query_client = instructor.from_openai(oa, mode=instructor.Mode.TOOLS)
    return _auto_query_client


@traceable(run_type="chain", name="auto_query")
def get_search_queries(
    user_input: str,
    auto_query_guidance: str = AUTO_QUERY_GUIDANCE,
    max_queries: int = 6,
) -> List[str]:
    """Decompose a user question into a small set of independent KB search
    queries via a single LLM call."""
    client = _get_auto_query_client()
    resp = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=400,
        temperature=0.2,
        response_model=_Queries,
        messages=[
            {
                "role": "system",
                "content": _AUTO_QUERY_SYSTEM.format(
                    max_queries=max_queries,
                    auto_query_guidance=auto_query_guidance,
                ),
            },
            {"role": "user", "content": user_input},
        ],
    )
    return resp.queries[:max_queries]


# ---------------------------------------------------------------------------
# Smart RRF alpha — DeepSeek picks BM25 weight per question
# ---------------------------------------------------------------------------

_smart_alpha_client = None


def _get_smart_alpha_client():
    """Cached raw OpenAI client (no instructor) for the smart-alpha call.
    Uses the same DeepSeek endpoint as auto_query."""
    global _smart_alpha_client
    if _smart_alpha_client is not None:
        return _smart_alpha_client
    _configure_deepseek_as_openai()
    from openai import OpenAI

    oa = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY") or os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("DSRAG_OPENAI_BASE_URL", "https://api.deepseek.com/v1"),
        timeout=30.0,
    )
    _smart_alpha_client = wrap_openai(oa)
    return _smart_alpha_client


_SMART_ALPHA_SYSTEM = """\
You are choosing how to weight retrieval over an SEC-filings knowledge base.
Two retrievers are run in parallel and their rankings are fused via RRF:
  - BM25 (lexical): rewards exact phrase matches, rare technical terms,
    specific dollar figures and percentages, exact table headings.
  - Semantic embedding: rewards conceptual overlap, paraphrase, abstract
    topic match.

Given the user's question, return a SINGLE FLOAT between 0.0 and 1.0
representing the BM25 weight in the RRF fusion. The semantic weight is
1 - alpha. Guidelines:
  - alpha=0.5: balanced (default for general questions).
  - alpha=0.65-0.75: question contains specific industry terms, named
    line items, exact metric phrases ("loss and loss adjustment expenses
    ratio", "consolidated statements of operations"), or numerical
    values.
  - alpha=0.25-0.4: conceptual or abstract question ("what's the
    company's strategy", "describe risk factors") where exact phrasing
    matters less than topic overlap.

Return ONLY the float. No explanation."""


@traceable(run_type="chain", name="smart_alpha")
def smart_rrf_alpha(query: str) -> float:
    """Ask DeepSeek for the optimal BM25 weight (0-1) for this query.
    Used when env RRF_ALPHA=smart (the default). Falls back to 0.4 on
    any error — that's the static value that won the FinanceBench
    sweep, so it's a sensible prior if the per-question call fails."""
    try:
        from src.config import settings

        client = _get_smart_alpha_client()
        # deepseek-v4-flash is a reasoning model — it spends tokens on
        # hidden reasoning_content before emitting visible content. Cap
        # at 256 so the visible answer (a single float) actually fits.
        resp = client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL_ID,
            max_tokens=256,
            temperature=0.0,
            messages=[
                {"role": "system", "content": _SMART_ALPHA_SYSTEM},
                {"role": "user", "content": query},
            ],
        )
        text = (resp.choices[0].message.content or "").strip()
        alpha = float(text)
        return max(0.0, min(1.0, alpha))
    except Exception as e:
        logger.warning(f"smart_rrf_alpha failed ({e}); defaulting to 0.4")
        return 0.4
