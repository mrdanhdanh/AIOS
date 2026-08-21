"""Dry-run engine — simulates upgrade without side effects.

AC-020-05: Dry-run creates no side effects.
AC-020-06: Dry-run deterministic.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from aios.upgrade.manifest import UpgradeManifest


@dataclass
class DryRunStep:
    """Simulated step result."""
    step_id: str
    would_execute: bool = True
    preconditions_met: bool = True
    postconditions_would_pass: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "would_execute": self.would_execute,
            "preconditions_met": self.preconditions_met,
            "postconditions_would_pass": self.postconditions_would_pass,
        }


@dataclass
class DryRunResult:
    """Result of a dry-run simulation."""

    upgrade_id: str
    ready: bool = True
    steps: list[DryRunStep] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "upgrade_id": self.upgrade_id,
            "ready": self.ready,
            "steps": [s.to_dict() for s in self.steps],
            "issues": self.issues,
            "duration_ms": self.duration_ms,
        }


class DryRunEngine:
    """Simulates an upgrade without creating side effects.

    AC-020-05: No side effects.
    AC-020-06: Deterministic — same input produces same plan.
    """

    def simulate(
        self,
        manifest: UpgradeManifest,
        current_state: dict[str, Any] | None = None,
    ) -> DryRunResult:
        """Simulate the upgrade and return the plan.

        No mutations to state.
        """
        start_time = time.time()
        state = dict(current_state) if current_state else {}
        steps: list[DryRunStep] = []
        issues: list[str] = []

        for step in manifest.steps:
            preconditions_met = all(pre in state for pre in step.preconditions)
            dry_step = DryRunStep(
                step_id=step.step_id,
                would_execute=preconditions_met,
                preconditions_met=preconditions_met,
                postconditions_would_pass=preconditions_met,
            )
            steps.append(dry_step)

            if not preconditions_met:
                missing = [p for p in step.preconditions if p not in state]
                issues.append(f"Step {step.step_id}: missing preconditions {missing}")

        ready = len(issues) == 0

        return DryRunResult(
            upgrade_id=manifest.upgrade_id,
            ready=ready,
            steps=steps,
            issues=issues,
            duration_ms=(time.time() - start_time) * 1000,
        )
