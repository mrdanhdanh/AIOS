"""Tests for Autonomy Constitution + Audit Trail (TASK-103)."""

from aios.autonomy_constitution.constitution import (
    AuditTrail,
    AutonomyConstitution,
    ConstitutionDecision,
    ConstitutionEngine,
)


def _decision(**kw):
    base = dict(
        decision_id="d1",
        principal="agent-x",
        action="read",
        policy_ref="policy:base",
        risk="low",
        trust_remaining=1.0,
        halt_active=False,
        evidence_ref="ev-1",
    )
    base.update(kw)
    return ConstitutionDecision(**base)


def test_violation_blocks():
    eng = ConstitutionEngine()
    # DESTRUCTIVE without approval -> violation -> BLOCK (fail-closed).
    compliant, entry = eng.evaluate(_decision(action="destructive", policy_ref="policy:base"))
    assert compliant is False
    assert entry.constitution_compliant is False


def test_audit_chain_immutable():
    trail = AuditTrail()
    e1 = trail.append(_entry("d1", "agent", "read", "p", True))
    e2 = trail.append(_entry("d2", "agent", "write", "p", True))
    assert e2.prev_entry_hash == e1.content_hash()
    assert trail.verify_chain() is True


def test_tamper_detected():
    trail = AuditTrail()
    e1 = trail.append(_entry("d1", "agent", "read", "p", True))
    e2 = trail.append(_entry("d2", "agent", "write", "p", True))
    # Tamper: alter the first entry after it was chained.
    e1.principal = "attacker"
    assert trail.detect_tamper() is True
    assert trail.verify_chain() is False


def test_decision_trace_principal_policy():
    eng = ConstitutionEngine()
    compliant, entry = eng.evaluate(_decision(action="read", policy_ref="policy:trace"))
    assert entry.principal == "agent-x"
    assert entry.policy_ref == "policy:trace"
    assert entry.constitution_compliant is True


def test_deterministic_compliance():
    c = AutonomyConstitution()
    d = _decision(action="destructive", policy_ref="policy:base")
    assert c.is_compliant(d) is c.is_compliant(d)


def test_audit_evidence_provenance():
    eng = ConstitutionEngine()
    compliant, entry = eng.evaluate(_decision())
    assert eng.provenance_complete(entry) is True
    assert entry.evidence_ref


def _entry(decision_id, principal, action, policy_ref, compliant):
    from aios.autonomy_constitution.constitution import AuditEntry

    return AuditEntry(
        decision_id=decision_id,
        principal=principal,
        action=action,
        policy_ref=policy_ref,
        constitution_compliant=compliant,
    )
