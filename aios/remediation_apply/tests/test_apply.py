"""Tests for TASK-097 — Remediation Apply + Re-test + Rollback + Certification (M14)."""

from __future__ import annotations

from aios.autonomy_governor.contracts import ApprovalRequest, AutonomyAction
from aios.remediation_apply.apply import ApplyOrchestrator, ApplyResult
from aios.remediation_candidate.candidate import Candidate
from aios.remediation_simulation.simulation import Sandbox, SimulationGate, SimulationGateEngine
from aios.runtime.permission import Permission, PermissionBroker, PermissionScope


def _broker() -> PermissionBroker:
    b = PermissionBroker()
    b.grant_many("remediation", [Permission(PermissionScope.EXECUTE, "*")])
    return b


def _low_risk() -> Candidate:
    return Candidate(
        candidate_id="cand-low", source_diagnosis_id="inc-1", action="restart_service",
        risk_score=0.2, policy_compliant=True, rollback_cost=0.1, blast_radius="local",
        impact=0.2, autonomy_action="execute",
    )


def _high_risk() -> Candidate:
    return Candidate(
        candidate_id="cand-high", source_diagnosis_id="inc-1", action="isolate_node",
        risk_score=0.6, policy_compliant=True, rollback_cost=0.5, blast_radius="global",
        impact=0.6, autonomy_action="modify_system",
    )


def _passed_simulation(candidate: Candidate) -> object:
    return SimulationGateEngine().run(candidate, Sandbox("sbx-1"), simulate_fn=lambda c: "pass")


def test_apply_with_permission_low_risk():
    eng = ApplyOrchestrator(permission_broker=_broker())
    res = eng.apply(_low_risk(), _passed_simulation(_low_risk()), re_test_fn=lambda c: True)
    assert isinstance(res, ApplyResult)
    assert res.permission_granted is True
    assert res.applied is True
    assert res.re_test_passed is True
    assert res.rolled_back is False
    assert res.certified is True


def test_missing_permission_no_apply():
    eng = ApplyOrchestrator(permission_broker=PermissionBroker())  # no grants
    res = eng.apply(_low_risk(), _passed_simulation(_low_risk()))
    assert res.permission_granted is False
    assert res.applied is False  # fail-closed
    assert res.certified is False


def test_high_risk_no_approval_no_apply():
    eng = ApplyOrchestrator(permission_broker=_broker())
    res = eng.apply(_high_risk(), _passed_simulation(_high_risk()), human_approval=None)
    assert res.human_approved is False
    assert res.applied is False  # fail-closed: needs human approval
    assert res.certified is False


def test_re_test_fail_rollback():
    eng = ApplyOrchestrator(permission_broker=_broker())
    res = eng.apply(_low_risk(), _passed_simulation(_low_risk()), re_test_fn=lambda c: False)
    assert res.re_test_passed is False
    assert res.rolled_back is True  # rollback on fail (T074/T066)
    assert res.certified is False
    assert res.applied is True


def test_high_risk_with_approval_certified():
    eng = ApplyOrchestrator(permission_broker=_broker())
    approval = ApprovalRequest(action="isolate_node", target="global")
    res = eng.apply(
        _high_risk(), _passed_simulation(_high_risk()), human_approval=approval,
        re_test_fn=lambda c: True,
    )
    assert res.human_approved is True
    assert res.applied is True
    assert res.certified is True


def test_deterministic_apply_result():
    eng = ApplyOrchestrator(permission_broker=_broker())
    r1 = eng.apply(_low_risk(), _passed_simulation(_low_risk()), re_test_fn=lambda c: True)
    r2 = eng.apply(_low_risk(), _passed_simulation(_low_risk()), re_test_fn=lambda c: True)
    assert eng.result_hash(r1) == eng.result_hash(r2)
    assert r1.applied == r2.applied
    assert r1.certified == r2.certified
