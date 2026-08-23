from aios.adversarial.environment_dependency_attackers import (
    EnvironmentDependencyAttack,
    EnvironmentDependencyAttacker,
    EnvironmentDependencyResult,
    BLOCKED,
    BREACH,
)
from aios.adversarial._common import AdversarialError


def test_attack_construction():
    a = EnvironmentDependencyAttack("D1", malicious_dep=True, blocked=True)
    assert a.attack_id == "D1"


def test_attack_blocked_when_blocked():
    at = EnvironmentDependencyAttacker()
    res = at.attack(EnvironmentDependencyAttack("D1", malicious_dep=True, blocked=True))
    assert isinstance(res, EnvironmentDependencyResult)
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_breach_when_not_blocked():
    at = EnvironmentDependencyAttacker()
    res = at.attack(EnvironmentDependencyAttack("D1", malicious_dep=True, blocked=False))
    assert res.breached is True
    assert res.status == BREACH


def test_attack_blocked_when_clean():
    at = EnvironmentDependencyAttacker()
    res = at.attack(EnvironmentDependencyAttack("D1", malicious_dep=False, blocked=False))
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_rejects_empty_id():
    at = EnvironmentDependencyAttacker()
    try:
        at.attack(EnvironmentDependencyAttack("", malicious_dep=True, blocked=False))
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_rejects_non_attack():
    at = EnvironmentDependencyAttacker()
    try:
        at.attack("not-an-attack")
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_deterministic_result_id():
    at = EnvironmentDependencyAttacker()
    a = at.attack(EnvironmentDependencyAttack("D1", malicious_dep=True, blocked=True))
    b = at.attack(EnvironmentDependencyAttack("D1", malicious_dep=True, blocked=True))
    assert a.result_id == b.result_id
