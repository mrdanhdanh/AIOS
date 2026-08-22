"""Memory filtering — scope, metadata filters, and provenance enforcement.

AC-023-08: Provenance tracked. When a query requires provenance, candidates
without provenance are excluded from the final selection (spec §6).
"""

from __future__ import annotations

from typing import Any

from aios.memory_coordinator.contracts import MemoryCandidate, MemoryQuery


class MemoryFilter:
    """Applies scope, metadata filters and provenance enforcement."""

    def apply(
        self,
        query: MemoryQuery,
        candidates: list[MemoryCandidate],
    ) -> list[MemoryCandidate]:
        result: list[MemoryCandidate] = []
        for c in candidates:
            # Scope boundary (INV-011 memory isolation).
            if query.scope and c.scope and c.scope != query.scope:
                continue

            # Metadata filters.
            if query.filters:
                if not self._matches_filters(c, query.filters):
                    continue

            # Provenance enforcement (fail-closed: exclude if missing).
            if query.required_provenance and not c.provenance:
                continue

            result.append(c)
        return result

    @staticmethod
    def _matches_filters(
        candidate: MemoryCandidate,
        filters: dict[str, Any],
    ) -> bool:
        for key, value in filters.items():
            if candidate.metadata.get(key) != value:
                return False
        return True
