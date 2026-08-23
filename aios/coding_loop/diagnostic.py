"""Diagnostic Agent (TASK-148, M21).

Diagnoses root cause from a classified failure (T147) + observation (T146) and
produces a diagnostic report. Built on Failure Classification T147 + Execution
Observation T146 + Evidence T001. TASK-148 is a *diagnostic agent*, not a new
repair planner.

Layering: ``coding_loop`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

from aios.coding_loop._common import CodingLoopError, _hash, _now
from aios.coding_loop.classification import FailureClass
from aios.coding_loop.observation import Observation


# Deterministic root-cause mapping from taxonomy label (T001 Rule 5 provenance).
_ROOT_CAUSE = {
    "SYNTAX": "malformed source token",
    "RUNTIME": "uncaught exception in execution path",
    "LOGIC": "incorrect branch / assertion mismatch",
    "TIMEOUT": "execution exceeded deadline",
    "RESOURCE": "resource exhaustion (memory/cpu)",
    "NETWORK": "unreachable dependency / egress blocked",
}


@dataclass
class DiagnosticReport:
    """Immutable-by-id diagnostic report (T148)."""

    report_id: str
    class_ref: str
    observation_ref: str
    root_cause: str
    confidence: float
    evidence_ref: str
    authority: str = "aios"
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.report_id:
            raise CodingLoopError("report_id required (T001 Rule 1, immutable).")
        if not self.evidence_ref:
            raise CodingLoopError("DiagnosticReport requires evidence_ref (T001 Rule 5).")
        if not (0.0 <= self.confidence <= 1.0):
            raise CodingLoopError("confidence must be in [0,1].")


class DiagnosticAgent:
    """Deterministic diagnostic agent; fail-closed on UNKNOWN (T148)."""

    def __init__(self) -> None:
        self._reports: Dict[str, DiagnosticReport] = {}

    def diagnose(
        self,
        failure_class: FailureClass,
        observation: Optional[Observation] = None,
        evidence_ref: Optional[str] = None,
        report_id: Optional[str] = None,
    ) -> DiagnosticReport:
        # Fail-closed: diagnosis requires a failure class with provenance (T001 Rule 5).
        if failure_class is None or not failure_class.evidence_ref:
            raise CodingLoopError("Diagnosis requires failure class with provenance (T001 Rule 5).")
        if failure_class.taxonomy_label == "UNKNOWN":
            root_cause = "UNKNOWN"
            confidence = 0.0
        else:
            root_cause = self._infer_root_cause(failure_class)
            confidence = min(1.0, failure_class.confidence + 0.1)
        ev = evidence_ref or failure_class.evidence_ref
        rid = report_id or f"diag-{uuid.uuid4().hex[:12]}"
        if rid in self._reports:
            raise CodingLoopError(f"Duplicate report_id '{rid}' (T001 Rule 1).")
        rep = DiagnosticReport(
            report_id=rid,
            class_ref=failure_class.class_id,
            observation_ref=failure_class.observation_ref,
            root_cause=root_cause,
            confidence=confidence,
            evidence_ref=ev,
        )
        self._reports[rid] = rep
        return rep

    def _infer_root_cause(self, failure_class: FailureClass) -> str:
        # Deterministic: same class -> same root cause.
        return _ROOT_CAUSE.get(failure_class.taxonomy_label, "undetermined")

    def is_promotable(self, report: DiagnosticReport) -> bool:
        """UNKNOWN root cause (low confidence) is never promoted to PASS (T078)."""
        return report.root_cause != "UNKNOWN" and report.confidence >= 0.5

    def get(self, report_id: str) -> DiagnosticReport:
        if report_id not in self._reports:
            raise CodingLoopError(f"Unknown report '{report_id}'.")
        return self._reports[report_id]

    def provenance(self, report_id: str) -> dict:
        rep = self.get(report_id)
        payload = (
            f"{rep.report_id}|{rep.class_ref}|{rep.root_cause}|"
            f"{rep.confidence}|{rep.evidence_ref}"
        )
        return {
            "report_id": rep.report_id,
            "class_ref": rep.class_ref,
            "root_cause": rep.root_cause,
            "confidence": rep.confidence,
            "evidence_ref": rep.evidence_ref,
            "authority": rep.authority,
            "content_hash": _hash(payload),
        }
