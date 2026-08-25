"""Tests for UnifiedRemediationLifecycle (TASK-236, M33)."""

from __future__ import annotations

from aios.autonomous_recovery.lifecycle import (
    RemediationPhase,
    UnifiedRemediationLifecycle,
)
from aios.kill_switch.controller import KillSwitchController
from aios.kill_switch.contracts import HaltScope, HaltSource, HaltSignal
from aios.remediation_detect.detect import Incident, Symptom, SymptomSeverity
from aios.remediation_simulation.simulation import SimulationGate


def _incident() -> Incident:
    return Incident(incident_id="inc-abc", kind="failure", severity="high", signal={})


def _symptoms() -> list[Symptom]:
    return [Symptom("s1", "svc down", evidence_ref="ev-1", severity=SymptomSeverity.HIGH)]


def _trace() -> list[str]:
    return ["root_cause:db_unreachable"]


def test_lifecycle_runs_to_done_with_low_risk_candidate():
    life = UnifiedRemediationLifecycle()
    report = life.run(_incident(), _symptoms(), _trace(), evidence_ref="ev-1")
    # Low-risk candidates (risk_score < 0.5) simulate+apply pass deterministically.
    assert report.phase in (RemediationPhase.DONE, RemediationPhase.APPLIED)
    assert report.diagnosis is not None
    assert report.diagnosis.is_traceable()
    assert report.selected is not None
    assert report.simulation is not None
    assert report.simulation.gate is SimulationGate.PASS
    assert report.integrity is not None
    assert report.integrity.passed is True


def test_lifecycle_escalates_without_traceable_diagnosis():
    life = UnifiedRemediationLifecycle()
    # No symptoms -> no evidence -> fail-closed escalation.
    report = life.run(_incident(), [], [], evidence_ref="")
    assert report.phase is RemediationPhase.DIAGNOSED
    assert report.success is False
    assert report.diagnosis is not None
    assert report.diagnosis.escalated is True


def test_lifecycle_halts_under_kill_switch():
    kill = KillSwitchController()
    kill.issue(
        HaltSignal(
            source=HaltSource.SAFETY,
            scope=HaltScope.GLOBAL,
            issued_at="2026-08-25T00:00:00Z",
            reason="emergency",
        )
    )
    life = UnifiedRemediationLifecycle(kill_switch=kill)
    report = life.run(_incident(), _symptoms(), _trace(), evidence_ref="ev-1")
    assert report.phase is RemediationPhase.HALTED
    assert report.halted is True
    assert report.success is False


def test_lifecycle_deterministic_same_inputs():
    r1 = UnifiedRemediationLifecycle().run(_incident(), _symptoms(), _trace(), evidence_ref="ev-1")
    r2 = UnifiedRemediationLifecycle().run(_incident(), _symptoms(), _trace(), evidence_ref="ev-1")
    assert r1.remediation_id == r2.remediation_id
    assert r1.phase == r2.phase
    assert r1.success == r2.success
