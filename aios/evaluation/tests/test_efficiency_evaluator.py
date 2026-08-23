from aios.evaluation.efficiency_evaluator import (
    EfficiencyBudget,
    EfficiencyEvaluator,
    EfficiencyReport,
)
from aios.evaluation._common import EvaluationError


def test_efficiency_construction_immutable():
    b = EfficiencyBudget("B1", 100.0, 200.0)
    assert b.budget_id == "B1"


def test_efficiency_pass_within_budget():
    e = EfficiencyEvaluator()
    rep = e.evaluate(EfficiencyBudget("B1", 100.0, 200.0))
    assert isinstance(rep, EfficiencyReport)
    assert rep.status == "PASS"


def test_efficiency_insufficient_over_budget():
    e = EfficiencyEvaluator()
    rep = e.evaluate(EfficiencyBudget("B1", 300.0, 200.0))
    assert rep.status == "INSUFFICIENT"


def test_efficiency_rejects_empty_id():
    e = EfficiencyEvaluator()
    try:
        e.evaluate(EfficiencyBudget("", 100.0, 200.0))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_efficiency_rejects_negative_limit():
    e = EfficiencyEvaluator()
    try:
        e.evaluate(EfficiencyBudget("B1", 100.0, -1.0))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_efficiency_rejects_non_budget():
    e = EfficiencyEvaluator()
    try:
        e.evaluate("not-a-budget")
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_efficiency_deterministic_report_id():
    e = EfficiencyEvaluator()
    a = e.evaluate(EfficiencyBudget("B1", 100.0, 200.0))
    b = e.evaluate(EfficiencyBudget("B1", 100.0, 200.0))
    assert a.report_id == b.report_id
