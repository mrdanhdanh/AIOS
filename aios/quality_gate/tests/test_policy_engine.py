from aios.quality_gate.policy_engine import Policy, PolicyEngine, PolicyReport
from aios.quality_gate._common import QualityGateError


def test_policy_construction_immutable():
    p = Policy("P1", "scope", "ALLOW", 1)
    assert p.policy_id == "P1"


def test_policy_allow_on_single_match():
    e = PolicyEngine("BALANCED")
    rep = e.evaluate("scope", [Policy("P1", "scope", "ALLOW", 1)])
    assert isinstance(rep, PolicyReport)
    assert rep.decision == "ALLOW"


def test_policy_precedence_higher_wins():
    e = PolicyEngine("BALANCED")
    rep = e.evaluate("scope", [Policy("P1", "scope", "ALLOW", 1), Policy("P2", "scope", "DENY", 5)])
    assert rep.decision == "DENY"


def test_policy_tie_blocked():
    e = PolicyEngine("BALANCED")
    rep = e.evaluate("scope", [Policy("P1", "scope", "ALLOW", 1), Policy("P2", "scope", "DENY", 1)])
    assert rep.decision == "BLOCKED"


def test_policy_no_match_blocked_fail_closed():
    e = PolicyEngine("BALANCED")
    rep = e.evaluate("scope", [Policy("P1", "other", "ALLOW", 1)])
    assert rep.decision == "BLOCKED"


def test_policy_rejects_invalid_profile():
    try:
        PolicyEngine("NOPE")
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_policy_deterministic_report_id():
    e = PolicyEngine("BALANCED")
    a = e.evaluate("scope", [Policy("P1", "scope", "ALLOW", 1)])
    b = e.evaluate("scope", [Policy("P1", "scope", "ALLOW", 1)])
    assert a.report_id == b.report_id
