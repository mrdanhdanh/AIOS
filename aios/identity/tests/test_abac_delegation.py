"""Tests for TASK-035 ABAC engine, delegation attenuation, and new contracts."""

from __future__ import annotations

from aios.identity.abac import AuthorizationEngine
from aios.identity.contracts import (
    AuthorizationDecision,
    AuthorizationRequest,
    Decision,
    Delegation,
    Permission,
    Policy,
    Principal,
    PrincipalType,
    Role,
)
from aios.identity.delegation import DelegationManager


def _principal(perms: set[Permission]) -> Principal:
    p = Principal(name="p", principal_type=PrincipalType.USER)
    p.roles.append(Role(name="r", permissions=perms))
    return p


def test_principal_new_fields() -> None:
    p = _principal({Permission.READ})
    assert p.principal_type == PrincipalType.USER
    assert p.auth_source.value == "local"
    assert p.metadata == {}


def test_abac_allow_via_policy() -> None:
    eng = AuthorizationEngine()
    eng.add_policy(Policy(name="allow-write", required_permission=Permission.WRITE, effect="allow"))
    subj = _principal({Permission.WRITE})
    d = eng.evaluate(AuthorizationRequest(subject=subj, action=Permission.WRITE))
    assert d.decision == Decision.ALLOW
    assert d.allowed is True


def test_abac_deny_via_policy() -> None:
    eng = AuthorizationEngine()
    eng.add_policy(Policy(name="deny-write", required_permission=Permission.WRITE, effect="deny",
                          conditions={"clearance": "high"}))
    subj = _principal({Permission.WRITE})
    d = eng.evaluate(AuthorizationRequest(subject=subj, action=Permission.WRITE))
    assert d.decision == Decision.DENY
    assert d.allowed is False


def test_abac_ask_when_no_grant() -> None:
    eng = AuthorizationEngine()
    subj = _principal({Permission.READ})
    d = eng.evaluate(AuthorizationRequest(subject=subj, action=Permission.ADMIN))
    assert d.decision == Decision.ASK
    assert d.allowed is False  # fail-closed


def test_delegation_attenuation() -> None:
    mgr = DelegationManager()
    delegator = _principal({Permission.READ, Permission.WRITE})
    delegatee = Principal(name="d")
    # Try to delegate ADMIN (not held) -> attenuated to empty -> rejected.
    try:
        mgr.delegate(delegator, delegatee, {Permission.ADMIN})
        assert False, "should raise"
    except Exception:
        pass
    d = mgr.delegate(delegator, delegatee, {Permission.READ, Permission.WRITE, Permission.ADMIN})
    assert d.permissions == {Permission.READ, Permission.WRITE}
    assert mgr.permissions_for(delegatee.principal_id) == {Permission.READ, Permission.WRITE}
