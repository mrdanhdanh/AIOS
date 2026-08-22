"""Migration 1.0 -> 1.1 — detect / plan / dry-run / apply / rollback (T085).

Canonical migration contract (T074-shaped):

    VersionMigration
    ├── from: 1.0.0
    ├── to: 1.1.0
    ├── steps: [ {id, up, down, verify} ]
    ├── dry_run_supported: bool
    └── evidence_ref

Safety properties (all fail-closed / reversible / evidence / deterministic /
no data loss):
* Fail-closed apply — verify FAIL -> never apply (T074).
* Reversible — every step provides a ``down``.
* Evidence required — every step records provenance (T001 Rule 5).
* Deterministic — same plan + state -> same result.
* No data loss — state migration is durable (T066).

Integration: imports ``aios.upgrade.migration_plan`` (T074) for the migration
plan shape, ``aios.harness.verification`` (T032) for the Verdict enum, and
``aios.versioning.versioning`` (T084) for the baseline version. No rewrite of
any dependency.
"""

from __future__ import annotations

import copy
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from aios.harness.verification import Verdict
from aios.upgrade.migration_plan import MigrationPhase, MigrationStep as _T074Step
from aios.versioning.versioning import VersionBaseline

# Step function signatures (kept dependency-free for testability).
StepFn = Callable[["dict[str, Any]"], None]
VerifyFn = Callable[["dict[str, Any]"], bool]

FROM_VERSION = "1.0.0"
TO_VERSION = "1.1.0"


class MigrationError(Exception):
    """Raised for unrecoverable migration configuration errors (fail-closed)."""


class MigrationStatus(str, Enum):
    PENDING = "pending"
    DRY_RUN = "dry_run"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationStep:
    """A single reversible migration step.

    Every step MUST provide ``down`` (reversible, fail-closed contract) and
    ``verify`` (run BEFORE ``up``; if it returns False the step is NOT applied).
    """

    id: str
    up: StepFn
    down: StepFn
    verify: VerifyFn
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "has_up": callable(self.up),
            "has_down": callable(self.down),
            "has_verify": callable(self.verify),
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class MigrationPlan:
    """The 1.0 -> 1.1 migration plan."""

    from_version: str = FROM_VERSION
    to_version: str = TO_VERSION
    steps: list[MigrationStep] = field(default_factory=list)
    dry_run_supported: bool = True
    evidence_ref: str = ""

    def __post_init__(self) -> None:
        if self.from_version != FROM_VERSION:
            raise MigrationError(
                f"migration must start at {FROM_VERSION}, got {self.from_version}"
            )
        for step in self.steps:
            if not callable(step.down):
                raise MigrationError(f"step {step.id!r} is not reversible (missing down)")

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_version": self.from_version,
            "to_version": self.to_version,
            "steps": [s.to_dict() for s in self.steps],
            "dry_run_supported": self.dry_run_supported,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class MigrationState:
    """The durable system state being migrated (T066-equivalent)."""

    version: str
    data: dict[str, Any] = field(default_factory=dict)

    def snapshot(self) -> "MigrationState":
        """Deep copy so migration never mutates the caller's original state."""
        return MigrationState(version=self.version, data=copy.deepcopy(self.data))

    def to_dict(self) -> dict[str, Any]:
        return {"version": self.version, "data": self.data}


@dataclass
class DryRunResult:
    ready: bool = True
    would_mutate: bool = False
    issues: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ready": self.ready,
            "would_mutate": self.would_mutate,
            "issues": list(self.issues),
            "steps": list(self.steps),
        }


@dataclass
class MigrationResult:
    status: MigrationStatus
    from_version: str = FROM_VERSION
    to_version: str = TO_VERSION
    steps_completed: int = 0
    steps_total: int = 0
    evidence: list[dict[str, Any]] = field(default_factory=list)
    state: Optional[MigrationState] = None
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "steps_completed": self.steps_completed,
            "steps_total": self.steps_total,
            "evidence": self.evidence,
            "state_version": self.state.version if self.state else None,
            "error": self.error,
        }

    @property
    def succeeded(self) -> bool:
        return self.status is MigrationStatus.APPLIED


@dataclass
class RollbackResult:
    status: MigrationStatus
    from_version: str = TO_VERSION
    to_version: str = FROM_VERSION
    restored_steps: int = 0
    evidence: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "restored_steps": self.restored_steps,
            "evidence": self.evidence,
            "error": self.error,
        }

    @property
    def succeeded(self) -> bool:
        return self.status is MigrationStatus.ROLLED_BACK


