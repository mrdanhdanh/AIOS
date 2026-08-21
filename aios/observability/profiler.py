"""Performance profiler.

AC-021-04: Performance bottleneck identifiable.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProfileResult:
    """Result of a profiling operation."""

    operation: str
    duration_ms: float
    start_time: float
    end_time: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "duration_ms": self.duration_ms,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "metadata": self.metadata,
        }


class ProfilerService:
    """Performance profiler for identifying bottlenecks.

    AC-021-04: Performance bottleneck identifiable.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._results: list[ProfileResult] = []
        self._active: dict[str, float] = {}

    def start(self, operation: str) -> None:
        """Start profiling an operation."""
        with self._lock:
            self._active[operation] = time.time()

    def stop(self, operation: str, metadata: dict[str, Any] | None = None) -> ProfileResult | None:
        """Stop profiling and record result."""
        with self._lock:
            start = self._active.pop(operation, None)
        if start is None:
            return None
        end = time.time()
        result = ProfileResult(
            operation=operation,
            duration_ms=(end - start) * 1000,
            start_time=start,
            end_time=end,
            metadata=metadata or {},
        )
        with self._lock:
            self._results.append(result)
        return result

    def get_slowest(self, limit: int = 10) -> list[ProfileResult]:
        """Get slowest operations."""
        with self._lock:
            sorted_results = sorted(self._results, key=lambda r: r.duration_ms, reverse=True)
        return sorted_results[:limit]

    def get_by_operation(self, operation: str) -> list[ProfileResult]:
        """Get all results for a specific operation."""
        with self._lock:
            return [r for r in self._results if r.operation == operation]

    def summary(self) -> dict[str, Any]:
        """Get profiling summary."""
        with self._lock:
            if not self._results:
                return {"total_operations": 0}
            durations = [r.duration_ms for r in self._results]
            return {
                "total_operations": len(self._results),
                "total_duration_ms": sum(durations),
                "avg_duration_ms": sum(durations) / len(durations),
                "max_duration_ms": max(durations),
                "min_duration_ms": min(durations),
            }

    def count(self) -> int:
        with self._lock:
            return len(self._results)
