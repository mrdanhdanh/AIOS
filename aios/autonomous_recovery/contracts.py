"""Autonomous Recovery contracts (TASK-055)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FailureClass(str, Enum):
    TRANSIENT = "transient"
    RESOURCE = "resource"
    DEPENDENCY = "dependency"
    POLICY = "policy"
    STATE = "state"
    LOGICAL = "logical"
    UNKNOWN = "unknown"


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RecoveryStrategy(str, Enum):
    RETRY = "retry"
    RESUME = "resume"
    FALLBACK = "fallback"
    ROLLBACK = "rollback"
    ESCALATE = "escalate"
    SAFE_STOP = "safe_stop"


class RecoveryVerdict(str, Enum):
    RECOVERED = "recovered"
    NOT_RECOVERED = "not_recovered"
    INCONCLUSIVE = "inconclusive"


@dataclass
class RecoveryAttempt:
    """Every recovery attempt is recorded with full provenance (spec §4)."""
    recovery_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    execution_id: str = ""
    failure: str = ""
    classification: FailureClass = FailureClass.UNKNOWN
    strategy: RecoveryStrategy = RecoveryStrategy.SAFE_STOP
    policy_decision: str = ""
    pre_state: dict[str, Any] = field(default_factory=dict)
    action: str = ""
    post_state: dict[str, Any] = field(default_factory=dict)
    verification: str = ""  # verdict string
    evidence: list[str] = field(default_factory=list)
    outcome: RecoveryVerdict = RecoveryVerdict.INCONCLUSIVE
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "recovery_id": self.recovery_id,
            "execution_id": self.execution_id,
            "classification": self.classification.value,
            "strategy": self.strategy.value,
            "policy_decision": self.policy_decision,
            "verification": self.verification,
            "evidence": list(self.evidence),
            "outcome": self.outcome.value,
        }
