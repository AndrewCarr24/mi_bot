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
    point that client at DeepSeek's OpenAI-compatible endpoint."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return
    # Don't stomp a real OPENAI_API_KEY if the caller set one explicitly.
    os.environ.setdefault("OPENAI_API_KEY", api_key)
    os.environ.setdefault(
        "DSRAG_OPENAI_BASE_URL",
        os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    )


def get_kb():
    """Load the persisted KB. NoReranker is baked into the KB metadata at
    build time, so no runtime swap needed."""
    global _kb
    if _kb is not None:
        return _kb
    _ensure_imports_registered()
    _configure_deepseek_as_openai()
    from dsrag.knowledge_base import KnowledgeBase

    logger.info(f"Loading dsRAG KB '{DSRAG_KB_ID}' from {DSRAG_STORE_DIR}")
    _kb = KnowledgeBase(
        DSRAG_KB_ID,
        storage_directory=str(DSRAG_STORE_DIR),
        exists_ok=True,
    )
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
    _auto_query_client = instructor.from_openai(oa, mode=instructor.Mode.TOOLS)
    return _auto_query_client


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
