"""Performance budget / SLO checks (TASK-075; integrates T069 SLO).

``aios/reliability`` (T069) is not present in this codebase, so the SLO check
lives here as a lightweight, fail-closed budget used by the routing layer.
"""

from __future__ import annotations

from dataclasses import dataclass


class SLOViolation(Exception):
    """Raised when latency/throughput exceeds the SLO (fail-closed)."""


@dataclass
class SLO:
    max_latency_ms: float = float("inf")
    min_throughput: float = 0.0  # operations per second


class PerformanceBudget:
    """Checks latency/throughput against an SLO (fail-closed)."""

    def __init__(self, slo: SLO | None = None) -> None:
        self._slo = slo or SLO()

    def check_latency(self, latency_ms: float) -> bool:
        return latency_ms <= self._slo.max_latency_ms

    def check_throughput(self, throughput: float) -> bool:
        return throughput >= self._slo.min_throughput

    def assert_within(self, latency_ms: float, throughput: float = float("inf")) -> None:
        if not self.check_latency(latency_ms):
            raise SLOViolation(
                f"Latency {latency_ms}ms exceeds SLO max {self._slo.max_latency_ms}ms"
            )
        if not self.check_throughput(throughput):
            raise SLOViolation(
                f"Throughput {throughput} below SLO min {self._slo.min_throughput}/s"
            )
