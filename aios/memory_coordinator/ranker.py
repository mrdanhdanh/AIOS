"""Deterministic ranking for memory candidates.

AC-023-04: Deterministic ranking without LLM.
"""

from __future__ import annotations

import time
from typing import Any

from aios.memory_coordinator.contracts import MemoryCandidate, MemoryScore


class Ranker:
    """Deterministic ranker for memory candidates.

    Uses weighted combination of relevance, recency, and importance.
    No LLM involved — fully deterministic.
    """

    def __init__(
        self,
        relevance_weight: float = 0.5,
        recency_weight: float = 0.3,
        importance_weight: float = 0.2,
    ) -> None:
        self._relevance_weight = relevance_weight
        self._recency_weight = recency_weight
        self._importance_weight = importance_weight

    def score(
        self,
        candidate: MemoryCandidate,
        query_text: str = "",
        reference_time: float | None = None,
    ) -> MemoryScore:
        """Score a single candidate."""
        ref_time = reference_time or time.time()

        # Relevance: simple text overlap
        relevance = self._compute_relevance(candidate.content, query_text)

        # Recency: exponential decay from reference time
        age_hours = max(0, (ref_time - candidate.timestamp) / 3600) if candidate.timestamp > 0 else 24
        recency = max(0, 1.0 - min(age_hours / 168, 1.0))  # 1 week half-life

        # Importance: from metadata or default
        importance = candidate.metadata.get("importance", 0.5)

        overall = (
            relevance * self._relevance_weight
            + recency * self._recency_weight
            + importance * self._importance_weight
        )

        return MemoryScore(
            memory_id=candidate.memory_id,
            relevance=relevance,
            recency=recency,
            importance=importance,
            overall=overall,
        )

    def rank(
        self,
        candidates: list[MemoryCandidate],
        query_text: str = "",
        reference_time: float | None = None,
    ) -> list[tuple[MemoryCandidate, MemoryScore]]:
        """Rank candidates and return sorted by overall score (descending)."""
        scored = []
        for c in candidates:
            score = self.score(c, query_text, reference_time)
            c.score = score.overall
            scored.append((c, score))
        scored.sort(key=lambda x: x[1].overall, reverse=True)
        return scored

    def _compute_relevance(self, content: str, query: str) -> float:
        """Simple text overlap relevance scoring."""
        if not query:
            return 0.5
        content_lower = content.lower()
        query_words = query.lower().split()
        if not query_words:
            return 0.5
        matches = sum(1 for w in query_words if w in content_lower)
        return min(matches / len(query_words), 1.0)