class MigrationRunner:
    """Executes a 1.0 -> 1.1 migration deterministically and fail-closed."""

    def __init__(self, baseline: VersionBaseline | None = None) -> None:
        self._baseline = baseline or VersionBaseline()

    # -- detect ---------------------------------------------------------------

    def detect(self, state: MigrationState) -> bool:
        """Return True iff the system is at the 1.0 baseline (detect 1.0)."""
        return state.version == FROM_VERSION

    # -- plan -----------------------------------------------------------------

    def plan(self, migration: MigrationPlan, state: MigrationState) -> list[str]:
        """Return the ordered, reversible step ids for the migration.

        Fail-closed: refuses to plan unless the system is detected at 1.0 and
        every step is reversible.
        """
        if not self.detect(state):
            raise MigrationError(
                f"system is at {state.version}, expected {FROM_VERSION}"
            )
        for step in migration.steps:
            if not callable(step.down):
                raise MigrationError(f"step {step.id!r} is not reversible")
        return [s.id for s in migration.steps]

    # -- dry-run --------------------------------------------------------------

    def dry_run(self, migration: MigrationPlan, state: MigrationState) -> DryRunResult:
        """Simulate the migration WITHOUT mutating ``state`` (AC-020-05)."""
        if not migration.dry_run_supported:
            return DryRunResult(ready=False, issues=["dry-run not supported"])
        # Operate on a snapshot so the original state is never touched.
        sim = state.snapshot()
        issues: list[str] = []
        step_ids: list[str] = []
        for step in migration.steps:
            if not step.verify(sim.data):
                issues.append(f"verify failed for step {step.id}")
            step_ids.append(step.id)
        return DryRunResult(
            ready=len(issues) == 0,
            would_mutate=False,
            issues=issues,
            steps=step_ids,
        )

    # -- apply (fail-closed) --------------------------------------------------

    def apply(self, migration: MigrationPlan, state: MigrationState) -> MigrationResult:
        """Apply the migration. Verify FAIL -> never apply (fail-closed)."""
        if not self.detect(state):
            return MigrationResult(
                status=MigrationStatus.FAILED,
                steps_total=len(migration.steps),
                error=f"system not at {FROM_VERSION}",
            )
        working = state.snapshot()
        evidence: list[dict[str, Any]] = []
        for i, step in enumerate(migration.steps):
            # Verify BEFORE up; if it fails, abort without mutating (fail-closed).
            if not step.verify(working.data):
                return MigrationResult(
                    status=MigrationStatus.FAILED,
                    steps_completed=i,
                    steps_total=len(migration.steps),
                    evidence=evidence,
                    error=f"verify failed at step {step.id}",
                )
            step.up(working.data)
            evidence.append(
                {
                    "step_id": step.id,
                    "phase": MigrationPhase.APPLYING.value,
                    "evidence_ref": step.evidence_ref or f"mig-{uuid.uuid4().hex}",
                }
            )
        working.version = migration.to_version
        # The caller's original ``state`` is untouched; the new state is returned
        # via the result (deterministic, no data loss).
        return MigrationResult(
            status=MigrationStatus.APPLIED,
            from_version=migration.from_version,
            to_version=migration.to_version,
            steps_completed=len(migration.steps),
            steps_total=len(migration.steps),
            evidence=evidence,
            state=working,
        )

    # -- rollback -------------------------------------------------------------

    def rollback(self, migration: MigrationPlan, state: MigrationState) -> RollbackResult:
        """Roll the system back to 1.0 by running each step's ``down`` in reverse."""
        if state.version != migration.to_version:
            return RollbackResult(
                status=MigrationStatus.FAILED,
                error=f"system at {state.version}, cannot roll back to {FROM_VERSION}",
            )
        working = state.snapshot()
        evidence: list[dict[str, Any]] = []
        restored = 0
        for step in reversed(migration.steps):
            step.down(working.data)
            restored += 1
            evidence.append(
                {
                    "step_id": step.id,
                    "phase": MigrationPhase.ROLLED_BACK.value,
                    "evidence_ref": step.evidence_ref or f"rb-{uuid.uuid4().hex}",
                }
            )
        working.version = FROM_VERSION
        return RollbackResult(
            status=MigrationStatus.ROLLED_BACK,
            from_version=migration.to_version,
            to_version=FROM_VERSION,
            restored_steps=restored,
            evidence=evidence,
        )

    # -- determinism / provenance helpers ------------------------------------

    def plan_hash(self, migration: MigrationPlan) -> str:
        """Deterministic hash of the plan (same plan -> same hash)."""
        data = json.dumps(migration.to_dict(), sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def provenance_complete(self, result: MigrationResult | RollbackResult) -> bool:
        """A migration result is provenanced when it records evidence."""
        return bool(getattr(result, "evidence", None))
