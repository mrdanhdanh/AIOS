from aios.adversarial.test_weakness_attackers import (
    TestWeaknessAttack,
    TestWeaknessAttacker,
    TestWeaknessResult,
    BLOCKED,
    BREACH,
)
from aios.adversarial._common import AdversarialError


def test_attack_construction():
    a = TestWeaknessAttack("T1", mutation_killed=True)
    assert a.attack_id == "T1"


def test_attack_blocked_when_killed():
    at = TestWeaknessAttacker()
    res = at.attack(TestWeaknessAttack("T1", mutation_killed=True))
    assert isinstance(res, TestWeaknessResult)
    assert res.breached is False
    assert res.status == BLOCKED


def test_attack_breach_when_survives():
    at = TestWeaknessAttacker()
    res = at.attack(TestWeaknessAttack("T1", mutation_killed=False))
    assert res.breached is True
    assert res.status == BREACH


def test_attack_rejects_empty_id():
    at = TestWeaknessAttacker()
    try:
        at.attack(TestWeaknessAttack("", mutation_killed=True))
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_rejects_non_attack():
    at = TestWeaknessAttacker()
    try:
        at.attack("not-an-attack")
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_attack_rejects_empty_results_not_applicable():
    # mutation_killed False is a valid breach, not an error
    at = TestWeaknessAttacker()
    res = at.attack(TestWeaknessAttack("T1", mutation_killed=False))
    assert res.status == BREACH


def test_attack_deterministic_result_id():
    at = TestWeaknessAttacker()
    a = at.attack(TestWeaknessAttack("T1", mutation_killed=True))
    b = at.attack(TestWeaknessAttack("T1", mutation_killed=True))
    assert a.result_id == b.result_id
