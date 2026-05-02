"""Tools available to the agent.

Two-tool retrieval stack:
  - `dsrag_kb`        — semantic RAG over the full filings + industry corpus
                        for point-in-time facts, figures, and disclosures.
  - `wiki_read_page`  — read a synthesized wiki page (per Karpathy's LLM-Wiki
                        pattern) for definitions, cross-MI overviews, and
                        regulatory context. Page slate listed inline below.

`memory_retrieval_tool` is orthogonal (user preferences/facts/summaries) and
only gets surfaced when AgentCore Memory is configured via MEMORY_ID.
"""

import json
import os
from pathlib import Path
from typing import Annotated, Literal

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg, tool
from loguru import logger

from src.config import settings


# Wiki lives at agent_fin/wiki/. Resolve from this file so the path
# is correct in dev and in deployed packages.
_WIKI_ROOT = Path(__file__).resolve().parents[4] / "wiki"


# Per-thread set of (doc_id, chunk_index) tuples we've already returned
# in earlier dsrag_kb calls within the same conversation. Used when
# DEDUP_CHUNKS=true to keep subsequent calls from re-pulling the same
# content. Keyed by thread_id from RunnableConfig.
_SEEN_CHUNKS_PER_THREAD: dict[str, set] = {}


@tool
async def memory_retrieval_tool(
    query: str,
    memory_types: list[Literal["preferences", "facts", "summaries"]],
    config: Annotated[RunnableConfig, InjectedToolArg],
) -> str:
    """
    Retrieve the user's stored preferences, facts, or session summaries.
    Use before answering to personalize results.

    Args:
        query: Search query for semantic matching.
        memory_types: Which memory types to retrieve.

    Returns:
        JSON with memories organized by type.
    """
    configurable = (config or {}).get("configurable", {})
    actor_id = configurable.get("actor_id", "user:default")
    session_id = configurable.get("thread_id", "default_session")

    try:
        from src.infrastructure.memory import get_memory_instance
        memory = get_memory_instance()
        retrieved = memory.retrieve_specific_memories(
            query=query,
            actor_id=actor_id,
            session_id=session_id,
            memory_types=memory_types,
            top_k=5,
        )
        formatted = {
            k: [item.get("content", str(item)) for item in v]
            for k, v in retrieved.items()
        }
        return json.dumps(formatted, indent=2)
    except Exception as e:
        logger.error(f"memory_retrieval_tool failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def dsrag_kb(
    question: str,
    doc_id: str | None = None,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Semantic search over SEC filings via a dsRAG knowledge base. Pass the
    user's question verbatim — the tool decomposes it into multiple
    search queries internally (via dsRAG's auto-query helper, which is
    domain-tuned for SEC filings) and runs them all against the KB.
    Returns the most relevant multi-chunk *segments* (contiguous sections
    identified by dsRAG's Relevant Segment Extraction). Segments include
    an AutoContext header describing the source document and section.

    Scoping: pass `doc_id` to restrict retrieval to a single filing
    (recommended whenever the user's question names a specific ticker +
    period). The KB holds multiple filings; without a filter, results
    can come from any of them. Use the `doc_id` column in the system
    prompt's filings_catalog to pick the right value (format:
    TICKER_FORM_PERIOD, e.g. "ACT_10-Q_2024-09-30"). Pass doc_id=None to
    search across all filings (appropriate for cross-filing comparisons).

    Args:
        question: The user's question (verbatim; do not paraphrase).
        doc_id: Optional filing identifier to restrict retrieval to.
            Must match a `doc_id` in filings_catalog exactly.

    Returns:
        JSON list of {score, doc_id, content} segments, highest score first.
    """
    from src.infrastructure.dsrag_kb import (
        get_kb,
        get_search_queries,
        smart_rrf_alpha,
    )

    try:
        queries = get_search_queries(
            question,
            max_queries=int(os.environ.get("AUTO_QUERY_MAX", "3")),
        )
    except Exception as e:
        logger.warning(f"dsrag_kb auto-query failed: {e}")
        queries = [question]

    kb = get_kb()
    metadata_filter = (
        {"field": "doc_id", "operator": "equals", "value": doc_id}
        if doc_id
        else None
    )

    # --- env-var-driven A/B knobs (set per call, reset after) -------------
    thread_id = ((config or {}).get("configurable") or {}).get("thread_id", "_default")

    # Chunk dedup: when DEDUP_CHUNKS=true, exclude chunks already
    # returned in earlier calls in this thread.
    dedup_on = os.environ.get("DEDUP_CHUNKS", "true").lower() == "true"
    seen = _SEEN_CHUNKS_PER_THREAD.setdefault(thread_id, set()) if dedup_on else None
    kb._excluded_chunks = seen if dedup_on else None

    # RRF alpha: BM25 weight in fusion. Default "smart" — DeepSeek picks
    # per question. Numeric value (e.g. "0.4") forces a static alpha for
    # the whole session. Smart mode is generalizable (adapts to question
    # character) at near-equal quality.
    #
    # Note: on the 23-question FinanceBench eval, the static value
    # alpha=0.4 was technically the most accurate (22/23 vs smart at
    # 21/23). Smart mode trades 1 question of accuracy for fewer
    # iterations (1.52 calls/q vs 1.61) and slightly lower cost
    # ($0.081 vs $0.085). See eval/results/alpha_sweep_*.json.
    alpha_raw = os.environ.get("RRF_ALPHA", "0.4").strip()
    if alpha_raw.lower() == "smart":
        alpha = smart_rrf_alpha(question)
        logger.info(f"dsrag_kb: smart α={alpha:.2f} for question {question[:60]!r}")
    else:
        try:
            alpha = max(0.0, min(1.0, float(alpha_raw)))
        except ValueError:
            alpha = 0.5
    kb._rrf_alpha = alpha

    logger.info(
        f"dsrag_kb invoked: question={question[:80]!r} doc_id={doc_id!r} "
        f"expanded_to={queries} α={alpha:.2f} dedup={dedup_on}"
    )

    try:
        results = kb.query(queries, metadata_filter=metadata_filter)
    except Exception as e:
        logger.warning(f"dsrag_kb query failed: {e}")
        return json.dumps({"error": str(e)})
    finally:
        # Reset per-call attrs so a stale value can't leak into the next call.
        kb._excluded_chunks = None
        kb._rrf_alpha = 0.4

    # If dedup is on, mark every chunk that contributed to a returned
    # segment as "seen" so it's excluded from future calls in this thread.
    if dedup_on and seen is not None:
        for r in results:
            doc = r.get("doc_id", "")
            cs, ce = r.get("chunk_start"), r.get("chunk_end")
            if cs is not None and ce is not None:
                for ci in range(int(cs), int(ce) + 1):
                    seen.add((doc, ci))

    payload = [
        {
            "score": round(float(r.get("score", 0.0) or 0.0), 3),
            "doc_id": r.get("doc_id", ""),
            "content": r.get("content") or r.get("text") or "",
        }
        for r in results
    ]
    return json.dumps(payload, indent=2, default=str)


@tool
def wiki_read_page(slug: str) -> str:
    """
    Read a single LLM-authored wiki page about US private mortgage insurance.

    The wiki holds pre-synthesized analyst-perspective pages — definitions
    of MI metrics (PMIERs, NIW, IIF, persistency, loss ratio, reinsurance),
    one page per MI in the corpus, and regulatory / industry topic pages.
    Each page follows a fixed schema (summary → What it is → Why it matters →
    Current state → How it has evolved → Sources → Related) and cites
    underlying filings by `doc_id`.

    Use this tool over `dsrag_kb` when the user is asking for a definition,
    a synthesized overview, a structural / regulatory explanation, or a
    cross-MI comparison that doesn't depend on a specific filing's exact
    wording.

    Available slugs:
      Metrics:    metrics/iif, metrics/loss_ratio, metrics/niw,
                  metrics/persistency
      Companies:  companies/acgl_arch, companies/act_enact,
                  companies/esnt_essent, companies/mtg_mgic,
                  companies/nmih_nmi, companies/rdn_radian
      Topics:     topics/catastrophe_impact_on_mi, topics/crt_reinsurance,
                  topics/gse_relationship, topics/mi_regulatory_landscape,
                  topics/pmiers, topics/us_mortgage_market
      Index:      index   (the catalog of all pages, generated from disk)

    Args:
        slug: Page slug, e.g. "topics/pmiers" or "companies/mtg_mgic".
            Must match exactly. Pass "index" for the page catalog.

    Returns:
        The page's markdown content, or an error string if the slug is
        unknown.
    """
    slug = (slug or "").strip().strip("/")
    if not slug:
        return json.dumps({"error": "slug is required"})

    # "index" is generated dynamically from the filesystem so the
    # available-pages list can't drift from the on-disk reality.
    if slug == "index":
        if not _WIKI_ROOT.is_dir():
            return json.dumps({"error": f"wiki root not found: {_WIKI_ROOT}"})
        slugs_by_section: dict[str, list[str]] = {}
        for md in sorted(_WIKI_ROOT.rglob("*.md")):
            rel = md.relative_to(_WIKI_ROOT)
            if rel.name == "AGENTS.md":
                continue
            section = rel.parts[0] if len(rel.parts) > 1 else "(root)"
            slugs_by_section.setdefault(section, []).append(
                str(rel.with_suffix(""))
            )
        lines = ["# Wiki page index", ""]
        for section in sorted(slugs_by_section):
            lines.append(f"## {section}")
            for s in slugs_by_section[section]:
                lines.append(f"- {s}")
            lines.append("")
        logger.info("wiki_read_page invoked: slug='index' (generated)")
        return "\n".join(lines)

    page_path = (_WIKI_ROOT / f"{slug}.md").resolve()
    # Containment check: refuse paths that escape the wiki dir.
    try:
        page_path.relative_to(_WIKI_ROOT.resolve())
    except ValueError:
        return json.dumps({"error": f"slug outside wiki root: {slug!r}"})
    if not page_path.is_file():
        return json.dumps({
            "error": f"unknown wiki page: {slug!r}",
            "hint": "call wiki_read_page('index') to list available pages",
        })
    logger.info(f"wiki_read_page invoked: slug={slug!r} → {page_path.name}")
    return page_path.read_text()


def get_tools() -> list:
    """Return the tools bound to the ReAct agent.

    Only `dsrag_kb` is bound here. `wiki_read_page` is reserved for
    deterministic graph-side preload via `wiki_preload_node` — the
    router decides whether a question's primary topic matches a wiki
    page and, if so, the graph reads that page before the agent runs.
    The agent itself doesn't have wiki_read_page available, which
    enforces the "wiki at most once per turn" constraint structurally.

    `memory_retrieval_tool` is only added when AgentCore Memory is
    configured (MEMORY_ID set).
    """
    tools = [dsrag_kb]
    if settings.MEMORY_ID:
        tools.append(memory_retrieval_tool)
    return tools
