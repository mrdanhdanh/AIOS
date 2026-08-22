"""Autonomous Memory contracts (TASK-057)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemoryScope(str, Enum):
    EXECUTION = "execution"
    GOAL = "goal"
    SESSION = "session"
    TENANT = "tenant"


class TrustStatus(str, Enum):
    UNTRUSTED = "untrusted"
    TRUSTED = "trusted"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"


@dataclass
class FailureMemoryEntry:
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal_id: str = ""
    execution_id: str = ""
    failure_class: str = ""  # from TASK-055 (TRANSIENT/RESOURCE/...)
    classification: str = ""
    recovery_strategy: str = ""
    outcome: str = ""  # recovered / safe_stopped
    evidence_ref: str = ""  # must be valid (provenance chain complete)
    retrieval_metadata: dict[str, Any] = field(default_factory=dict)  # tags/scope hints, NOT embedding_key
    created_at: float = field(default_factory=time.time)
    scope: MemoryScope = MemoryScope.GOAL

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id, "goal_id": self.goal_id,
            "execution_id": self.execution_id, "failure_class": self.failure_class,
            "outcome": self.outcome, "evidence_ref": self.evidence_ref,
            "scope": self.scope.value,
        }


@dataclass
class GoalMemoryEntry:
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal_id: str = ""
    execution_id: str = ""
    plan_ref: str = ""
    outcome: str = ""  # completed / failed / paused
    observation: dict[str, Any] = field(default_factory=dict)  # raw, not trusted
    lesson_candidate: str = ""  # derived lesson, NOT trusted by default
    evidence_ref: str = ""  # must be valid
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    trust_status: TrustStatus = TrustStatus.UNTRUSTED
    created_at: float = field(default_factory=time.time)
    scope: MemoryScope = MemoryScope.GOAL

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id, "goal_id": self.goal_id,
            "outcome": self.outcome, "lesson_candidate": self.lesson_candidate,
            "evidence_ref": self.evidence_ref,
            "verification_status": self.verification_status.value,
            "trust_status": self.trust_status.value, "scope": self.scope.value,
        }
