"""TASK-180 — Release Gate + Decision Explainability (M24).

Decides release with explainable, fail-closed reasoning. Any unmet blocking
criterion -> NO_RELEASE with an explanation; no criteria -> BLOCKED.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.quality_gate._common import QualityGateError, _hash

RELEASE_DECISIONS = ("RELEASE", "NO_RELEASE", "BLOCKED")


@dataclass(frozen=True)
class ReleaseCriterion:
    criterion_id: str
    name: str
    met: bool
    blocking: bool = True

    def __post_init__(self) -> None:
        if not self.criterion_id:
            raise QualityGateError("criterion_id must be non-empty")
        if not self.name:
            raise QualityGateError("name must be non-empty")


@dataclass(frozen=True)
class ReleaseReport:
    report_id: str
    decision: str
    explanation: str
    unmet: tuple


class ReleaseGate:
    """Decide release with explainable, fail-closed reasoning."""

    def evaluate(self, criteria: List[ReleaseCriterion]) -> ReleaseReport:
        if criteria is None:
            raise QualityGateError("criteria must be provided")
        for c in criteria:
            if not isinstance(c, ReleaseCriterion):
                raise QualityGateError("each criterion must be a ReleaseCriterion")
        unmet = [c for c in criteria if not c.met and c.blocking]
        if not criteria:
            decision = "BLOCKED"
            explanation = "no criteria evaluated"
        elif unmet:
            decision = "NO_RELEASE"
            explanation = "blocking criteria unmet: " + ", ".join(c.name for c in unmet)
        else:
            decision = "RELEASE"
            explanation = "all blocking criteria met"
        report_id = _hash(f"{decision}|{','.join(sorted(c.criterion_id for c in criteria))}")
        return ReleaseReport(report_id=report_id, decision=decision, explanation=explanation, unmet=tuple(unmet))
