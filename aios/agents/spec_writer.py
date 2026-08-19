"""Spec-writer role.

Produces the ``spec.md`` content for a task from the master specification. It
operates purely on text/governance inputs; it never touches providers or the
filesystem directly (that is delegated to the runtime/capability layer).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SpecInput:
    task_id: str
    objective: str
    scope: str
    deliverables: List[str]
    acceptance: List[str]
    dependencies: List[str]


class SpecWriter:
    """Renders a task specification document from structured input."""

    def render(self, spec: SpecInput) -> str:
        lines = [
            f"# {spec.task_id} — Specification",
            "",
            "## Objective",
            spec.objective,
            "",
            "## Scope",
            spec.scope,
            "",
            "## Deliverables",
        ]
        lines += [f"- {d}" for d in spec.deliverables]
        lines += ["", "## Acceptance Criteria"]
        lines += [f"- {a}" for a in spec.acceptance]
        lines += ["", "## Dependencies"]
        lines += [f"- {d}" for d in spec.dependencies] or ["- (none)"]
        return "\n".join(lines)

    def to_artifact(self, spec: SpecInput) -> Dict[str, str]:
        # Returns a record the orchestrator stores in the artifact map.
        return {f"{spec.task_id}/spec.md": self.render(spec)}
