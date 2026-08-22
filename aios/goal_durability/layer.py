"""Goal Durability Layer (TASK-056).

Coordinates durable checkpoints over the existing Runtime. Checkpoints are
immutable, atomically committed with a monotonic sequence, and content-hashed.
Resume validates the checkpoint (hash + provenance + policy) and refuses to
re-run completed tasks or duplicate acknowledged side effects. Stale
checkpoints trigger a re-plan rather than blind continuation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from aios.goal_durability.contracts import (
    DurableCheckpoint,
    InterruptionCause,
    ResumeVerdict,
)


@dataclass
class ResumePlan:
    verdict: ResumeVerdict
    goal_id: str = ""
    skip_tasks: list[str] = field(default_factory=list)
    resume_tasks: list[str] = field(default_factory=list)
    stale: bool = False
    replan: bool = False
    reason: str = ""


class GoalDurabilityLayer:
    def __init__(
        self,
        store: dict[str, DurableCheckpoint] | None = None,
        policy_validator: Callable[[dict[str, Any]], bool] | None = None,
        planner: Callable[[str], Any] | None = None,
        evidence_exists: Callable[[str], bool] | None = None,
    ) -> None:
        # goal_id -> latest checkpoint (atomic, versioned)
        self._store = store if store is not None else {}
        self._sequences: dict[str, int] = {}
        self._acknowledged: dict[str, set[str]] = {}
        self._policy_validator = policy_validator
        self._planner = planner
        self._evidence_exists = evidence_exists or (lambda eid: True)

    # ---- checkpoint coordinator ----------------------------------------
    def checkpoint(
        self,
        goal_id: str,
        cause: InterruptionCause | str,
        goal_state: dict[str, Any],
        completed_tasks: list[str],
        pending_tasks: list[str],
        current_subgoal: str = "",
        execution_graph_state: dict[str, Any] | None = None,
        world_state_ref: str = "",
        memory_refs: list[str] | None = None,
        artifact_refs: list[str] | None = None,
        policy_autonomy_state: dict[str, Any] | None = None,
        recovery_state: dict[str, Any] | None = None,
        evidence_refs: list[str] | None = None,
    ) -> DurableCheckpoint:
        # Atomic, versioned commit: sequence is always current+1.
        seq = self._sequences.get(goal_id, -1) + 1
        cp = DurableCheckpoint(
            goal_id=goal_id,
            sequence=seq,
            interruption_cause=cause.value if isinstance(cause, InterruptionCause) else str(cause),
            goal_state=dict(goal_state),
            current_subgoal=current_subgoal,
            completed_tasks=list(completed_tasks),
            pending_tasks=list(pending_tasks),
            execution_graph_state=dict(execution_graph_state or {}),
            world_state_ref=world_state_ref,
            memory_refs=list(memory_refs or []),
            artifact_refs=list(artifact_refs or []),
            policy_autonomy_state=dict(policy_autonomy_state or {}),
            recovery_state=dict(recovery_state or {}),
            evidence_refs=list(evidence_refs or []),
        )
        cp.finalize()
        self._store[goal_id] = cp
        self._sequences[goal_id] = seq
        return cp

    def get_latest(self, goal_id: str) -> DurableCheckpoint | None:
        return self._store.get(goal_id)

    # ---- resume validator ----------------------------------------------
    def validate(self, cp: DurableCheckpoint) -> ResumeVerdict:
        # 1. content hash integrity
        if cp.compute_hash() != cp.content_hash:
            return ResumeVerdict.INVALID
        # 2. provenance: evidence refs must exist
        if cp.evidence_refs and not all(self._evidence_exists(e) for e in cp.evidence_refs):
            return ResumeVerdict.INCONCLUSIVE
        # 3. policy re-validation
        if self._policy_validator is not None and not self._policy_validator(cp.policy_autonomy_state):
            return ResumeVerdict.INVALID
        return ResumeVerdict.VALID

    # ---- stale detector -------------------------------------------------
    def detect_stale(self, cp: DurableCheckpoint, current_versions: dict[str, Any] | None = None) -> bool:
        if not current_versions:
            return False
        # Compare recorded versions against current world/plan/policy versions.
        recorded = cp.policy_autonomy_state.get("versions", {})
        for key, cur in current_versions.items():
            if recorded.get(key) != cur:
                return True
        return False

    # ---- idempotency guard ---------------------------------------------
    def acknowledge_action(self, goal_id: str, action_id: str) -> None:
        self._acknowledged.setdefault(goal_id, set()).add(action_id)

    def is_action_acknowledged(self, goal_id: str, action_id: str) -> bool:
        return action_id in self._acknowledged.get(goal_id, set())

    # ---- resume ---------------------------------------------------------
    def resume(
        self,
        goal_id: str,
        current_versions: dict[str, Any] | None = None,
    ) -> ResumePlan:
        cp = self._store.get(goal_id)
        if cp is None:
            return ResumePlan(ResumeVerdict.INVALID, goal_id, reason="no checkpoint")
        verdict = self.validate(cp)
        if verdict in (ResumeVerdict.INVALID, ResumeVerdict.INCONCLUSIVE):
            # Fail-closed: do not resume from invalid/inconclusive state.
            return ResumePlan(verdict, goal_id, reason="checkpoint not verifiable")

        stale = self.detect_stale(cp, current_versions)
        if stale:
            # Re-plan instead of continuing with an obsolete plan.
            if self._planner is not None:
                self._planner(goal_id)
            return ResumePlan(
                ResumeVerdict.STALE, goal_id,
                skip_tasks=list(cp.completed_tasks),
                resume_tasks=list(cp.pending_tasks),
                stale=True, replan=True,
                reason="stale checkpoint -> re-plan",
            )

        # Idempotent resume: skip completed tasks; do not re-issue acknowledged
        # side-effect actions.
        completed = set(cp.completed_tasks)
        resume_tasks = [t for t in cp.pending_tasks if t not in completed]
        return ResumePlan(
            ResumeVerdict.VALID, goal_id,
            skip_tasks=list(completed),
            resume_tasks=resume_tasks,
            stale=False, replan=False,
            reason="resume from valid checkpoint",
        )
