"""Harness contracts — canonical types for specs, runs, results, and assertions."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RunStatus(Enum):
    """Lifecycle states for a HarnessRun."""
    CREATED = "created"
    PREPARING = "preparing"
    VALIDATING = "validating"
    RUNNING = "running"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    DIAGNOSED = "diagnosed"


_VALID_TRANSITIONS: dict[RunStatus, set[RunStatus]] = {
    RunStatus.CREATED: {RunStatus.PREPARING, RunStatus.FAILED},
    RunStatus.PREPARING: {RunStatus.VALIDATING, RunStatus.FAILED},
    RunStatus.VALIDATING: {RunStatus.RUNNING, RunStatus.FAILED},
    RunStatus.RUNNING: {RunStatus.VERIFYING, RunStatus.FAILED},
    RunStatus.VERIFYING: {RunStatus.COMPLETED, RunStatus.FAILED},
    RunStatus.COMPLETED: set(),
    RunStatus.FAILED: {RunStatus.DIAGNOSED},
    RunStatus.DIAGNOSED: set(),
}


class HarnessError(Exception):
    """Raised on harness contract or lifecycle errors."""


@dataclass(frozen=True)
class Assertion:
    """A single verifiable claim about a harness run outcome."""
    name: str
    passed: bool
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


@dataclass
class HarnessSpec:
    """Declarative specification of a harness."""
    spec_id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    target: str = ""
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "spec_id": self.spec_id, "name": self.name, "version": self.version,
            "target": self.target, "preconditions": self.preconditions,
            "postconditions": self.postconditions, "invariants": self.invariants,
        }

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(str(self.to_dict()).encode()).hexdigest()[:16]


@dataclass
class HarnessRun:
    """An execution instance of a HarnessSpec."""
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    spec_id: str = ""
    status: RunStatus = RunStatus.CREATED
    result: RunResult | None = None

    def transition(self, new_status: RunStatus) -> None:
        allowed = _VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise HarnessError(f"Invalid: {self.status.value} → {new_status.value}")
        self.status = new_status

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id, "spec_id": self.spec_id,
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
        }


@dataclass
class RunResult:
    """Outcome produced by a harness run."""
    passed: bool = False
    verdict: str = "PENDING"
    assertions: list[Assertion] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed, "verdict": self.verdict,
            "assertions": [a.to_dict() for a in self.assertions],
            "evidence_refs": self.evidence_refs,
        }
