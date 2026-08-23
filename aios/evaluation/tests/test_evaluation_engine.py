from aios.evaluation.evaluation_engine import (
    DimensionScore,
    EvaluationEngine,
    ScoreReport,
)
from aios.evaluation._common import EvaluationError


def test_engine_construction():
    e = EvaluationEngine()
    assert isinstance(e, EvaluationEngine)


def test_engine_score_pass():
    e = EvaluationEngine()
    rep = e.score([DimensionScore("correctness", 0.9, 0.8), DimensionScore("robustness", 0.85, 0.7)])
    assert isinstance(rep, ScoreReport)
    assert rep.status == "PASS"
    assert rep.below == ()


def test_engine_score_insufficient_below_threshold():
    e = EvaluationEngine()
    rep = e.score([DimensionScore("correctness", 0.9, 0.8), DimensionScore("robustness", 0.5, 0.7)])
    assert rep.status == "INSUFFICIENT"
    assert "robustness" in rep.below


def test_engine_score_unknown_when_empty():
    e = EvaluationEngine()
    rep = e.score([])
    assert rep.status == "UNKNOWN"


def test_engine_rejects_score_out_of_range():
    e = EvaluationEngine()
    try:
        e.score([DimensionScore("correctness", 1.5, 0.8)])
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_engine_rejects_non_score():
    e = EvaluationEngine()
    try:
        e.score(["not-a-score"])
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_engine_deterministic_report_id():
    e = EvaluationEngine()
    a = e.score([DimensionScore("correctness", 0.9, 0.8)])
    b = e.score([DimensionScore("correctness", 0.9, 0.8)])
    assert a.report_id == b.report_id
