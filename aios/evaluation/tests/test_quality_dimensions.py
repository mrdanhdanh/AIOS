from aios.evaluation.quality_dimensions import (
    DimensionReport,
    QualityDimension,
    QualityDimensionEvaluator,
)
from aios.evaluation._common import EvaluationError


def test_dimension_construction_immutable():
    d = QualityDimension("D1", "correctness", 0.3, 0.8)
    assert d.dimension_id == "D1"


def test_dimension_pass_when_above_threshold():
    ev = QualityDimensionEvaluator()
    rep = ev.evaluate(QualityDimension("D1", "correctness", 0.3, 0.8), 0.9)
    assert isinstance(rep, DimensionReport)
    assert rep.status == "PASS"


def test_dimension_insufficient_below_threshold():
    ev = QualityDimensionEvaluator()
    rep = ev.evaluate(QualityDimension("D1", "correctness", 0.3, 0.8), 0.5)
    assert rep.status == "INSUFFICIENT"


def test_dimension_rejects_weight_out_of_range():
    ev = QualityDimensionEvaluator()
    try:
        ev.evaluate(QualityDimension("D1", "correctness", 1.5, 0.8), 0.9)
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_dimension_rejects_value_out_of_range():
    ev = QualityDimensionEvaluator()
    try:
        ev.evaluate(QualityDimension("D1", "correctness", 0.3, 0.8), 1.5)
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_dimension_rejects_non_dimension():
    ev = QualityDimensionEvaluator()
    try:
        ev.evaluate("not-a-dimension", 0.9)
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_dimension_deterministic_report_id():
    ev = QualityDimensionEvaluator()
    a = ev.evaluate(QualityDimension("D1", "correctness", 0.3, 0.8), 0.9)
    b = ev.evaluate(QualityDimension("D1", "correctness", 0.3, 0.8), 0.9)
    assert a.report_id == b.report_id
