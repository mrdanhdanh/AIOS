"""TASK-188 — Benchmark Registry (M25).

Registers benchmarks with immutable ids. Fail-closed: duplicate id or empty
id raises EvaluationError; lookup of unknown id returns UNKNOWN (never PASS).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from aios.evaluation._common import EvaluationError, _hash


@dataclass(frozen=True)
class Benchmark:
    benchmark_id: str
    name: str
    suite: str

    def __post_init__(self) -> None:
        if not self.benchmark_id:
            raise EvaluationError("benchmark_id must be non-empty")
        if not self.name:
            raise EvaluationError("name must be non-empty")


@dataclass(frozen=True)
class RegistryReport:
    report_id: str
    registered: int
    found: Optional[str]
    status: str  # PASS | UNKNOWN


class BenchmarkRegistry:
    """Register and look up benchmarks deterministically."""

    def __init__(self) -> None:
        self._store: Dict[str, Benchmark] = {}

    def register(self, bench: Benchmark) -> RegistryReport:
        if not isinstance(bench, Benchmark):
            raise EvaluationError("bench must be a Benchmark")
        if bench.benchmark_id in self._store:
            raise EvaluationError(f"duplicate benchmark_id: {bench.benchmark_id}")
        self._store[bench.benchmark_id] = bench
        report_id = _hash(f"{bench.benchmark_id}|{len(self._store)}")
        return RegistryReport(report_id=report_id, registered=len(self._store), found=bench.benchmark_id, status="PASS")

    def lookup(self, benchmark_id: str) -> RegistryReport:
        if not benchmark_id:
            raise EvaluationError("benchmark_id must be non-empty")
        found = self._store.get(benchmark_id)
        status = "PASS" if found else "UNKNOWN"
        report_id = _hash(f"{benchmark_id}|{status}")
        return RegistryReport(report_id=report_id, registered=len(self._store), found=found.benchmark_id if found else None, status=status)
