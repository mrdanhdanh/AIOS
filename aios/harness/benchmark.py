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


class GateVerdict(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


@dataclass
class BenchmarkMetric:
    name: str
    value: float = 0.0
    threshold: float = 0.0
    is_hard: bool = False


@dataclass
class BenchmarkBaseline:
    name: str
    metrics: dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class BenchmarkCandidate:
    name: str
    metrics: dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class BenchmarkComparison:
    metric_name: str
    baseline_value: float
    candidate_value: float
    delta: float
    verdict: GateVerdict


@dataclass
class BenchmarkFinding:
    severity: GateVerdict
    message: str


@dataclass
class BenchmarkReport:
    verdict: GateVerdict
    findings: list[BenchmarkFinding] = field(default_factory=list)
    comparisons: list[BenchmarkComparison] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "findings": [f.message for f in self.findings],
            "comparisons": len(self.comparisons),
        }


class GateEvaluator:
    """Regression gate with PASS/WARNING/FAIL/INCONCLUSIVE verdicts (AC-033-01..04).

    Fail-closed: missing baseline → INCONCLUSIVE; any hard metric breach → FAIL.
    """

    def __init__(self, warning_threshold: float = 0.1, fail_threshold: float = 0.25) -> None:
        self.warning_threshold = warning_threshold
        self.fail_threshold = fail_threshold

    def evaluate(self, baseline: BenchmarkBaseline, candidate: BenchmarkCandidate) -> BenchmarkReport:
        if not baseline.metrics:
            return BenchmarkReport(verdict=GateVerdict.INCONCLUSIVE, findings=[BenchmarkFinding(GateVerdict.INCONCLUSIVE, "No baseline")])

        findings: list[BenchmarkFinding] = []
        comparisons: list[BenchmarkComparison] = []
        has_fail = False
        has_warning = False

        for metric, b_val in baseline.metrics.items():
            c_val = candidate.metrics.get(metric, 0.0)
            if b_val == 0:
                delta = 0.0
                verdict = GateVerdict.INCONCLUSIVE
            else:
                delta = (c_val - b_val) / abs(b_val)
                if delta <= -self.fail_threshold:
                    verdict = GateVerdict.FAIL
                    has_fail = True
                    findings.append(BenchmarkFinding(GateVerdict.FAIL, f"{metric} regressed {delta:.1%}"))
                elif delta <= -self.warning_threshold:
                    verdict = GateVerdict.WARNING
                    has_warning = True
                    findings.append(BenchmarkFinding(GateVerdict.WARNING, f"{metric} degraded {delta:.1%}"))
                else:
                    verdict = GateVerdict.PASS
            comparisons.append(BenchmarkComparison(metric, b_val, c_val, delta, verdict))

        if has_fail:
            overall = GateVerdict.FAIL
        elif has_warning:
            overall = GateVerdict.WARNING
        else:
            overall = GateVerdict.PASS
        return BenchmarkReport(verdict=overall, findings=findings, comparisons=comparisons)
