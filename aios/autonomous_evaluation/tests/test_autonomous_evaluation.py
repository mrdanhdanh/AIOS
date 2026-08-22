"""Tests for TASK-060 Autonomous Evaluation."""
from __future__ import annotations

from aios.autonomous_evaluation.contracts import Decision, DecisionPolicy
from aios.autonomous_evaluation.evaluator import (
    DecisionMapper,
    LoopGate,
    StepEvaluator,
    evaluate_step,
)
from aios.harness.evaluation import EvalVerdict


def test_pass_authorizes_continue():
    ev = StepEvaluator().evaluate("s1", [{"name": "q", "value": 1.0, "threshold": 0.5}], "ev:1")
    assert ev == EvalVerdict.PASS
    d = DecisionMapper().map(ev)
    assert d == Decision.CONTINUE


def test_fail_hard_maps_to_recover():
    ev = StepEvaluator().evaluate("s1", [{"name": "q", "value": 0.1, "threshold": 0.5, "is_hard": True}], "ev:1")
    assert ev == EvalVerdict.FAIL
    d = DecisionMapper().map(ev)
    assert d == Decision.RECOVER


def test_warning_policy_driven_not_hardcoded():
    ev = StepEvaluator().evaluate("s1", [{"name": "q", "value": 0.4, "threshold": 0.5}], "ev:1")
    assert ev == EvalVerdict.WARNING
    # minor warning -> continue
    d1 = DecisionMapper().map(ev, {"quality_degradation": False})
    assert d1 == Decision.CONTINUE
    # degradation -> revise (policy-driven)
    d2 = DecisionMapper().map(ev, {"quality_degradation": True})
    assert d2 == Decision.REVISE


def test_inconclusive_never_promotes():
    ev = StepEvaluator().evaluate("s1", [{"name": "q", "value": 0.4, "threshold": 0.5}], "")
    assert ev == EvalVerdict.INCONCLUSIVE
    d = DecisionMapper().map(ev)
    assert d in (Decision.ESCALATE, Decision.REVISE, Decision.SAFE_STOP)
    assert d != Decision.CONTINUE


def test_missing_evidence_inconclusive():
    ev = StepEvaluator().evaluate("s1", [{"name": "q", "value": 1.0, "threshold": 0.5}], "")
    assert ev == EvalVerdict.INCONCLUSIVE


def test_loop_gate_blocks_on_budget():
    g = LoopGate()
    final, gov = g.gate(Decision.CONTINUE, {"budget_exceeded": True})
    assert final == Decision.BLOCK
    assert gov == "budget_exceeded"


def test_loop_gate_governor_escalate():
    def gov(decision, ctx):
        return "ESCALATE"
    g = LoopGate(governor_decision=gov)
    final, gov_v = g.gate(Decision.CONTINUE, {})
    assert final == Decision.ESCALATE


def test_loop_gate_governor_allow():
    def gov(decision, ctx):
        return "ALLOW"
    g = LoopGate(governor_decision=gov)
    final, gov_v = g.gate(Decision.RECOVER, {})
    assert final == Decision.RECOVER
    assert gov_v == "allowed"


def test_end_to_end_evaluate_step():
    rec = evaluate_step("s1", [{"name": "q", "value": 1.0, "threshold": 0.5}], "ev:1",
                        context={}, governor=lambda d, c: "ALLOW")
    assert rec.verdict == "pass"
    assert rec.decision_candidate == Decision.CONTINUE
    assert rec.governor_verdict == "allowed"


def test_deterministic_same_input_same_verdict():
    m = [{"name": "q", "value": 0.1, "threshold": 0.5, "is_hard": True}]
    r1 = evaluate_step("s", m, "ev:1", context={}, governor=lambda d, c: "ALLOW")
    r2 = evaluate_step("s", m, "ev:1", context={}, governor=lambda d, c: "ALLOW")
    assert r1.verdict == r2.verdict == "fail"
    assert r1.decision_candidate == r2.decision_candidate == Decision.RECOVER
