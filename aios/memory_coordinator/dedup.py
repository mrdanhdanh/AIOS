"""Deduplication for memory candidates.

AC-023-06: Duplicate memory doesn't bloat context.
"""

from __future__ import annotations

import hashlib
from typing import Any

from aios.memory_coordinator.contracts import MemoryCandidate


class Deduplicator:
    """Removes duplicate memory candidates.

    Uses content hash for exact dedup and optional similarity threshold.
    """

    def __init__(self, similarity_threshold: float = 0.9) -> None:
        self._similarity_threshold = similarity_threshold

    def _content_hash(self, content: str) -> str:
        """Compute hash of content."""
        normalized = content.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def deduplicate(self, candidates: list[MemoryCandidate]) -> list[MemoryCandidate]:
        """Remove exact duplicates by content hash.

        AC-023-06: Duplicate memory doesn't bloat context.
        """
        seen: dict[str, MemoryCandidate] = {}
        result: list[MemoryCandidate] = []

        for c in candidates:
            h = self._content_hash(c.content)
            if h not in seen:
                seen[h] = c
                result.append(c)
            else:
                # Keep the one with higher score
                if c.score > seen[h].score:
                    result.remove(seen[h])
                    seen[h] = c
                    result.append(c)

        return result

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """Compute Jaccard similarity between two texts."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union) if union else 0.0

    def similarity_deduplicate(
        self,
        candidates: list[MemoryCandidate],
    ) -> list[MemoryCandidate]:
        """Remove near-duplicates using similarity threshold."""
        if not candidates:
            return []

        result: list[MemoryCandidate] = [candidates[0]]
        for c in candidates[1:]:
            is_dup = False
            for existing in result:
                sim = self.compute_similarity(c.content, existing.content)
                if sim >= self._similarity_threshold:
                    is_dup = True
                    if c.score > existing.score:
                        result.remove(existing)
                        result.append(c)
                    break
            if not is_dup:
                result.append(c)

        return result
