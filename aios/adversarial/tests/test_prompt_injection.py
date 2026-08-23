from aios.adversarial.prompt_injection import (
    PromptInjectionTester,
    PromptInjectionAttack,
    PromptInjectionResult,
    UntrustedArtifactIsolation,
    ArtifactIsolationAttack,
    ArtifactIsolationResult,
    BLOCKED,
    BREACH,
)
from aios.adversarial._common import AdversarialError


def test_prompt_construction():
    a = PromptInjectionAttack("P1", injection_present=True, sanitized=True)
    assert a.attack_id == "P1"


def test_prompt_blocked_when_sanitized():
    t = PromptInjectionTester()
    res = t.attack(PromptInjectionAttack("P1", injection_present=True, sanitized=True))
    assert isinstance(res, PromptInjectionResult)
    assert res.breached is False
    assert res.status == BLOCKED


def test_prompt_breach_when_unsanitized():
    t = PromptInjectionTester()
    res = t.attack(PromptInjectionAttack("P1", injection_present=True, sanitized=False))
    assert res.breached is True
    assert res.status == BREACH


def test_isolation_blocked_when_isolated():
    i = UntrustedArtifactIsolation()
    res = i.attack(ArtifactIsolationAttack("A1", untrusted=True, isolated=True))
    assert isinstance(res, ArtifactIsolationResult)
    assert res.breached is False
    assert res.status == BLOCKED


def test_isolation_breach_when_not_isolated():
    i = UntrustedArtifactIsolation()
    res = i.attack(ArtifactIsolationAttack("A1", untrusted=True, isolated=False))
    assert res.breached is True
    assert res.status == BREACH


def test_prompt_rejects_empty_id():
    t = PromptInjectionTester()
    try:
        t.attack(PromptInjectionAttack("", injection_present=True, sanitized=False))
        assert False, "expected AdversarialError"
    except AdversarialError:
        pass


def test_prompt_deterministic_result_id():
    t = PromptInjectionTester()
    a = t.attack(PromptInjectionAttack("P1", injection_present=True, sanitized=True))
    b = t.attack(PromptInjectionAttack("P1", injection_present=True, sanitized=True))
    assert a.result_id == b.result_id
