from aios.evaluation.baseline_manager import (
    Baseline,
    BaselineManager,
    BaselineReport,
)
from aios.evaluation._common import EvaluationError


def test_baseline_construction_immutable():
    b = Baseline("subj", 0.8)
    assert b.subject == "subj"


def test_baseline_set_and_get_pass():
    m = BaselineManager()
    m.set_baseline(Baseline("subj", 0.8))
    rep = m.get_baseline("subj")
    assert isinstance(rep, BaselineReport)
    assert rep.status == "PASS"
    assert rep.value == 0.8


def test_baseline_get_unknown_when_missing():
    m = BaselineManager()
    rep = m.get_baseline("missing")
    assert rep.status == "UNKNOWN"
    assert rep.value is None


def test_baseline_rejects_empty_subject():
    m = BaselineManager()
    try:
        m.set_baseline(Baseline("", 0.8))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_baseline_get_rejects_empty_subject():
    m = BaselineManager()
    try:
        m.get_baseline("")
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_baseline_rejects_non_baseline():
    m = BaselineManager()
    try:
        m.set_baseline("not-a-baseline")
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_baseline_deterministic_report_id():
    m = BaselineManager()
    a = m.set_baseline(Baseline("subj", 0.8))
    b = BaselineManager().set_baseline(Baseline("subj", 0.8))
    assert a.report_id == b.report_id
