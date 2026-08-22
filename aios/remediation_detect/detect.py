"""Remediation Detect + Diagnose (TASK-094, M14).

Canonical diagnosis contract:

    Diagnosis
    ├── incident_id
    ├── symptoms: [..]
    ├── root_cause
    ├── confidence        # evidence-based
    ├── causal_trace
    └── evidence_ref

Safety properties (all fail-closed / causal-trace / provenance / deterministic):
* Fail-closed diagnosis — missing evidence -> escalate, never conclude.
* Causal trace — root cause must be traceable (no guessing).
* Evidence required — every diagnosis carries provenance (T001 Rule 5).
* Deterministic — same incident + same evidence -> same diagnosis.
* No parallel diagnosis system — uses Stuck (T061) + Observability (T065/T069)
  + Evidence (T001).

Integration: imports ``aios.stuck_detection`` (StuckDetector, IterationSample),
``aios.observability`` (MetricsCollector, AuditService) and
``aios.governance.evidence.store`` (EvidenceStore, Evidence). No rewrite of any
dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional

from aios.governance.evidence.store import Evidence, EvidenceStore
from aios.observability.audit import AuditService
from aios.observability.metrics import MetricsCollector
from aios.stuck_detection.detector import IterationSample, StuckDetector


class SymptomSeverity(str, Enum):
    """Severity of an observed symptom."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Symptom:
    """An observed symptom of an incident, captured with evidence."""

    symptom_id: str
    description: str
    evidence_ref: str = ""
    severity: SymptomSeverity = SymptomSeverity.MEDIUM

    def to_dict(self) -> dict[str, Any]:
        return {
            "symptom_id": self.symptom_id,
            "description": self.description,
            "evidence_ref": self.evidence_ref,
            "severity": self.severity.value,
        }


@dataclass
class Incident:
    """A detected anomaly / failure / deviation (the thing to diagnose)."""

    incident_id: str
    kind: str  # anomaly | failure | deviation
    severity: str
    signal: dict[str, Any] = field(default_factory=dict)  # stuck signal dict
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "kind": self.kind,
            "severity": self.severity,
            "signal": dict(self.signal),
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class Diagnosis:
    """Fail-closed diagnosis of an incident (root cause + causal trace)."""

    incident_id: str
    symptoms: List[Symptom]
    root_cause: str
    confidence: float  # evidence-based, never guessed
    causal_trace: List[str]
    evidence_ref: str = ""
    escalated: bool = False  # True when fail-closed (no evidence / no trace)

    def is_traceable(self) -> bool:
        """Root cause is traceable iff a causal chain + root cause exist."""
        return bool(self.causal_trace) and bool(self.root_cause) and not self.escalated

    def canonical(self) -> str:
        """Deterministic canonical serialization (used for hashing / evidence)."""
        payload = {
            "incident_id": self.incident_id,
            "symptoms": [s.to_dict() for s in self.symptoms],
            "root_cause": self.root_cause,
            "confidence": round(self.confidence, 4),
            "causal_trace": list(self.causal_trace),
            "evidence_ref": self.evidence_ref,
            "escalated": self.escalated,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "symptoms": [s.to_dict() for s in self.symptoms],
            "root_cause": self.root_cause,
            "confidence": self.confidence,
            "causal_trace": list(self.causal_trace),
            "evidence_ref": self.evidence_ref,
            "escalated": self.escalated,
            "traceable": self.is_traceable(),
        }


