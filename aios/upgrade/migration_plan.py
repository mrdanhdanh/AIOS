"""Migration Plan & Engine (TASK-074 — Upgrade & Migration 1.0).

Implements the canonical Migration 1.0 contract:

    MigrationPlan
    ├── from_version
    ├── to_version
    ├── steps: [ {id, up, down, verify} ]
    ├── dry_run_supported: bool
    └── evidence_ref

Safety properties (all fail-closed / reversible / evidence / deterministic /
no data loss). Integrates with:
  * aios.upgrade            (existing upgrade pipeline — peer package)
  * aios.goal_durability    (durable state, T066-equivalent durable layer)
  * aios.harness.verification (T032 verification pipeline)

Architecture: aios.upgrade is an "unknown" layer, so importing peer/infra
modules (harness, goal_durability, upgrade.manifest) is permitted. Agents are
never imported.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from aios.goal_durability.contracts import DurableCheckpoint
from aios.harness.verification import Verdict, VerificationPipeline
from aios.upgrade.manifest import UpgradeManifest, UpgradeStep, UpgradeStepType

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

StepFn = Callable[["dict[str, Any]"], None]
VerifyFn = Callable[["dict[str, Any]"], bool]


class MigrationPhase(str, Enum):
    PENDING = "pending"
    VERIFYING = "verifying"
    APPLYING = "applying"
    COMPLETED = "completed"
    FAILED = "failed"
    DRY_RUN = "dry_run"
    ROLLED_BACK = "rolled_back"


class MigrationError(Exception):
    """Raised for unrecoverable migration configuration errors."""


# ---------------------------------------------------------------------------
# Plan model
# ---------------------------------------------------------------------------


@dataclass
class MigrationStep:
    """A single reversible migration step.

    Every step MUST provide ``down`` (reversible, fail-closed contract).
    ``verify`` is run BEFORE ``up``; if it returns False the step is NOT
    applied (fail-closed — no partial mutation).
    """

    id: str
    up: StepFn
    down: StepFn
    verify: VerifyFn
    description: str = ""

    def is_reversible(self) -> bool:
        return self.down is not None


@dataclass
class MigrationPlan:
    """Ordered, reversible migration plan from one version to another."""

    from_version: str
    to_version: str
    steps: list[MigrationStep] = field(default_factory=list)
    dry_run_supported: bool = True
    evidence_ref: str = ""

    @property
    def step_count(self) -> int:
        return len(self.steps)

    def is_fully_reversible(self) -> bool:
        return all(s.is_reversible() for s in self.steps)

    def compute_hash(self) -> str:
        content = f"{self.from_version}:{self.to_version}:{self.dry_run_supported}"
        for s in self.steps:
            content += f":{s.id}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_manifest(self) -> UpgradeManifest:
        """Peer integration: express this plan as the existing UpgradeManifest."""
        steps = [
            UpgradeStep(
                step_id=s.id,
                step_type=UpgradeStepType.DATA,
                description=s.description,
                reversible=s.is_reversible(),
            )
            for s in self.steps
        ]
        return UpgradeManifest(
            upgrade_id=f"mig-{self.from_version}-{self.to_version}",
            source_version=self.from_version,
            target_version=self.to_version,
            steps=steps,
            rollback_supported=self.is_fully_reversible(),
        )


# ---------------------------------------------------------------------------
# Evidence & report
# ---------------------------------------------------------------------------


@dataclass
class StepEvidence:
    evidence_id: str
    run_id: str
    step_id: str
    phase: str
    status: str
    content_hash: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "run_id": self.run_id,
            "step_id": self.step_id,
            "phase": self.phase,
            "status": self.status,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp,
        }


@dataclass
class MigrationReport:
    plan_id: str
    from_version: str
    to_version: str
    phase: MigrationPhase
    applied_steps: list[str] = field(default_factory=list)
    failed_step: str = ""
    error: str = ""
    evidence: list[StepEvidence] = field(default_factory=list)
    state_hash_before: str = ""
    state_hash_after: str = ""
    dry_run: bool = False
    duration_ms: float = 0.0

    @property
    def succeeded(self) -> bool:
        return self.phase == MigrationPhase.COMPLETED

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "phase": self.phase.value,
            "applied_steps": list(self.applied_steps),
            "failed_step": self.failed_step,
            "error": self.error,
            "evidence": [e.to_dict() for e in self.evidence],
            "state_hash_before": self.state_hash_before,
            "state_hash_after": self.state_hash_after,
            "dry_run": self.dry_run,
            "duration_ms": self.duration_ms,
        }


def _json_default(o: Any) -> Any:
    if isinstance(o, DurableCheckpoint):
        return o.to_dict()
    return str(o)


def hash_state(state: dict[str, Any]) -> str:
    """Deterministic hash of a (JSON-serialisable) state dict."""
    payload = json.dumps(state, sort_keys=True, default=_json_default)
    return hashlib.sha256(payload.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class MigrationEngine:
    """Detect version, select plan, run steps in order (fail-closed, reversible).

    Safety rules enforced:
      * verify FAIL -> step NOT applied (fail-closed).
      * every step must be reversible (have ``down``).
      * dry-run never mutates state.
      * every step writes provenance evidence.
      * same plan + state -> same result (deterministic).
    """

    def __init__(self) -> None:
        self._plans: dict[tuple[str, str], MigrationPlan] = {}
        self._version_resolver: Callable[["dict[str, Any]"], str] | None = None

    # -- registration ------------------------------------------------------
    def register_plan(self, plan: MigrationPlan) -> None:
        self._plans[(plan.from_version, plan.to_version)] = plan

    def set_version_resolver(self, fn: Callable[["dict[str, Any]"], str]) -> None:
        self._version_resolver = fn

    # -- version detection -------------------------------------------------
    def detect_current_version(self, state: dict[str, Any]) -> str:
        if self._version_resolver is not None:
            return self._version_resolver(state)
        return str(state.get("version", "0.0.0"))

    def select_plan(self, current: str, target: str) -> MigrationPlan:
        plan = self._plans.get((current, target))
        if plan is None:
            raise MigrationError(f"No plan registered from {current} to {target}")
        return plan

    # -- convenience -------------------------------------------------------
    def migrate(
        self,
        state: dict[str, Any],
        target: str,
        dry_run: bool = False,
        run_id: str | None = None,
    ) -> MigrationReport:
        current = self.detect_current_version(state)
        plan = self.select_plan(current, target)
        return self.run(plan, state, dry_run=dry_run, run_id=run_id)

    # -- verify (harness T032 integration) --------------------------------
    def _verify_step(
        self, step: MigrationStep, state: dict[str, Any], run_id: str
    ) -> tuple[bool, StepEvidence]:
        # Integrate with the T032 harness verification pipeline: the step's
        # verify callable becomes a postcondition; the resulting Verdict drives
        # the fail-closed decision and produces traceable evidence.
        pipeline = VerificationPipeline()
        pipeline.add_postcondition(lambda: bool(step.verify(state)))
        result = pipeline.verify(run_id=run_id)
        ok = result.verdict == Verdict.PASS
        evidence = StepEvidence(
            evidence_id=f"ev-{hashlib.sha256((run_id + step.id + 'verify').encode()).hexdigest()[:8]}",
            run_id=run_id,
            step_id=step.id,
            phase=MigrationPhase.VERIFYING.value,
            status="pass" if ok else "fail",
            content_hash=hash_state(state),
        )
        return ok, evidence

    # -- run ---------------------------------------------------------------
    def run(
        self,
        plan: MigrationPlan,
        state: dict[str, Any],
        dry_run: bool = False,
        run_id: str | None = None,
    ) -> MigrationReport:
        if not plan.is_fully_reversible():
            raise MigrationError("Plan contains irreversible steps (missing down)")
        if dry_run and not plan.dry_run_supported:
            raise MigrationError("Plan does not support dry-run")

        run_id = run_id or f"mig-{uuid.uuid4().hex[:8]}"
        start = time.time()
        state_hash_before = hash_state(state)
        report = MigrationReport(
            plan_id=f"{plan.from_version}->{plan.to_version}",
            from_version=plan.from_version,
            to_version=plan.to_version,
            phase=MigrationPhase.DRY_RUN if dry_run else MigrationPhase.PENDING,
            dry_run=dry_run,
            state_hash_before=state_hash_before,
        )

        applied: list[str] = []
        for step in plan.steps:
            ok, ev = self._verify_step(step, state, run_id)
            report.evidence.append(ev)
            if not ok:
                # Fail-closed: do NOT apply, leave state untouched.
                report.phase = MigrationPhase.FAILED
                report.failed_step = step.id
                report.error = f"verify FAILED for step {step.id} (fail-closed, not applied)"
                report.state_hash_after = hash_state(state)
                report.duration_ms = (time.time() - start) * 1000
                return report

            if dry_run:
                # Dry-run: verify only, never mutate.
                continue

            step.up(state)
            applied.append(step.id)
            report.evidence.append(
                StepEvidence(
                    evidence_id=f"ev-{hashlib.sha256((run_id + step.id + 'apply').encode()).hexdigest()[:8]}",
                    run_id=run_id,
                    step_id=step.id,
                    phase=MigrationPhase.APPLYING.value,
                    status="applied",
                    content_hash=hash_state(state),
                )
            )

        report.phase = MigrationPhase.DRY_RUN if dry_run else MigrationPhase.COMPLETED
        report.applied_steps = applied
        report.state_hash_after = hash_state(state)
        report.duration_ms = (time.time() - start) * 1000
        return report

    # -- rollback ----------------------------------------------------------
    def rollback(
        self,
        plan: MigrationPlan,
        state: dict[str, Any],
        applied_steps: list[str] | None = None,
        run_id: str | None = None,
    ) -> MigrationReport:
        run_id = run_id or f"rb-{uuid.uuid4().hex[:8]}"
        start = time.time()
        state_hash_before = hash_state(state)
        applied = applied_steps if applied_steps is not None else [s.id for s in plan.steps]

        rolled: list[str] = []
        evidence: list[StepEvidence] = []
        for step_id in reversed(applied):
            step = next((s for s in plan.steps if s.id == step_id), None)
            if step is None or step.down is None:
                continue
            step.down(state)
            rolled.append(step_id)
            evidence.append(
                StepEvidence(
                    evidence_id=f"ev-{hashlib.sha256((run_id + step_id + 'down').encode()).hexdigest()[:8]}",
                    run_id=run_id,
                    step_id=step_id,
                    phase=MigrationPhase.ROLLED_BACK.value,
                    status="rolled_back",
                    content_hash=hash_state(state),
                )
            )

        return MigrationReport(
            plan_id=f"{plan.from_version}->{plan.to_version}",
            from_version=plan.from_version,
            to_version=plan.to_version,
            phase=MigrationPhase.ROLLED_BACK,
            applied_steps=rolled,
            evidence=evidence,
            state_hash_before=state_hash_before,
            state_hash_after=hash_state(state),
            duration_ms=(time.time() - start) * 1000,
        )


# ---------------------------------------------------------------------------
# Sample durable-state migration step (T066 / goal_durability)
# ---------------------------------------------------------------------------


def sample_durable_migration_step() -> MigrationStep:
    """Sample state-migration step for durable state (T066 / goal_durability).

    Migrates a :class:`DurableCheckpoint` stored under ``state['checkpoint']``
    to schema version 1.1 by ADDING a ``schema_version`` key inside its
    ``goal_state``. All original fields are preserved (no data loss) and the
    step is fully reversible via ``down``.
    """

    def _up(state: dict[str, Any]) -> None:
        cp = state.get("checkpoint")
        if cp is None or not isinstance(cp, DurableCheckpoint):
            return
        # Preserve original content hash for no-data-loss verification.
        state["checkpoint_original_hash"] = cp.compute_hash()
        cp.goal_state["schema_version"] = "1.1"

    def _down(state: dict[str, Any]) -> None:
        cp = state.get("checkpoint")
        if cp is None or not isinstance(cp, DurableCheckpoint):
            return
        cp.goal_state.pop("schema_version", None)
        state.pop("checkpoint_original_hash", None)

    def _verify(state: dict[str, Any]) -> bool:
        cp = state.get("checkpoint")
        if cp is None or not isinstance(cp, DurableCheckpoint):
            return False
        # Applicability gate (fail-closed, pre-apply): only migrate when the
        # checkpoint exists and has NOT already been migrated (idempotent).
        return cp.goal_state.get("schema_version") != "1.1"

    return MigrationStep(
        id="migrate-durable-checkpoint",
        up=_up,
        down=_down,
        verify=_verify,
        description="Migrate durable checkpoint to schema 1.1 (no data loss)",
    )


def make_durable_migration_plan(from_version: str, to_version: str) -> MigrationPlan:
    """Build a plan that migrates durable state safely (T066)."""
    return MigrationPlan(
        from_version=from_version,
        to_version=to_version,
        steps=[sample_durable_migration_step()],
        dry_run_supported=True,
        evidence_ref="goal_durability",
    )
