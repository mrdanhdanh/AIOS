from aios.evaluation.failure_attribution import (
    AttributionReport,
    Failure,
    FailureAttributor,
)
from aios.evaluation._common import EvaluationError


def test_failure_construction_immutable():
    f = Failure("F1", "crash", "logic")
    assert f.failure_id == "F1"


def test_failure_attributed_known_cause():
    a = FailureAttributor()
    rep = a.attribute(Failure("F1", "crash", "logic"))
    assert isinstance(rep, AttributionReport)
    assert rep.status == "ATTRIBUTED"
    assert rep.cause == "logic"


def test_failure_unknown_when_cause_unknown():
    a = FailureAttributor()
    rep = a.attribute(Failure("F1", "crash", "unknown"))
    assert rep.status == "UNKNOWN"
    assert rep.cause == "unknown"


def test_failure_rejects_empty_id():
    a = FailureAttributor()
    try:
        a.attribute(Failure("", "crash", "logic"))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_failure_rejects_empty_symptom():
    a = FailureAttributor()
    try:
        a.attribute(Failure("F1", "", "logic"))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_failure_rejects_non_failure():
    a = FailureAttributor()
    try:
        a.attribute("not-a-failure")
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_failure_deterministic_report_id():
    a = FailureAttributor()
    b1 = a.attribute(Failure("F1", "crash", "logic"))
    b2 = a.attribute(Failure("F1", "crash", "logic"))
    assert b1.report_id == b2.report_id
