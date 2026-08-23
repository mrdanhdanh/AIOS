from aios.adversarial.requirement_scope_attackers import (
    RequirementScopeAttack,
    RequirementScopeAttacker,
    RequirementScopeResult,
    BLOCKED,
    BREACH,
)
from aios.adversarial._common import AdversarialError


def test_attack_construction():
    a = RequirementScopeAttack("S1", attempted_scope="x", allowed_scope="x")
    assert a.attack_id == "S1"


def test_attack_blocked_when_in_scope():
    at = RequirementScopeAttacker()
    res = at.attack(RequirementScopeAttack("S1", attempted_scope="x", allowed_scope="x"))
    assert isinstance(res, RequirementScopeResult)
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_breach_when_out_of_scope():
    at = RequirementScopeAttacker()
    res = at.attack(RequirementScopeAttack("S1", attempted_scope="y", allowed_scope="x"))
    assert res.breached is True
    assert res.status == BREACH


def test_attack_rejects_empty_id():
    at = RequirementScopeAttacker()
    try:
        at.attack(RequirementScopeAttack("", attempted_scope="x", allowed_scope="x"))
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_rejects_empty_scope():
    at = RequirementScopeAttacker()
    try:
        at.attack(RequirementScopeAttack("S1", attempted_scope="", allowed_scope="x"))
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_rejects_non_attack():
    at = RequirementScopeAttacker()
    try:
        at.attack("not-an-attack")
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_deterministic_result_id():
    at = RequirementScopeAttacker()
    a = at.attack(RequirementScopeAttack("S1", attempted_scope="x", allowed_scope="x"))
    b = at.attack(RequirementScopeAttack("S1", attempted_scope="x", allowed_scope="x"))
    assert a.result_id == b.result_id
