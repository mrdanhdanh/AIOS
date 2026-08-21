"""Deterministic compression for context items.

AC-024-06: Deterministic compression before LLM.
AC-024-08: Provenance preserved after compression.
"""

from __future__ import annotations

from aios.context_optimizer.contracts import ContextItem


class DeterministicCompressor:
    """Compresses context items deterministically without LLM.

    Strategies: truncation, sentence extraction, key phrase extraction.
    """

    def truncate(self, item: ContextItem, max_tokens: int) -> ContextItem:
        """Truncate content to max_tokens while preserving provenance."""
        words = item.content.split()
        if len(words) <= max_tokens:
            return item
        truncated_words = words[:max_tokens]
        return ContextItem(
            item_id=item.item_id,
            priority=item.priority,
            content=" ".join(truncated_words) + " [...]",
            token_count=max_tokens,
            source=item.source,
            provenance=list(item.provenance),
            metadata={**item.metadata, "compressed": True, "strategy": "truncate"},
        )

    def extract_key_sentences(self, item: ContextItem, max_sentences: int = 3) -> ContextItem:
        """Extract first N sentences as summary."""
        sentences = [s.strip() for s in item.content.split(".") if s.strip()]
        if len(sentences) <= max_sentences:
            return item
        extracted = ". ".join(sentences[:max_sentences]) + "."
        token_count = max(1, len(extracted.split()))
        return ContextItem(
            item_id=item.item_id,
            priority=item.priority,
            content=extracted,
            token_count=token_count,
            source=item.source,
            provenance=list(item.provenance),
            metadata={**item.metadata, "compressed": True, "strategy": "extract"},
        )

    def compress_to_fit(
        self,
        items: list[ContextItem],
        budget: int,
    ) -> tuple[list[ContextItem], int]:
        """Compress items to fit within token budget.

        AC-024-06: Deterministic.
        AC-024-08: Provenance preserved.
        Returns (compressed_items, compressed_count).
        """
        total = sum(i.token_count for i in items)
        if total <= budget:
            return items, 0

        compressed_count = 0
        result: list[ContextItem] = []
        remaining_budget = budget

        # Sort by priority (lower = higher priority)
        sorted_items = sorted(items, key=lambda i: i.priority.value)

        for item in sorted_items:
            if item.priority.never_drop:
                # P0/P1: always keep, but compress if needed
                if item.token_count > remaining_budget:
                    compressed = self.truncate(item, remaining_budget)
                    result.append(compressed)
                    compressed_count += 1
                    remaining_budget = 0
                else:
                    result.append(item)
                    remaining_budget -= item.token_count
            else:
                if item.token_count <= remaining_budget:
                    result.append(item)
                    remaining_budget -= item.token_count
                else:
                    # Try to compress
                    if remaining_budget > 10:
                        compressed = self.truncate(item, remaining_budget)
                        result.append(compressed)
                        compressed_count += 1
                        remaining_budget = 0

        return result, compressed_count
