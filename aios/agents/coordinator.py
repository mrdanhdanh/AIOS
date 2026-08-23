"""Coordinator agent role (prototype, TASK-controller).

A top-level *pure* agent that **coordinates** the other agent roles
(Spec-Writer, Critic, Reviewer, Orchestrator). It performs no work itself; it
drives the governance-aligned pipeline:

    spec -> critique x2 -> breakdown(tasks) -> review -> orchestrate/close

Per Rule 3 (Architecture Guard, ARCH-001..004) it MUST NOT import execution
primitives (``subprocess``), provider adapters or filesystem adapters directly;
it acts only through the agent interfaces injected into it. It is pure
(I/O-free), deterministic (same inputs -> same coordination result) and
fail-closed (any missing mandatory artifact rejects the run before closing).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Protocol


class SpecWriterLike(Protocol):
    def render(self, spec) -> str: ...
    def to_artifact(self, spec) -> Dict[str, str]: ...


class CriticLike(Protocol):
    def critique(self, spec_text: str, round_no: int, prior_findings=None): ...


class ReviewerLike(Protocol):
    def review(self, artifacts: Dict[str, str]): ...


class OrchestratorLike(Protocol):
    def advance(self, task_id: str, to_state: str, artifacts=None) -> str: ...
    def can_close(self, task_id: str) -> bool: ...
    def close_if_gate_passes(self, task_id: str) -> bool: ...


@dataclass
class CoordinationStep:
    name: str
    status: str  # OK | SKIPPED | FAILED
    detail: str


@dataclass
class CoordinationResult:
    task_id: str
    steps: List[CoordinationStep] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)
    approved: bool = False
    closed: bool = False

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "steps": [
                {"name": s.name, "status": s.status, "detail": s.detail}
                for s in self.steps
            ],
            "artifacts": sorted(self.artifacts.keys()),
            "approved": self.approved,
            "closed": self.closed,
        }


class CoordinatorAgent:
    """Coordinates the agent roles to drive a task to a reviewable/closed state.

    All collaborators are injected (capability-injection, ARCH-004); the agent
    never reaches into runtime/tool/provider layers directly.
    """

    def __init__(
        self,
        spec_writer: SpecWriterLike,
        critic: CriticLike,
        reviewer: ReviewerLike,
        orchestrator: OrchestratorLike,
    ) -> None:
        self._spec_writer = spec_writer
        self._critic = critic
        self._reviewer = reviewer
        self._orchestrator = orchestrator

    def coordinate(self, task_id: str, spec_input) -> CoordinationResult:
        """Run the full coordination pipeline for ``task_id``.

        Fail-closed: if the review rejects the artifact set, the task is NOT
        closed and the result reports ``approved=False``.
        """
        result = CoordinationResult(task_id=task_id)

        # 1) Specification
        spec_text = self._spec_writer.render(spec_input)
        result.artifacts["spec.md"] = spec_text
        result.steps.append(
            CoordinationStep("spec", "OK", f"{len(spec_text)} chars rendered")
        )

        # 2) Critique x2 (deterministic analysis over the spec)
        c1 = self._critic.critique(spec_text, 1)
        result.artifacts["critique-1.md"] = (
            f"verdict={c1.verdict}; findings={c1.findings}"
        )
        result.steps.append(CoordinationStep("critique-1", "OK", c1.verdict))
        c2 = self._critic.critique(spec_text, 2, prior_findings=getattr(c1, "findings", None))
        result.artifacts["critique-2.md"] = (
            f"verdict={c2.verdict}; findings={c2.findings}"
        )
        result.steps.append(CoordinationStep("critique-2", "OK", c2.verdict))

        # 3) Breakdown -> tasks.md (minimal, derived from spec deliverables)
        tasks_text = self._breakdown(spec_input)
        result.artifacts["tasks.md"] = tasks_text
        result.steps.append(
            CoordinationStep("breakdown", "OK", f"{len(tasks_text)} chars")
        )

        # 4) Review (fail-closed gate before implementation)
        review = self._reviewer.review(result.artifacts)
        result.approved = bool(getattr(review, "approved", False))
        if not result.approved:
            result.steps.append(
                CoordinationStep(
                    "review", "FAILED", "; ".join(getattr(review, "notes", []))
                )
            )
            return result
        result.steps.append(
            CoordinationStep("review", "OK", "; ".join(getattr(review, "notes", [])))
        )

        # 5) Orchestrate / close (only when gate + lifecycle allow)
        closed = bool(self._orchestrator.close_if_gate_passes(task_id))
        result.closed = closed
        result.steps.append(
            CoordinationStep(
                "orchestrate",
                "OK" if closed else "SKIPPED",
                "task closed" if closed else "gate/lifecycle not satisfied",
            )
        )
        return result

    @staticmethod
    def _breakdown(spec_input) -> str:
        """Produce a minimal tasks.md from the spec's deliverables."""
        deliverables = getattr(spec_input, "deliverables", []) or []
        lines = [f"# {getattr(spec_input, 'task_id', 'TASK')} — Task Breakdown", ""]
        if deliverables:
            lines += ["## Tasks"] + [f"- [ ] {d}" for d in deliverables]
        else:
            lines += ["## Tasks", "- (none specified)"]
        return "\n".join(lines)
