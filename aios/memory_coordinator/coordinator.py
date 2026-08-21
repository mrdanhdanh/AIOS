"""Memory Coordinator — central coordination layer.

AC-023-01: Full unified contract.
AC-023-02: Accesses all 4 memory types via contract.
AC-023-04: Deterministic ranking.
AC-023-07: Budget-aware selection.
AC-023-08: Provenance tracked.
AC-023-09: Agent cannot access memory implementation directly.
AC-023-10: Output compatible with Context Service.
"""

from __future__ import annotations

import time
from typing import Any, Protocol, runtime_checkable

from aios.memory_coordinator.contracts import (
    MemoryCandidate,
    MemoryContext,
    MemoryQuery,
    MemorySelection,
    MemoryType,
)
from aios.memory_coordinator.dedup import Deduplicator
from aios.memory_coordinator.ranker import Ranker


@runtime_checkable
class MemoryStoreProtocol(Protocol):
    """Protocol for memory stores."""

    def search(self, query: str, limit: int = 10) -> list[MemoryCandidate]: ...


class MemoryCoordinator:
    """Coordinates retrieval, ranking, dedup, and selection from 4 memory types.

    AC-023-01: Full unified contract.
    AC-023-02: Accesses all 4 memory types via protocol.
    AC-023-09: Agents access memory only through this coordinator.
    """

    def __init__(
        self,
        ranker: Ranker | None = None,
        dedup: Deduplicator | None = None,
    ) -> None:
        self._ranker = ranker or Ranker()
        self._dedup = dedup or Deduplicator()
        self._stores: dict[MemoryType, MemoryStoreProtocol] = {}

    def register_store(self, memory_type: MemoryType, store: MemoryStoreProtocol) -> None:
        """Register a memory store for a specific type."""
        self._stores[memory_type] = store

    def retrieve(
        self,
        query: MemoryQuery,
        stores: dict[MemoryType, MemoryStoreProtocol] | None = None,
    ) -> list[MemoryCandidate]:
        """Retrieve candidates from all registered stores.

        AC-023-02: Accesses all 4 types via contract.
        """
        active_stores = stores or self._stores
        all_candidates: list[MemoryCandidate] = []

        for mem_type in query.memory_types:
            store = active_stores.get(mem_type)
            if store is None:
                continue
            candidates = store.search(
                query=query.query_text,
                limit=query.max_candidates,
            )
            # Filter by memory type
            candidates = [c for c in candidates if c.memory_type == mem_type]
            all_candidates.extend(candidates)

        return all_candidates

    def rank_and_dedup(
        self,
        candidates: list[MemoryCandidate],
        query_text: str = "",
    ) -> list[MemoryCandidate]:
        """Rank and deduplicate candidates.

        AC-023-04: Deterministic ranking.
        AC-023-06: Deduplication.
        """
        # Rank
        ranked = self._ranker.rank(candidates, query_text)
        ranked_candidates = [c for c, _ in ranked]

        # Dedup
        deduped = self._dedup.deduplicate(ranked_candidates)
        return deduped

    def select_within_budget(
        self,
        candidates: list[MemoryCandidate],
        budget: int,
    ) -> MemorySelection:
        """Select candidates within token budget.

        AC-023-07: Budget-aware selection.
        """
        selected: list[MemoryCandidate] = []
        total_tokens = 0
        dropped = 0

        for c in candidates:
            token_count = c.token_count or max(1, len(c.content.split()))
            if total_tokens + token_count <= budget:
                selected.append(c)
                total_tokens += token_count
            else:
                dropped += 1

        return MemorySelection(
            selected=selected,
            total_tokens=total_tokens,
            budget=budget,
            dropped_count=dropped,
        )

    def coordinate(self, query: MemoryQuery) -> MemoryContext:
        """Full coordination pipeline: retrieve → rank → dedup → select.

        AC-023-10: Output compatible with Context Service.
        """
        # Step 1: Retrieve
        candidates = self.retrieve(query)

        # Step 2: Rank and dedup
        processed = self.rank_and_dedup(candidates, query.query_text)

        # Step 3: Select within budget
        selection = self.select_within_budget(processed, query.token_budget)

        # Step 4: Build provenance
        provenance = [
            c.memory_id for c in selection.selected
        ]

        return MemoryContext(
            query=query,
            selection=selection,
            provenance=provenance,
            metadata={
                "total_candidates": len(candidates),
                "after_dedup": len(processed),
                "selected_count": len(selection.selected),
            },
        )
