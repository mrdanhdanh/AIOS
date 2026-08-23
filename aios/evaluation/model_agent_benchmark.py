"""TASK-195 — Model / Agent Benchmark (M25).

Runs a benchmark suite and aggregates results. Based on Adversarial Evaluation
pattern T165. Constants: BREACH / UNKNOWN. BREACH present -> INSUFFICIENT;
UNKNOWN present -> UNKNOWN; else PASS.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.evaluation._common import EvaluationError, _hash

BREACH = "BREACH"
UNKNOWN = "UNKNOWN"
PASS = "PASS"
INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class BenchmarkResult:
    result_id: str
    name: str
    status: str  # PASS | BREACH | UNKNOWN

    def __post_init__(self) -> None:
        if not self.result_id:
            raise EvaluationError("result_id must be non-empty")
        if self.status not in (PASS, BREACH, UNKNOWN):
            raise EvaluationError(f"invalid status: {self.status}")


@dataclass(frozen=True)
class BenchmarkReport:
    report_id: str
    total: int
    breaches: int
    status: str


class ModelAgentBenchmark:
    """Run a benchmark suite and aggregate results."""

    def run(self, results: List[BenchmarkResult]) -> BenchmarkReport:
        if results is None:
            raise EvaluationError("results must be provided")
        for r in results:
            if not isinstance(r, BenchmarkResult):
                raise EvaluationError("each result must be a BenchmarkResult")
        total = len(results)
        breaches = sum(1 for r in results if r.status == BREACH)
        if any(r.status == BREACH for r in results):
            status = INSUFFICIENT
        elif any(r.status == UNKNOWN for r in results):
            status = UNKNOWN
        else:
            status = PASS
        report_id = _hash(f"{total}|{breaches}|{status}")
        return BenchmarkReport(report_id=report_id, total=total, breaches=breaches, status=status)
