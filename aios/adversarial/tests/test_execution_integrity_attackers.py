from aios.adversarial.execution_integrity_attackers import (
    ExecutionIntegrityAttack,
    ExecutionIntegrityAttacker,
    ExecutionIntegrityResult,
    BLOCKED,
    BREACH,
)
from aios.adversarial._common import AdversarialError


def test_attack_construction():
    a = ExecutionIntegrityAttack("X1", tamper_attempt=True, integrity_verified=False)
    assert a.attack_id == "X1"


def test_attack_blocked_when_detected():
    at = ExecutionIntegrityAttacker()
    res = at.attack(ExecutionIntegrityAttack("X1", tamper_attempt=True, integrity_verified=False))
    assert isinstance(res, ExecutionIntegrityResult)
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_breach_when_undetected():
    at = ExecutionIntegrityAttacker()
    res = at.attack(ExecutionIntegrityAttack("X1", tamper_attempt=True, integrity_verified=True))
    assert res.breached is True
    assert res.status == BREACH


def test_attack_blocked_when_no_tamper():
    at = ExecutionIntegrityAttacker()
    res = at.attack(ExecutionIntegrityAttack("X1", tamper_attempt=False, integrity_verified=True))
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_rejects_empty_id():
    at = ExecutionIntegrityAttacker()
    try:
        at.attack(ExecutionIntegrityAttack("", tamper_attempt=True, integrity_verified=False))
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_rejects_non_attack():
    at = ExecutionIntegrityAttacker()
    try:
        at.attack("not-an-attack")
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_deterministic_result_id():
    at = ExecutionIntegrityAttacker()
    a = at.attack(ExecutionIntegrityAttack("X1", tamper_attempt=True, integrity_verified=False))
    b = at.attack(ExecutionIntegrityAttack("X1", tamper_attempt=True, integrity_verified=False))
    assert a.result_id == b.result_id
