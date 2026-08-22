"""Remediation Integrity + Kill Switch (TASK-098, M14).

Canonical integrity contract:

    RemediationIntegrity
    ├── remediation_id
    ├── artifact_hashes: [..]
    ├── audit_trail: [..]
    ├── kill_switch_hooked: bool
    ├── tampered: bool
    └── evidence_ref

Safety properties (all fail-closed / kill-switch-respected / provenance / deterministic):
* Fail-closed integrity — tampered artifact -> reject (never promote, T078).
* Kill switch respected — remediation respects T068 halt.
* Audit required — every step carries an audit trail.
* Evidence required — every integrity check carries provenance (T001 Rule 5).
* Deterministic — same artifact + same check -> same result.
* No parallel integrity system — uses Integrity (T078) + Kill Switch (T068).

Integration: imports ``aios.verification_integrity`` (IntegrityChecker, sha256),
``aios.kill_switch`` (KillSwitchController, HaltSignal, HaltScope, HaltSource) and
``aios.governance.evidence.store`` (EvidenceStore). No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List, Optional

from aios.governance.evidence.store import EvidenceStore
from aios.kill_switch.contracts import HaltScope, HaltSignal, HaltSource
from aios.kill_switch.controller import KillSwitchController
from aios.verification_integrity.integrity import IntegrityChecker, sha256


@dataclass
class RemediationArtifact:
    """A remediation artifact with content + expected (untampered) hash (T078)."""

    artifact_id: str
    content: str
    expected_hash: str

    def is_tampered(self) -> bool:
        """True when the content hash differs from the expected hash."""
        return sha256(self.content) != self.expected_hash

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "expected_hash": self.expected_hash,
            "actual_hash": sha256(self.content),
        }


@dataclass
class RemediationIntegrity:
    """Fail-closed integrity result for a remediation run."""

    remediation_id: str
    artifact_hashes: List[str]
    audit_trail: List[str]
    kill_switch_hooked: bool
    tampered: bool
    passed: bool  # fail-closed: tampered OR missing audit -> False
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "remediation_id": self.remediation_id,
            "artifact_hashes": list(self.artifact_hashes),
            "audit_trail": list(self.audit_trail),
            "kill_switch_hooked": self.kill_switch_hooked,
            "tampered": self.tampered,
            "passed": self.passed,
            "evidence_ref": self.evidence_ref,
        }


class _RemediationContext:
    """A minimal execution context so a remediation respects the kill switch (T068)."""

    def __init__(self, context_id: str) -> None:
        self.context_id = context_id
        self.context_type = "remediation"
        self._halted = False

    def on_halt(self, signal: HaltSignal) -> None:
        self._halted = True

    def is_halted(self) -> bool:
        return self._halted

    def drain(self):  # type: ignore[no-untyped-def]
        return None


class RemediationIntegrityGate:
    """Verifies remediation integrity (T078) and hooks the kill switch (T068)."""

    def __init__(
        self,
        integrity_checker: Optional[IntegrityChecker] = None,
        kill_switch: Optional[KillSwitchController] = None,
        evidence_store: Optional[EvidenceStore] = None,
    ) -> None:
        self._integrity = integrity_checker or IntegrityChecker()
        self._kill = kill_switch or KillSwitchController()
        self._evidence = evidence_store or EvidenceStore()

    # -- integrity check (fail-closed) ---------------------------------------

    def check(
        self,
        remediation_id: str,
        artifacts: List[RemediationArtifact],
        audit_trail: List[str],
        kill_switch_hooked: bool = True,
    ) -> RemediationIntegrity:
        """Same artifact + same check -> same result (deterministic)."""
        tampered = any(self._integrity.is_tampered(a.content, a.expected_hash) for a in artifacts)
        audit_ok = bool(audit_trail)
        artifact_hashes = [sha256(a.content) for a in artifacts]
        # Fail-closed: tampered OR missing audit -> reject (never promote).
        passed = (not tampered) and audit_ok
        result = RemediationIntegrity(
            remediation_id=remediation_id,
            artifact_hashes=artifact_hashes,
            audit_trail=list(audit_trail),
            kill_switch_hooked=bool(kill_switch_hooked),
            tampered=tampered,
            passed=passed,
            evidence_ref=f"rint-{hashlib.sha256(remediation_id.encode()).hexdigest()[:8]}",
        )
        self._record_evidence(result)
        return result

    # -- kill switch integration (T068) ---------------------------------------

    def hook_kill_switch(self, remediation_id: str) -> None:
        """Register the remediation context so it respects a halt signal (T068)."""
        self._kill.register(_RemediationContext(remediation_id))

    def should_halt(self, remediation_id: str, scope: HaltScope = HaltScope.GLOBAL) -> bool:
        """True when a halt is active and the remediation must stop (T068)."""
        return self._kill.is_halted(scope=scope, target_id=remediation_id)

    def issue_halt(self, reason: str, evidence_ref: str = "") -> HaltSignal:
        """Issue an emergency halt (T068) that stops running remediations."""
        signal = HaltSignal(
            source=HaltSource.SAFETY,
            scope=HaltScope.GLOBAL,
            issued_at=datetime.now(timezone.utc).isoformat(),
            reason=reason,
            evidence_ref=evidence_ref,
        )
        self._kill.issue(signal)
        return signal

    # -- evidence -------------------------------------------------------------

    def _record_evidence(self, result: RemediationIntegrity) -> str:
        ev_id = result.evidence_ref
        self._evidence.add_evidence(
            evidence_id=ev_id,
            task_id="TASK-098",
            run_id="run-098",
            producer="remediation_integrity",
            type="integrity",
            source=result.remediation_id,
            content=json.dumps(result.to_dict(), sort_keys=True),
        )
        return ev_id

    def provenance_complete(self, result: RemediationIntegrity) -> bool:
        """Every integrity check carries provenance (T001 Rule 5)."""
        return bool(result.evidence_ref)

    def result_hash(self, result: RemediationIntegrity) -> str:
        """Deterministic hash (same result -> same hash)."""
        payload = {
            "remediation_id": result.remediation_id,
            "artifact_hashes": sorted(result.artifact_hashes),
            "audit_trail": sorted(result.audit_trail),
            "kill_switch_hooked": result.kill_switch_hooked,
            "tampered": result.tampered,
            "passed": result.passed,
            "evidence_ref": result.evidence_ref,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()
