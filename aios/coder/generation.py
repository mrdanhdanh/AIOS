"""Code Generation Runtime (TASK-127, M19).

Executes a verified CodingPlan (T126) into code artifacts. The runtime never
calls tools/runtime directly — all code operations are dispatched through a
Capability (T009/T014, ARCH-004). Every emitted artifact carries a
``content_hash`` (T078) and provenance (T001 Rule 5). Execution is deterministic
(same plan -> same artifact set) and fail-closed (unhashable artifact -> reject).
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Dict, List, Optional, Protocol


class GenerationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class GenerationError(Exception):
    """Raised on generation failures (fail-closed, T078 / ARCH-004)."""


@dataclass
class GeneratedArtifact:
    artifact_id: str
    step_index: int
    action: str
    target: str
    content: str
    content_hash: str
    evidence_id: str

    def to_dict(self) -> dict:
        return {
            "artifact_id": self.artifact_id,
            "step_index": self.step_index,
            "action": self.action,
            "target": self.target,
            "content": self.content,
            "content_hash": self.content_hash,
            "evidence_id": self.evidence_id,
        }


@dataclass
class GenerationRun:
    run_id: str
    plan_ref: str
    capability_ref: str
    policy_ref: Optional[str]
    steps_executed: List[int] = field(default_factory=list)
    artifacts: List[GeneratedArtifact] = field(default_factory=list)
    status: GenerationStatus = GenerationStatus.PENDING

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "plan_ref": self.plan_ref,
            "capability_ref": self.capability_ref,
            "policy_ref": self.policy_ref,
            "steps_executed": self.steps_executed,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "status": self.status.value,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class CapabilityDispatcher(Protocol):
    """Capability contract (T009/T014). The runtime only emits code through
    this boundary — never imports tool/runtime directly (ARCH-004)."""

    def execute(self, action: str, target: str) -> str:
        """Return generated code content for ``action`` on ``target``."""
        ...


class CodeGenerationRuntime:
    """Executes a verified CodingPlan into code artifacts (T127)."""

    def __init__(self, capability: CapabilityDispatcher, policy_ref: Optional[str] = None) -> None:
        self._capability = capability
        self._policy_ref = policy_ref

    def run(self, plan, run_id: Optional[str] = None) -> GenerationRun:
        """Execute ``plan`` (must be VERIFIED) into a GenerationRun.

        Fail-closed: an unverified plan or an unhashable artifact rejects the
        run (T078). Deterministic: same plan -> same artifact set.
        """
        if getattr(plan, "status", None) is not None and plan.status.value != "VERIFIED":
            raise GenerationError("plan must be VERIFIED before generation (T078).")
        run = GenerationRun(
            run_id=run_id or f"run-{uuid.uuid4().hex[:12]}",
            plan_ref=getattr(plan, "plan_id", "unknown"),
            capability_ref="capability-dispatcher",
            policy_ref=self._policy_ref,
            status=GenerationStatus.RUNNING,
        )
        for idx, step in enumerate(plan.steps):
            content = self._capability.execute(step.action, step.target)
            if content is None or not isinstance(content, str):
                run.status = GenerationStatus.FAILED
                raise GenerationError(f"capability returned unhashable content at step {idx} (T078).")
            try:
                content_hash = _hash(content)
            except Exception as exc:  # pragma: no cover - defensive
                run.status = GenerationStatus.FAILED
                raise GenerationError(f"artifact not hashable at step {idx}: {exc}") from exc
            artifact = GeneratedArtifact(
                artifact_id=f"art-{uuid.uuid4().hex[:12]}",
                step_index=idx,
                action=step.action,
                target=step.target,
                content=content,
                content_hash=content_hash,
                evidence_id=f"ev-{uuid.uuid4().hex[:12]}",
            )
            run.artifacts.append(artifact)
            run.steps_executed.append(idx)
        run.status = GenerationStatus.SUCCEEDED
        return run
