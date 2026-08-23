from aios.adversarial.adversarial_evaluation import (
    AdversarialEvaluationHarness,
    AdversarialReport,
    AttackResult,
    BLOCKED,
    BREACH,
    UNKNOWN,
)
from aios.adversarial._common import AdversarialError


def _r(aid, status):
    return AttackResult(aid, "type", status)


def test_report_construction():
    rep = _r("A1", BLOCKED)
    assert rep.attack_id == "A1"


def test_evaluate_pass_when_all_blocked():
    h = AdversarialEvaluationHarness()
    rep = h.evaluate([_r("A1", BLOCKED), _r("A2", BLOCKED)])
    assert isinstance(rep, AdversarialReport)
    assert rep.breached is False
    assert rep.status == "PASS"


def test_evaluate_insufficient_on_breach():
    h = AdversarialEvaluationHarness()
    rep = h.evaluate([_r("A1", BLOCKED), _r("A2", BREACH)])
    assert rep.breached is True
    assert rep.status == "INSUFFICIENT"


def test_evaluate_unknown_when_inconclusive():
    h = AdversarialEvaluationHarness()
    rep = h.evaluate([_r("A1", BLOCKED), _r("A2", UNKNOWN)])
    assert rep.status == UNKNOWN


def test_evaluate_rejects_empty_attack_id():
    h = AdversarialEvaluationHarness()
    try:
        h.evaluate([AttackResult("", "t", BLOCKED)])
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_evaluate_rejects_empty_results():
    h = AdversarialEvaluationHarness()
    try:
        h.evaluate([])
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_evaluate_deterministic_report_id():
    h = AdversarialEvaluationHarness()
    a = h.evaluate([_r("A1", BLOCKED), _r("A2", BLOCKED)])
    b = h.evaluate([_r("A1", BLOCKED), _r("A2", BLOCKED)])
    assert a.report_id == b.report_id
