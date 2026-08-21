"""Tests for benchmark and regression gate."""

from __future__ import annotations

from aios.harness.benchmark import BaselineManager, BenchmarkRun, ComparisonResult, RegressionDetector, ReleaseGate


class TestBenchmark:
    def test_baseline_manager(self) -> None:
        bm = BaselineManager()
        run = BenchmarkRun(benchmark_id="b1", metrics={"quality": 0.9})
        bm.set_baseline("v1", run)
        assert bm.has_baseline("v1")
        assert bm.get_baseline("v1").metrics["quality"] == 0.9

    def test_no_baseline(self) -> None:
        bm = BaselineManager()
        assert bm.has_baseline("nonexistent") is False

    def test_regression_detection(self) -> None:
        detector = RegressionDetector()
        baseline = BenchmarkRun(metrics={"latency": 100, "quality": 0.9})
        current = BenchmarkRun(metrics={"latency": 150, "quality": 0.85})
        comparisons = detector.detect(baseline, current, {"latency": 0.1, "quality": 0.1})
        assert len(comparisons) == 2
        latency_comp = [c for c in comparisons if c.metric_name == "latency"][0]
        assert latency_comp.result == ComparisonResult.REGRESSED

    def test_no_regression(self) -> None:
        detector = RegressionDetector()
        baseline = BenchmarkRun(metrics={"quality": 0.9})
        current = BenchmarkRun(metrics={"quality": 0.91})
        comparisons = detector.detect(baseline, current)
        assert all(c.result != ComparisonResult.REGRESSED for c in comparisons)

    def test_release_gate_pass(self) -> None:
        gate = ReleaseGate()
        comparisons = [
            __import__("aios.harness.benchmark", fromlist=["MetricComparison"]).MetricComparison(result=ComparisonResult.STABLE),
        ]
        result = gate.check(comparisons)
        assert result["passed"] is True

    def test_release_gate_fail(self) -> None:
        from aios.harness.benchmark import MetricComparison
        gate = ReleaseGate()
        comparisons = [MetricComparison(result=ComparisonResult.REGRESSED)]
        result = gate.check(comparisons)
        assert result["passed"] is False
