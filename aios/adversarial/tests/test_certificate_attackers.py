from aios.adversarial.certificate_attackers import (
    CertificateAttack,
    CertificateAttacker,
    CertificateResult,
    BLOCKED,
    BREACH,
)
from aios.adversarial._common import AdversarialError


def test_attack_construction():
    a = CertificateAttack("C1", forged=True, verified=False)
    assert a.attack_id == "C1"


def test_attack_blocked_when_forged_but_rejected():
    at = CertificateAttacker()
    res = at.attack(CertificateAttack("C1", forged=True, verified=False))
    assert isinstance(res, CertificateResult)
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_breach_when_forged_and_verified():
    at = CertificateAttacker()
    res = at.attack(CertificateAttack("C1", forged=True, verified=True))
    assert res.breached is True
    assert res.status == BREACH


def test_attack_blocked_when_not_forged():
    at = CertificateAttacker()
    res = at.attack(CertificateAttack("C1", forged=False, verified=True))
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_rejects_empty_id():
    at = CertificateAttacker()
    try:
        at.attack(CertificateAttack("", forged=True, verified=False))
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_rejects_non_attack():
    at = CertificateAttacker()
    try:
        at.attack("not-an-attack")
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_deterministic_result_id():
    at = CertificateAttacker()
    a = at.attack(CertificateAttack("C1", forged=True, verified=False))
    b = at.attack(CertificateAttack("C1", forged=True, verified=False))
    assert a.result_id == b.result_id
