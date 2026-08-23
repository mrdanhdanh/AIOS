from aios.adversarial.evidence_attackers import (
    EvidenceAttack,
    EvidenceAttacker,
    EvidenceAttackResult,
    BLOCKED,
    BREACH,
)
from aios.adversarial._common import AdversarialError


def test_attack_construction():
    a = EvidenceAttack("E1", tampered=True, detected=True)
    assert a.attack_id == "E1"


def test_attack_blocked_when_detected():
    at = EvidenceAttacker()
    res = at.attack(EvidenceAttack("E1", tampered=True, detected=True))
    assert isinstance(res, EvidenceAttackResult)
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_breach_when_undetected():
    at = EvidenceAttacker()
    res = at.attack(EvidenceAttack("E1", tampered=True, detected=False))
    assert res.breached is True
    assert res.status == BREACH


def test_attack_blocked_when_not_tampered():
    at = EvidenceAttacker()
    res = at.attack(EvidenceAttack("E1", tampered=False, detected=False))
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_rejects_empty_id():
    at = EvidenceAttacker()
    try:
        at.attack(EvidenceAttack("", tampered=True, detected=False))
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_rejects_non_attack():
    at = EvidenceAttacker()
    try:
        at.attack("not-an-attack")
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_deterministic_result_id():
    at = EvidenceAttacker()
    a = at.attack(EvidenceAttack("E1", tampered=True, detected=True))
    b = at.attack(EvidenceAttack("E1", tampered=True, detected=True))
    assert a.result_id == b.result_id