class DetectDiagnoseEngine:
    """Detect anomalies/failures/deviations and diagnose root cause (fail-closed)."""

    def __init__(
        self,
        evidence_store: Optional[EvidenceStore] = None,
        stuck_detector: Optional[StuckDetector] = None,
        metrics: Optional[MetricsCollector] = None,
        audit: Optional[AuditService] = None,
    ) -> None:
        self._evidence = evidence_store or EvidenceStore()
        self._stuck = stuck_detector or StuckDetector()
        self._metrics = metrics or MetricsCollector()
        self._audit = audit or AuditService()

    # -- detect ---------------------------------------------------------------

    def observe(
        self,
        iteration: int,
        progress: float,
        cost: float,
        state_hash: str,
        evidence_ref: str = "",
    ) -> None:
        """Feed one loop iteration into observability + stuck detection (T061)."""
        self._stuck.observe(
            IterationSample(iteration, progress, cost, state_hash, evidence_ref)
        )
        self._metrics.record_execution(success=progress >= 0.0)

    def detect(self) -> Optional[Incident]:
        """Detect an anomaly/failure/deviation via observability (T061/T065/T069)."""
        sig = self._stuck.detect()
        if sig is None:
            return None
        return Incident(
            incident_id=f"inc-{hashlib.sha256(sig.signal_id.encode()).hexdigest()[:8]}",
            kind=sig.kind.value,
            severity=sig.severity.value,
            signal=sig.to_dict(),
            evidence_ref=sig.evidence_ref,
        )

    # -- symptom capture ------------------------------------------------------

    def capture_symptom(
        self,
        symptom_id: str,
        description: str,
        evidence_ref: str,
        severity: SymptomSeverity = SymptomSeverity.MEDIUM,
    ) -> Symptom:
        """Capture a symptom with evidence (T001 provenance)."""
        return Symptom(symptom_id, description, evidence_ref, severity)

    # -- diagnose (fail-closed) ----------------------------------------------

    def diagnose(
        self,
        incident: Optional[Incident],
        symptoms: List[Symptom],
        causal_trace: List[str],
        evidence_ref: str = "",
    ) -> Diagnosis:
        """Diagnose root cause. Fail-closed: missing evidence / no trace -> escalate.

        Deterministic: same incident + same symptoms + same trace -> same diagnosis.
        """
        has_evidence = bool(symptoms) and all(s.evidence_ref for s in symptoms)
        if incident is None or not has_evidence or not causal_trace:
            # Fail-closed: never conclude without evidence + a traceable chain.
            diag = Diagnosis(
                incident_id=incident.incident_id if incident else "",
                symptoms=list(symptoms),
                root_cause="",
                confidence=0.0,
                causal_trace=list(causal_trace),
                evidence_ref=evidence_ref,
                escalated=True,
            )
            self._audit.record(
                who="remediation_detect",
                what="diagnose_escalated",
                result="escalated",
                provenance=[evidence_ref] if evidence_ref else [],
            )
            return diag

        # Evidence-based confidence (never guessed): more evidence + longer trace
        # raises confidence, capped at 1.0.
        confidence = round(
            min(1.0, 0.4 + 0.15 * len(symptoms) + 0.1 * len(causal_trace)), 4
        )
        diag = Diagnosis(
            incident_id=incident.incident_id,
            symptoms=list(symptoms),
            root_cause=causal_trace[-1],
            confidence=confidence,
            causal_trace=list(causal_trace),
            evidence_ref=evidence_ref,
            escalated=False,
        )
        self._record_evidence(diag)
        return diag

    def _record_evidence(self, diag: Diagnosis) -> str:
        ev_id = diag.evidence_ref or (
            f"diag-{hashlib.sha256(diag.incident_id.encode()).hexdigest()[:8]}"
        )
        self._evidence.add_evidence(
            evidence_id=ev_id,
            task_id="TASK-094",
            run_id="run-094",
            producer="remediation_detect",
            type="diagnosis",
            source=diag.incident_id,
            content=diag.canonical(),
        )
        diag.evidence_ref = ev_id
        return ev_id

    # -- determinism / provenance ---------------------------------------------

    def provenance_complete(self, diag: Diagnosis) -> bool:
        """Every diagnosis carries provenance (T001 Rule 5)."""
        return bool(diag.evidence_ref)

    def result_hash(self, diag: Diagnosis) -> str:
        """Deterministic hash (same diagnosis -> same hash)."""
        return hashlib.sha256(diag.canonical().encode("utf-8")).hexdigest()
