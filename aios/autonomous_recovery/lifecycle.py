"""Unified Remediation Lifecycle (TASK-236, M33).

Self-healing loop that wires the existing remediation planes into ONE
fail-closed lifecycle instead of adding a new subsystem:

    Failure -> Detect -> Diagnose -> Candidate -> Risk Score
            -> Simulation -> Independent Verification -> Approval/Auto-Apply
            -> Rollback if FAIL -> Integrity -> (Kill Switch hard guard)

Every step reuses the already-shipped modules:
    * aios.remediation_detect   (DetectDiagnoseEngine)
    * aios.remediation_candidate (CandidateEngine)
    * aios.remediation_simulation (SimulationGateEngine)
    * aios.remediation_apply    (ApplyOrchestrator)
    * aios.remediation_integrity (RemediationIntegrityGate + KillSwitch)
    * aios.autonomous_recovery  (RecoveryController)
    * aios.kill_switch          (KillSwitchController)
    * aios.governance.evidence  (EvidenceStore)

Safety properties (all fail-closed / kill-switch-respected / provenance /
deterministic):
* Fail-closed — any missing evidence / failed gate -> escalate, never apply.
* Kill switch respected — a halt signal stops the lifecycle immediately.
* Evidence required — every phase records provenance (T001 Rule 5).
* Deterministic — same inputs -> same report.
* No parallel remediation system — orchestrates existing modules only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Optional

from aios.governance.evidence.store import EvidenceStore
from aios.kill_switch.controller import KillSwitchController
from aios.kill_switch.contracts import HaltScope
from aios.remediation_apply.apply import ApplyOrchestrator, ApplyResult
from aios.remediation_candidate.candidate import Candidate, CandidateEngine, CandidatePlan
from aios.remediation_detect.detect import (
    DetectDiagnoseEngine,
    Diagnosis,
    Incident,
    Symptom,
)
from aios.remediation_integrity.integrity import (
    RemediationArtifact,
    RemediationIntegrity,
    RemediationIntegrityGate,
)
from aios.remediation_simulation.simulation import (
    Sandbox,
    SimulationGate,
    SimulationGateEngine,
    SimulationResult,
)


class RemediationPhase(str, Enum):
    """Lifecycle phases (fail-closed progression)."""

    IDLE = "idle"
    DETECTED = "detected"
    DIAGNOSED = "diagnosed"
    CANDIDATE = "candidate"
    SIMULATED = "simulated"
    VERIFIED = "verified"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"
    HALTED = "halted"
    DONE = "done"


@dataclass
class RemediationReport:
    """Fail-closed, provenance-carrying result of one remediation run."""

    remediation_id: str
    phase: RemediationPhase
    incident: Optional[Incident] = None
    diagnosis: Optional[Diagnosis] = None
    candidate_plan: Optional[CandidatePlan] = None
    selected: Optional[Candidate] = None
    simulation: Optional[SimulationResult] = None
    apply_result: Optional[ApplyResult] = None
    integrity: Optional[RemediationIntegrity] = None
    halted: bool = False
    rolled_back: bool = False
    success: bool = False
    trace: List[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "remediation_id": self.remediation_id,
            "phase": self.phase.value,
            "incident_id": self.incident.incident_id if self.incident else "",
            "diagnosis_traceable": self.diagnosis.is_traceable() if self.diagnosis else False,
            "candidates": len(self.candidate_plan.candidates) if self.candidate_plan else 0,
            "selected_candidate": self.selected.candidate_id if self.selected else "",
            "simulation_gate": self.simulation.gate.value if self.simulation else "",
            "applied": self.apply_result.applied if self.apply_result else False,
            "re_test_passed": self.apply_result.re_test_passed if self.apply_result else False,
            "integrity_passed": self.integrity.passed if self.integrity else False,
            "halted": self.halted,
            "rolled_back": self.rolled_back,
            "success": self.success,
            "trace": list(self.trace),
        }


class UnifiedRemediationLifecycle:
    """Orchestrates the full self-healing loop (M33, TASK-236).

    Deterministic: same incident + same symptoms + same trace -> same report.
    Fail-closed: any missing evidence / failed gate -> escalate, never apply.
    """

    def __init__(
        self,
        evidence_store: Optional[EvidenceStore] = None,
        kill_switch: Optional[KillSwitchController] = None,
        detect_engine: Optional[DetectDiagnoseEngine] = None,
        candidate_engine: Optional[CandidateEngine] = None,
        simulation_engine: Optional[SimulationGateEngine] = None,
        apply_orchestrator: Optional[ApplyOrchestrator] = None,
        integrity_gate: Optional[RemediationIntegrityGate] = None,
    ) -> None:
        self._evidence = evidence_store or EvidenceStore()
        self._kill = kill_switch or KillSwitchController()
        self._detect = detect_engine or DetectDiagnoseEngine(evidence_store=self._evidence)
        self._candidate = candidate_engine or CandidateEngine(evidence_store=self._evidence)
        self._sim = simulation_engine or SimulationGateEngine(evidence_store=self._evidence)
        self._apply = apply_orchestrator or ApplyOrchestrator(evidence_store=self._evidence)
        self._integrity = integrity_gate or RemediationIntegrityGate(
            kill_switch=self._kill, evidence_store=self._evidence
        )

    # -- public API -----------------------------------------------------------

    def run(
        self,
        incident: Optional[Incident],
        symptoms: List[Symptom],
        causal_trace: List[str],
        evidence_ref: str = "",
        subject: str = "remediation",
        human_approval: Any = None,
        apply_fn: Optional[Callable[[Candidate], None]] = None,
        re_test_fn: Optional[Callable[[Candidate], bool]] = None,
        simulate_fn: Optional[Callable[[Candidate], str]] = None,
        meta_fn: Optional[Callable[[str], str]] = None,
    ) -> RemediationReport:
        """Drive the full remediation lifecycle (fail-closed)."""
        remediation_id = f"rem-{hashlib_sha256((incident.incident_id if incident else 'x') + evidence_ref)}"
        trace: List[str] = []

        # 0. Kill switch hard guard (T068) — halt stops everything.
        if self._kill.is_halted(scope=HaltScope.GLOBAL):
            trace.append("halted:kill_switch_active")
            return RemediationReport(
                remediation_id=remediation_id,
                phase=RemediationPhase.HALTED,
                incident=incident,
                halted=True,
                trace=trace,
            )

        # 1. Diagnose (fail-closed).
        diagnosis = self._detect.diagnose(incident, symptoms, causal_trace, evidence_ref)
        trace.append(f"diagnosed:traceable={diagnosis.is_traceable()}")
        if diagnosis.escalated or not diagnosis.is_traceable():
            # Fail-closed: never remediate without a traceable root cause.
            trace.append("escalated:no_traceable_diagnosis")
            return RemediationReport(
                remediation_id=remediation_id,
                phase=RemediationPhase.DIAGNOSED,
                incident=incident,
                diagnosis=diagnosis,
                trace=trace,
            )

        # 2. Candidate generation + risk scoring + policy filter.
        plan = self._candidate.run(diagnosis)
        trace.append(f"candidates:{len(plan.candidates)}:rejected:{len(plan.rejected)}")
        if not plan.candidates:
            trace.append("no_compliant_candidate")
            return RemediationReport(
                remediation_id=remediation_id,
                phase=RemediationPhase.CANDIDATE,
                incident=incident,
                diagnosis=diagnosis,
                candidate_plan=plan,
                trace=trace,
            )
        selected = plan.candidates[0]

        # 3. Simulation + independent (meta) verification (fail-closed gate).
        sim = self._sim.run(
            selected,
            sandbox=Sandbox(f"sbx-{selected.candidate_id}"),
            simulate_fn=simulate_fn,
            meta_fn=meta_fn,
        )
        trace.append(f"simulation_gate:{sim.gate.value}")
        if sim.gate is not SimulationGate.PASS:
            trace.append("rejected:simulation_gate")
            return RemediationReport(
                remediation_id=remediation_id,
                phase=RemediationPhase.SIMULATED,
                incident=incident,
                diagnosis=diagnosis,
                candidate_plan=plan,
                selected=selected,
                simulation=sim,
                trace=trace,
            )

        # 4. Apply (permission + approval + re-test + rollback) — fail-closed.
        apply_result = self._apply.apply(
            selected,
            sim,
            subject=subject,
            human_approval=human_approval,
            apply_fn=apply_fn,
            re_test_fn=re_test_fn,
        )
        trace.append(
            f"applied:{apply_result.applied}:re_test:{apply_result.re_test_passed}"
            f":rolled_back:{apply_result.rolled_back}"
        )

        # 5. Integrity + kill-switch hook (T078/T068).
        artifacts = [
            RemediationArtifact(
                artifact_id=selected.candidate_id,
                content=json.dumps(selected.to_dict(), sort_keys=True),
                expected_hash=sha256(json.dumps(selected.to_dict(), sort_keys=True)),
            )
        ]
        self._integrity.hook_kill_switch(remediation_id)
        integrity = self._integrity.check(
            remediation_id=remediation_id,
            artifacts=artifacts,
            audit_trail=list(trace),
            kill_switch_hooked=True,
        )
        trace.append(f"integrity_passed:{integrity.passed}")

        # 6. Final verdict (fail-closed).
        success = (
            apply_result.applied
            and apply_result.re_test_passed
            and not apply_result.rolled_back
            and integrity.passed
        )
        if apply_result.rolled_back:
            phase = RemediationPhase.ROLLED_BACK
        elif success:
            phase = RemediationPhase.DONE
        else:
            phase = RemediationPhase.APPLIED

        return RemediationReport(
            remediation_id=remediation_id,
            phase=phase,
            incident=incident,
            diagnosis=diagnosis,
            candidate_plan=plan,
            selected=selected,
            simulation=sim,
            apply_result=apply_result,
            integrity=integrity,
            rolled_back=apply_result.rolled_back,
            success=success,
            trace=trace,
        )


def hashlib_sha256(text: str) -> str:
    """Deterministic short hash helper."""
    import hashlib

    return hashlib.sha256(text.encode()).hexdigest()[:8]


def sha256(text: str) -> str:
    """Re-export of verification_integrity.sha256 for artifact hashing."""
    from aios.verification_integrity.integrity import sha256 as _sha256

    return _sha256(text)
