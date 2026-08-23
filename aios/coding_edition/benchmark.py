"""TASK-216 — Benchmark Gate (M26).

Gate benchmark results against a baseline, converging Benchmark (T195) and
Benchmark/Regression (T033). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from aios.coding_edition._common import CodingEditionError, _hash


class BenchmarkVerdict(str, Enum):
    """Benchmark outcome (T216)."""

    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


@dataclass
class BenchmarkResult:
    """A single benchmark measurement (T216)."""

    name: str
    value: float
    baseline: float
    higher_is_better: bool = True

    def __post_init__(self) -> None:
        if not self.name:
            raise CodingEditionError("benchmark name is required.")


class BenchmarkGate:
    """Deterministic benchmark gate (T216)."""

    def __init__(self, tolerance: float = 0.05) -> None:
        self._tolerance = tolerance

    def evaluate(self, results: List[BenchmarkResult]) -> BenchmarkVerdict:
        """Evaluate benchmark results against baselines (fail-closed)."""
        if not results:
            return BenchmarkVerdict.UNKNOWN
        for r in results:
            if r.higher_is_better:
                if r.value < r.baseline * (1.0 - self._tolerance):
                    return BenchmarkVerdict.FAIL
            else:
                if r.value > r.baseline * (1.0 + self._tolerance):
                    return BenchmarkVerdict.FAIL
        return BenchmarkVerdict.PASS

    def benchmark_hash(self, results: List[BenchmarkResult]) -> str:
        v = self.evaluate(results)
        payload = "|".join(f"{r.name}:{r.value:.4f}:{r.baseline:.4f}" for r in results)
        return _hash(f"{v.value}|{payload}")
