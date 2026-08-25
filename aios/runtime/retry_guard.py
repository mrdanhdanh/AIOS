"""RetryGuard — deterministic auto-stop on repeated identical failures (TASK-226).

Runtime-layer capability (compliant ARCH-001..004: lives in runtime, no agent
imports). Detects when the same failure signature repeats >= threshold and
halts with a root-cause report instead of looping "Try Again" / "thử lại".

This codifies the prose rule in AGENTS.md §12 ("auto-stop ngưỡng cụ thể":
stop after >=3 identical failures, report root cause, never loop). It is
deterministic and fail-closed: an invalid threshold raises; unknown signatures
are simply absent (no false stop).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


DEFAULT_THRESHOLD = 3


@dataclass
class FailureRecord:
    signature: str
    count: int = 0
    first_seen: str = ""
    last_message: str = ""


class RetryGuard:
    """Tracks failure signatures and triggers auto-stop at a repeat threshold."""

    def __init__(self, threshold: int = DEFAULT_THRESHOLD) -> None:
        if threshold < 1:
            raise ValueError("threshold must be >= 1")
        self.threshold = threshold
        self._records: Dict[str, FailureRecord] = {}

    def observe(self, signature: str, message: str = "", when: str = "") -> bool:
        """Record a failure. Returns True when auto-stop should trigger."""
        if not signature:
            raise ValueError("signature must be non-empty")
        rec = self._records.get(signature)
        if rec is None:
            rec = FailureRecord(signature=signature, first_seen=when)
            self._records[signature] = rec
        rec.count += 1
        rec.last_message = message
        return rec.count >= self.threshold

    def should_stop(self, signature: str) -> bool:
        rec = self._records.get(signature)
        return rec is not None and rec.count >= self.threshold

    def count(self, signature: str) -> int:
        rec = self._records.get(signature)
        return rec.count if rec is not None else 0

    def report(self, signature: str) -> str:
        rec = self._records.get(signature)
        if rec is None:
            return ""
        return (
            f"AUTO-STOP: identical failure '{signature}' repeated "
            f"{rec.count} times (threshold={self.threshold}). "
            f"Root cause: {rec.last_message or 'unknown'}. "
            f"Halting to avoid retry loop."
        )

    def reset(self, signature: str) -> None:
        self._records.pop(signature, None)
