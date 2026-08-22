"""Advanced Stuck Detection contracts (TASK-061)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StuckKind(str, Enum):
    NO_PROGRESS = "no_progress"
    OSCILLATION = "oscillation"
    PLATEAU = "plateau"
    RESOURCE_BURN = "resource_burn"
    DEADLOCK = "deadlock"


class StuckSeverity(str, Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass
class StuckSignal:
    signal_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    kind: StuckKind = StuckKind.NO_PROGRESS
    severity: StuckSeverity = StuckSeverity.MINOR
    iteration_first_seen: int = 0
    confidence: float = 0.0  # based on evidence, not guesswork
    evidence_ref: str = ""  # provenance to trajectory/metrics
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "kind": self.kind.value,
            "severity": self.severity.value,
            "iteration_first_seen": self.iteration_first_seen,
            "confidence": self.confidence,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class StuckPolicy:
    """Policy-driven mapping of StuckSignal → candidate action.

    Not a hard 1:1 mapping: severity/confidence/evidence drive the decision.
    """
    # Default candidate per kind (deterministic baseline).
    no_progress_action: str = "escalate"
    oscillation_action: str = "safe_stop"
    plateau_action: str = "recover"
    resource_burn_action: str = "escalate"
    deadlock_action: str = "safe_stop"
    # Fail-closed: low confidence / missing evidence -> escalate, never ignore.
    low_confidence_threshold: float = 0.5

    def resolve(self, signal: StuckSignal) -> str:
        if not signal.evidence_ref or signal.confidence < self.low_confidence_threshold:
            # Fail-closed: do not auto-continue; escalate for human/policy.
            return "escalate"
        mapping = {
            StuckKind.NO_PROGRESS: self.no_progress_action,
            StuckKind.OSCILLATION: self.oscillation_action,
            StuckKind.PLATEAU: self.plateau_action,
            StuckKind.RESOURCE_BURN: self.resource_burn_action,
            StuckKind.DEADLOCK: self.deadlock_action,
        }
        return mapping.get(signal.kind, "escalate")
