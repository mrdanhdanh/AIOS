from aios.adversarial.collusion_detector import (
    CollusionDetector,
    CollusionReport,
    ResilienceReport,
    AttackCorpusRegression,
)
from aios.adversarial.adversarial_evaluation import AttackResult, BLOCKED, BREACH
from aios.adversarial._common import AdversarialError


def _r(aid, status):
    return AttackResult(aid, "t", status)


def test_detect_construction():
    rep = _r("A1", BLOCKED)
    assert rep.attack_id == "A1"


def test_detect_collusion_when_multiple_breaches():
    d = CollusionDetector()
    rep = d.detect([_r("A1", BREACH), _r("A2", BREACH), _r("A3", BLOCKED)])
    assert isinstance(rep, CollusionReport)
    assert rep.collusion_detected is True
    assert rep.status == "INSUFFICIENT"


def test_detect_no_collusion_single_breach():
    d = CollusionDetector()
    rep = d.detect([_r("A1", BREACH), _r("A2", BLOCKED)])
    assert rep.collusion_detected is False
    assert rep.status == "PASS"


def test_score_resilience_high():
    d = CollusionDetector()
    rep = d.score_resilience([_r("A1", BLOCKED), _r("A2", BLOCKED), _r("A3", BLOCKED), _r("A4", BLOCKED), _r("A5", BLOCKED)])
    assert isinstance(rep, ResilienceReport)
    assert rep.score == 1.0
    assert rep.status == "PASS"


def test_score_resilience_low():
    d = CollusionDetector()
    rep = d.score_resilience([_r("A1", BREACH), _r("A2", BLOCKED)])
    assert rep.score == 0.5
    assert rep.status == "INSUFFICIENT"


def test_corpus_regression_detected():
    d = CollusionDetector()
    rep = d.check_corpus_regression(baseline=10, current=8)
    assert isinstance(rep, AttackCorpusRegression)
    assert rep.regressed is True
    assert rep.status == "INSUFFICIENT"


def test_detect_rejects_empty_attack_id():
    d = CollusionDetector()
    try:
        d.detect([AttackResult("", "t", BLOCKED)])
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass
