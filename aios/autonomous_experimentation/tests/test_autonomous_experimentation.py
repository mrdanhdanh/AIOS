"""Tests for TASK-058 Autonomous Experimentation."""
from __future__ import annotations

from aios.autonomous_experimentation.contracts import ExperimentStatus, MetricSpec
from aios.autonomous_experimentation.controller import ExperimentController


def _ctrl(**kw):
    return ExperimentController(**kw)


def test_propose_rejects_vague_metric():
    c = _ctrl()
    exp, err = c.propose("make it better", "b", "v1", "c", "v2", "s", [])
    assert exp is None
    assert "metric_spec" in err


def test_propose_rejects_mutable_baseline_version():
    c = _ctrl()
    exp, err = c.propose("improve latency", "b", "latest", "c", "v2", "s",
                         [MetricSpec("latency", "decrease", 0.1)])
    assert exp is None
    assert "immutable" in err


def test_propose_accepts_valid_experiment():
    c = _ctrl()
    exp, err = c.propose("reduce latency by 10%", "b", "v1", "c", "v2", "s",
                         [MetricSpec("latency", "decrease", 0.1)])
    assert exp is not None
    assert exp.status == ExperimentStatus.PROPOSED


def test_governor_denial_blocks():
    c = _ctrl(governor_allow=lambda e: False)
    exp, _ = c.propose("reduce latency", "b", "v1", "c", "v2", "s",
                       [MetricSpec("latency", "decrease", 0.1)])
    st = c.authorize(exp)
    assert st == ExperimentStatus.REJECTED


def test_promotion_ready_when_improved_no_regression_policy_pass():
    c = _ctrl()
    exp, _ = c.propose("reduce latency", "b", "v1", "c", "v2", "s",
                       [MetricSpec("latency", "decrease", 0.1)])
    c.authorize(exp)
    base = {"latency": 1.0, "cost": 1.0, "failure": 0.0}
    cand = {"latency": 0.8, "cost": 1.0, "failure": 0.0, "verdict": "pass"}
    d = c.evaluate(exp, base, cand, policy_pass=True)
    assert d.decision == "PROMOTION_READY"


def test_not_promoted_on_cost_regression():
    c = _ctrl()
    exp, _ = c.propose("reduce latency", "b", "v1", "c", "v2", "s",
                       [MetricSpec("latency", "decrease", 0.1)])
    c.authorize(exp)
    base = {"latency": 1.0, "cost": 1.0}
    cand = {"latency": 0.8, "cost": 3.0, "verdict": "pass"}  # cost +200%
    d = c.evaluate(exp, base, cand, policy_pass=True)
    assert d.decision == "NOT_PROMOTED"
    assert "regression" in d.reason


def test_inconclusive_not_promoted():
    c = _ctrl()
    exp, _ = c.propose("reduce latency", "b", "v1", "c", "v2", "s",
                       [MetricSpec("latency", "decrease", 0.1)])
    c.authorize(exp)
    base = {"latency": 1.0}
    cand = {"latency": 0.8, "verdict": "inconclusive"}
    d = c.evaluate(exp, base, cand, policy_pass=True)
    assert d.decision == "NOT_PROMOTED"


def test_policy_fail_not_promoted():
    c = _ctrl()
    exp, _ = c.propose("reduce latency", "b", "v1", "c", "v2", "s",
                       [MetricSpec("latency", "decrease", 0.1)])
    c.authorize(exp)
    base = {"latency": 1.0}
    cand = {"latency": 0.8, "verdict": "pass"}
    d = c.evaluate(exp, base, cand, policy_pass=False)
    assert d.decision == "NOT_PROMOTED"


def test_run_uses_harness_only():
    called = {"n": 0}
    def harness(e):
        called["n"] += 1
        return {"verdict": "pass", "latency": 0.8}
    c = _ctrl(harness_run=harness)
    exp, _ = c.propose("reduce latency", "b", "v1", "c", "v2", "s",
                       [MetricSpec("latency", "decrease", 0.1)])
    c.authorize(exp)
    res = c.run(exp)
    assert called["n"] == 1
    assert exp.status == ExperimentStatus.EVALUATED
