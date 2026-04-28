"""FlashRank cross-encoder reranker, wrapped as a dsRAG `Reranker` subclass.

Plugs into the existing `_search` hook point at the END of dsRAG's
retrieval pipeline (or the end of `HybridKnowledgeBase._search` for
us). Takes the candidates from semantic / hybrid retrieval and
re-orders them using a small cross-encoder.

Light default: `ms-marco-TinyBERT-L-2-v2` (~4 MB ONNX model). The
heavier default `ms-marco-MiniLM-L-12-v2` (33 MB) is more accurate
but ~2-3× slower per call; flip via the env var FLASHRANK_MODEL.

Cost
- Model download on first instantiation (~5-10s, one time per
  process). Cached under ~/.flashrank/.
- Per-query latency for top-N reranking:
    L-2-v2  : ~50-150ms for 50 candidates
    L-12-v2 : ~150-400ms for 50 candidates
- Adds onnxruntime to the runtime image (~55 MB).
"""

from __future__ import annotations

import os
from typing import Optional

from loguru import logger

from dsrag.reranker import Reranker


class FlashRankReranker(Reranker):
    """Cross-encoder reranker via FlashRank.

    Reorders the merged candidate list from `HybridKnowledgeBase._search`
    using a small cross-encoder that scores (query, chunk_text) jointly.
    The cross-encoder catches relevance signals that bag-of-vectors
    similarity blurs (subtle phrase matches, term order, negation).

    Args:
        model_name: a FlashRank model identifier. Defaults to the smallest
            and fastest cross-encoder.
        top_k: keep at most this many results after reranking. Defaults
            to keeping all (no further trimming — RSE downstream caps).
    """

    def __init__(
        self,
        model_name: str = "ms-marco-TinyBERT-L-2-v2",
        top_k: Optional[int] = None,
    ) -> None:
        super().__init__()
        from flashrank import Ranker

        self.model_name = model_name
        self.top_k = top_k
        logger.info(f"FlashRankReranker: loading {model_name!r}")
        self._ranker = Ranker(model_name=model_name)
        logger.info("FlashRankReranker: ready")

    def rerank_search_results(self, query: str, search_results: list) -> list:
        if not search_results:
            return search_results

        from flashrank import RerankRequest

        # Build the passage list — flashrank keys passages by an "id" we
        # supply, which lets us map reranked results back to the source.
        passages = []
        for i, r in enumerate(search_results):
            md = r.get("metadata") or {}
            text = md.get("chunk_text") or ""
            passages.append({"id": i, "text": text})

        reranked = self._ranker.rerank(
            RerankRequest(query=query, passages=passages)
        )

        # `reranked` is a list of {"id", "text", "score", ...} ordered by
        # cross-encoder score (highest first). Map back to the original
        # VectorSearchResult dicts and overwrite `similarity` with the
        # cross-encoder score so RSE downstream sees the new ranking.
        reordered: list = []
        for item in reranked:
            i = item["id"]
            r = dict(search_results[i])  # shallow copy — don't mutate input
            r["similarity"] = float(item.get("score", 0.0))
            reordered.append(r)

        if self.top_k is not None:
            reordered = reordered[: self.top_k]
        return reordered

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["model_name"] = self.model_name
        d["top_k"] = self.top_k
        return d
