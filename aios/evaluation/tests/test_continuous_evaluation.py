from aios.evaluation.continuous_evaluation import (
    ContinuousEvaluation,
    ContinuousReport,
)
from aios.evaluation.evaluation_engine import DimensionScore
from aios.evaluation._common import EvaluationError


def test_continuous_construction():
    c = ContinuousEvaluation()
    assert isinstance(c, ContinuousEvaluation)


def test_continuous_pass_integration():
    c = ContinuousEvaluation()
    rep = c.run("subj", [DimensionScore("correctness", 0.9, 0.8)], 0.9, 0.8)
    assert isinstance(rep, ContinuousReport)
    assert rep.status == "PASS"
    assert rep.components == 2


def test_continuous_insufficient_on_regression():
    c = ContinuousEvaluation()
    rep = c.run("subj", [DimensionScore("correctness", 0.9, 0.8)], 0.7, 0.8)
    assert rep.status == "INSUFFICIENT"


def test_continuous_unknown_on_empty_scores():
    c = ContinuousEvaluation()
    rep = c.run("subj", [], 0.9, 0.8)
    assert rep.status == "UNKNOWN"


def test_continuous_rejects_empty_subject():
    c = ContinuousEvaluation()
    try:
        c.run("", [DimensionScore("correctness", 0.9, 0.8)], 0.9, 0.8)
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_continuous_rejects_none_scores():
    c = ContinuousEvaluation()
    try:
        c.run("subj", None, 0.9, 0.8)
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_continuous_deterministic_report_id():
    c = ContinuousEvaluation()
    a = c.run("subj", [DimensionScore("c", 0.9, 0.8)], 0.9, 0.8)
    b = c.run("subj", [DimensionScore("c", 0.9, 0.8)], 0.9, 0.8)
    assert a.report_id == b.report_id
