from aios.evaluation.agent_behavior_evaluator import (
    AgentBehaviorEvaluator,
    BehaviorEvalReport,
    BehaviorSpec,
)
from aios.evaluation._common import EvaluationError


def test_behavior_construction_immutable():
    s = BehaviorSpec("S1", "expected", "actual")
    assert s.spec_id == "S1"


def test_behavior_pass_on_match():
    e = AgentBehaviorEvaluator()
    rep = e.evaluate(BehaviorSpec("S1", "ok", "ok"))
    assert isinstance(rep, BehaviorEvalReport)
    assert rep.status == "PASS"


def test_behavior_insufficient_on_mismatch():
    e = AgentBehaviorEvaluator()
    rep = e.evaluate(BehaviorSpec("S1", "ok", "fail"))
    assert rep.status == "INSUFFICIENT"


def test_behavior_rejects_empty_id():
    e = AgentBehaviorEvaluator()
    try:
        e.evaluate(BehaviorSpec("", "ok", "ok"))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_behavior_rejects_non_spec():
    e = AgentBehaviorEvaluator()
    try:
        e.evaluate("not-a-spec")
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_behavior_match_with_complex_values():
    e = AgentBehaviorEvaluator()
    rep = e.evaluate(BehaviorSpec("S1", {"a": 1}, {"a": 1}))
    assert rep.status == "PASS"


def test_behavior_deterministic_report_id():
    e = AgentBehaviorEvaluator()
    a = e.evaluate(BehaviorSpec("S1", "ok", "ok"))
    b = e.evaluate(BehaviorSpec("S1", "ok", "ok"))
    assert a.report_id == b.report_id
