"""Benchmark and regression gate.

AC-033-01: Benchmark has clear baseline.
AC-033-02: No baseline → INCONCLUSIVE.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ComparisonResult(str, Enum):
    IMPROVED = "improved"
    REGRESSED = "regressed"
    STABLE = "stable"
    INCONCLUSIVE = "inconclusive"


@dataclass
class MetricComparison:
    """Comparison of a metric between baseline and current."""
    metric_name: str = ""
    baseline_value: float = 0.0
    current_value: float = 0.0
    threshold: float = 0.1
    result: ComparisonResult = ComparisonResult.STABLE

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_name": self.metric_name, "baseline_value": self.baseline_value,
            "current_value": self.current_value, "result": self.result.value,
        }


@dataclass
class BenchmarkRun:
    """A benchmark execution result."""
    benchmark_id: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {"benchmark_id": self.benchmark_id, "metrics": self.metrics}


class BaselineManager:
    """Manages benchmark baselines."""

    def __init__(self) -> None:
        self._baselines: dict[str, BenchmarkRun] = {}

    def set_baseline(self, name: str, run: BenchmarkRun) -> None:
        self._baselines[name] = run

    def get_baseline(self, name: str) -> BenchmarkRun | None:
        return self._baselines.get(name)

    def has_baseline(self, name: str) -> bool:
        return name in self._baselines


class RegressionDetector:
    """Detects regressions between baseline and current benchmark."""

    def detect(
        self,
        baseline: BenchmarkRun,
        current: BenchmarkRun,
        thresholds: dict[str, float] | None = None,
    ) -> list[MetricComparison]:
        """Compare baseline and current, return comparisons."""
        thresholds = thresholds or {}
        comparisons = []

        all_metrics = set(baseline.metrics) | set(current.metrics)
        for metric in all_metrics:
            b_val = baseline.metrics.get(metric, 0.0)
            c_val = current.metrics.get(metric, 0.0)
            threshold = thresholds.get(metric, 0.1)

            if b_val == 0 and c_val == 0:
                result = ComparisonResult.STABLE
            elif b_val == 0:
                result = ComparisonResult.INCONCLUSIVE
            else:
                change = (c_val - b_val) / abs(b_val)
                if change > threshold:
                    result = ComparisonResult.REGRESSED
                elif change < -threshold:
                    result = ComparisonResult.IMPROVED
                else:
                    result = ComparisonResult.STABLE

            comparisons.append(MetricComparison(
                metric_name=metric, baseline_value=b_val, current_value=c_val,
                threshold=threshold, result=result,
            ))

        return comparisons


class ReleaseGate:
    """Gate that blocks release if regressions detected."""

    def check(self, comparisons: list[MetricComparison]) -> dict[str, Any]:
        regressed = [c for c in comparisons if c.result == ComparisonResult.REGRESSED]
        return {
            "passed": len(regressed) == 0,
            "regressions": len(regressed),
            "total_compared": len(comparisons),
        }
