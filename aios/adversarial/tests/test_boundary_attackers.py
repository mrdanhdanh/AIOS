from aios.adversarial.boundary_attackers import (
    BoundaryAttack,
    BoundaryAttacker,
    BoundaryResult,
    BLOCKED,
    BREACH,
)
from aios.adversarial._common import AdversarialError


def test_attack_construction():
    a = BoundaryAttack("B1", escape_attempt=True, contained=True)
    assert a.attack_id == "B1"


def test_attack_blocked_when_contained():
    at = BoundaryAttacker()
    res = at.attack(BoundaryAttack("B1", escape_attempt=True, contained=True))
    assert isinstance(res, BoundaryResult)
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_breach_when_not_contained():
    at = BoundaryAttacker()
    res = at.attack(BoundaryAttack("B1", escape_attempt=True, contained=False))
    assert res.breached is True
    assert res.status == BREACH


def test_attack_blocked_when_no_attempt():
    at = BoundaryAttacker()
    res = at.attack(BoundaryAttack("B1", escape_attempt=False, contained=False))
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_rejects_empty_id():
    at = BoundaryAttacker()
    try:
        at.attack(BoundaryAttack("", escape_attempt=True, contained=False))
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_rejects_non_attack():
    at = BoundaryAttacker()
    try:
        at.attack("not-an-attack")
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_deterministic_result_id():
    at = BoundaryAttacker()
    a = at.attack(BoundaryAttack("B1", escape_attempt=True, contained=True))
    b = at.attack(BoundaryAttack("B1", escape_attempt=True, contained=True))
    assert a.result_id == b.result_id
