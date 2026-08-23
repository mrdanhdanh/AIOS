"""TASK-204 — Recovery Orchestrator (M26).

Recovery orchestration for coding failures, converging Recovery (T055) and
Remediation (T094-T098). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from aios.coding_edition._common import CodingEditionError, _hash, _now


class FailureKind(str, Enum):
    """Classified failure kinds (T204)."""

    BUILD = "BUILD"
    TEST = "TEST"
    RUNTIME = "RUNTIME"
    POLICY = "POLICY"
    UNKNOWN = "UNKNOWN"


@dataclass
class Failure:
    """A detected failure to recover from (T204)."""

    failure_id: str
    kind: FailureKind
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.failure_id:
            raise CodingEditionError("failure_id is required (T001 Rule 1, immutable).")


@dataclass
class RecoveryStep:
    """A single recovery action (T204)."""

    action: str
    target: str


@dataclass
class RecoveryPlan:
    """An immutable-by-id recovery plan (T204)."""

    plan_id: str
    failure_id: str
    steps: List[RecoveryStep]
    strategy: str
    at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.plan_id:
            raise CodingEditionError("plan_id is required (T001 Rule 1, immutable).")
        if not self.steps:
            raise CodingEditionError("recovery plan requires at least one step.")


# Deterministic strategy selection per failure kind.
_STRATEGY: Dict[FailureKind, str] = {
    FailureKind.BUILD: "rebuild",
    FailureKind.TEST: "rerun-tests",
    FailureKind.RUNTIME: "rollback",
    FailureKind.POLICY: "escalate",
    FailureKind.UNKNOWN: "diagnose",
}


class RecoveryOrchestrator:
    """Deterministic recovery orchestrator (T204)."""

    def __init__(self, run_id: Optional[str] = None) -> None:
        self._run_id = run_id or f"rec-{uuid.uuid4().hex[:12]}"

    @property
    def run_id(self) -> str:
        return self._run_id

    def plan(self, failure: Failure) -> RecoveryPlan:
        """Build a deterministic recovery plan for ``failure`` (fail-closed)."""
        strategy = _STRATEGY.get(failure.kind, "diagnose")
        steps = [RecoveryStep(action=strategy, target=failure.failure_id)]
        if failure.kind == FailureKind.RUNTIME:
            steps.append(RecoveryStep(action="snapshot-restore", target=failure.failure_id))
        if failure.kind == FailureKind.POLICY:
            steps.append(RecoveryStep(action="request-approval", target=failure.failure_id))
        return RecoveryPlan(
            plan_id=f"rp-{uuid.uuid4().hex[:8]}",
            failure_id=failure.failure_id,
            steps=steps,
            strategy=strategy,
        )

    def plan_hash(self, failure: Failure) -> str:
        p = self.plan(failure)
        payload = "|".join(f"{s.action}:{s.target}" for s in p.steps)
        return _hash(f"{failure.failure_id}|{p.strategy}|{payload}")
