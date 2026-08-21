"""Context Optimizer — main optimization pipeline.

AC-024-01: Context classified P0–P6.
AC-024-02: Doesn't exceed token budget.
AC-024-03: P0/P1 never dropped.
AC-024-04: Duplicates removed.
AC-024-05: Stale/expired handled.
AC-024-06: Deterministic compression first.
AC-024-10: Not dependent on specific Model Provider.
"""

from __future__ import annotations

import hashlib
from typing import Any

from aios.context_optimizer.compressor import DeterministicCompressor
from aios.context_optimizer.contracts import ContextItem, ContextPriority, OptimizedContext


class ContextOptimizer:
    """Optimizes context by priority, budget, and lifecycle.

    Deterministic-first — no LLM involvement.
    """

    def __init__(
        self,
        compressor: DeterministicCompressor | None = None,
    ) -> None:
        self._compressor = compressor or DeterministicCompressor()

    def optimize(
        self,
        items: list[ContextItem],
        budget: int = 4000,
    ) -> OptimizedContext:
        """Full optimization pipeline.

        AC-024-01..06, AC-024-10.
        """
        # Step 1: Filter expired/superseded
        valid_items = [i for i in items if i.is_valid]

        # Step 2: Deduplicate
        deduped = self._deduplicate(valid_items)

        # Step 3: Sort by priority
        sorted_items = sorted(deduped, key=lambda i: i.priority.value)

        # Step 4: Compress to fit budget
        compressed, compressed_count = self._compressor.compress_to_fit(
            sorted_items, budget
        )

        # Step 5: Enforce budget — drop lowest priority first (never P0/P1)
        final, dropped = self._enforce_budget(compressed, budget)

        # Step 6: Collect provenance
        provenance = []
        for item in final:
            provenance.extend(item.provenance)

        total_tokens = sum(i.token_count for i in final)

        return OptimizedContext(
            items=final,
            total_tokens=total_tokens,
            budget=budget,
            dropped_count=dropped,
            compressed_count=compressed_count,
            provenance=list(set(provenance)),
        )

    def _deduplicate(self, items: list[ContextItem]) -> list[ContextItem]:
        """Remove duplicates by content hash."""
        seen: dict[str, ContextItem] = {}
        for item in items:
            h = hashlib.sha256(item.content.lower().strip().encode()).hexdigest()[:16]
            if h not in seen:
                seen[h] = item
            elif item.priority.value < seen[h].priority.value:
                # Higher priority wins
                seen[h] = item
        return list(seen.values())

    def _enforce_budget(
        self,
        items: list[ContextItem],
        budget: int,
    ) -> tuple[list[ContextItem], int]:
        """Enforce budget by dropping lowest priority items.

        AC-024-03: P0/P1 never dropped.
        """
        total = sum(i.token_count for i in items)
        if total <= budget:
            return items, 0

        # Separate never-drop from droppable
        never_drop = [i for i in items if i.priority.never_drop]
        droppable = [i for i in items if not i.priority.never_drop]

        never_drop_tokens = sum(i.token_count for i in never_drop)
        remaining_budget = budget - never_drop_tokens

        # Drop from lowest priority first
        droppable.sort(key=lambda i: i.priority.value, reverse=True)
        kept: list[ContextItem] = []
        dropped = 0

        for item in droppable:
            if item.token_count <= remaining_budget:
                kept.append(item)
                remaining_budget -= item.token_count
            else:
                dropped += 1

        return never_drop + kept, dropped

    def classify_item(self, item: ContextItem) -> ContextPriority:
        """Classify an item's priority based on metadata."""
        if item.metadata.get("is_system"):
            return ContextPriority.P0_SYSTEM
        if item.metadata.get("is_critical"):
            return ContextPriority.P1_CRITICAL
        if item.metadata.get("is_task"):
            return ContextPriority.P2_TASK
        if item.source in ("conversation", "session"):
            return ContextPriority.P4_HISTORY
        if item.source == "knowledge":
            return ContextPriority.P3_MEMORY
        return ContextPriority.P6_LOW
