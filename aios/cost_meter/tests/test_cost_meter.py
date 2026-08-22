"""Tests for TASK-075 cost metering + performance budget (T069 SLO)."""

from __future__ import annotations

import pytest

from aios.cost_meter import (
    CostExceeded,
    CostMeter,
    PerformanceBudget,
    SLO,
    SLOViolation,
)


class TestCostMeter:
    def test_record_per_step_and_goal(self) -> None:
        meter = CostMeter(budget=1.0, goal_id="g1")
        r1 = meter.record("s1", 0.1, "provider-a", evidence_ref="ev:1")
        r2 = meter.record("s2", 0.2, "provider-b", evidence_ref="ev:2")
        assert meter.spent() == pytest.approx(0.3)
        assert meter.remaining() == pytest.approx(0.7)
        assert len(meter.records()) == 2
        assert r1.goal_id == "g1" and r1.step_id == "s1"

    def test_budget_exceeded_escalate_stop(self) -> None:
        # AC2: cost exceeds budget -> escalate/stop (fail-closed).
        meter = CostMeter(budget=0.25, goal_id="g1")
        meter.record("s1", 0.1, "provider-a")
        meter.record("s2", 0.1, "provider-a")
        with pytest.raises(CostExceeded):
            meter.record("s3", 0.1, "provider-a")
        # Spend is not silently allowed to grow past the budget.
        assert meter.spent() == pytest.approx(0.2)
        assert meter.is_over_budget() is False

    def test_negative_budget_rejected(self) -> None:
        with pytest.raises(ValueError):
            CostMeter(budget=-1.0)

    def test_evidence_ref_provenance(self) -> None:
        # AC6: every cost record has provenance evidence.
        meter = CostMeter(budget=10.0)
        rec = meter.record("s1", 0.01, "provider-a", evidence_ref="ev:abc")
        assert rec.evidence_ref == "ev:abc"


class TestPerformanceBudget:
    def test_within_slo_passes(self) -> None:
        # AC3: perf within SLO.
        pb = PerformanceBudget(SLO(max_latency_ms=200.0, min_throughput=5.0))
        pb.assert_within(latency_ms=150.0, throughput=10.0)

    def test_latency_slo_violation(self) -> None:
        pb = PerformanceBudget(SLO(max_latency_ms=200.0))
        with pytest.raises(SLOViolation):
            pb.assert_within(latency_ms=500.0)

    def test_throughput_slo_violation(self) -> None:
        pb = PerformanceBudget(SLO(min_throughput=5.0))
        with pytest.raises(SLOViolation):
            pb.assert_within(latency_ms=10.0, throughput=1.0)

    def test_check_helpers(self) -> None:
        pb = PerformanceBudget(SLO(max_latency_ms=100.0, min_throughput=2.0))
        assert pb.check_latency(50.0) is True
        assert pb.check_latency(150.0) is False
        assert pb.check_throughput(3.0) is True
        assert pb.check_throughput(1.0) is False
