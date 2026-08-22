"""Deterministic retention policy (TASK-057 §3).

TTL expiry + max-size eviction by RetentionPriority (TRUSTED > VERIFIED >
UNVERIFIED; newer > older). Eviction is deterministic — no semantic/LLM
ranking.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class RetentionPolicy:
    ttl_seconds: float = 86400.0 * 30
    max_size: int = 1000

    def is_expired(self, entry: Any) -> bool:
        created = getattr(entry, "created_at", 0.0)
        return (time.time() - float(created)) > self.ttl_seconds

    def priority(self, entry: Any) -> tuple[int, float]:
        """Higher tuple = higher priority (evicted last)."""
        trust = getattr(entry, "trust_status", None)
        verify = getattr(entry, "verification_status", None)
        score = 0
        if verify is not None and str(verify.value) == "verified":
            score += 1
        if trust is not None and str(trust.value) == "trusted":
            score += 2
        created = float(getattr(entry, "created_at", 0.0))
        return (score, created)

    def select_eviction(self, entries: list[Any]) -> Any | None:
        """Pick the lowest-priority entry to evict (deterministic)."""
        if not entries:
            return None
        return min(entries, key=self.priority)
