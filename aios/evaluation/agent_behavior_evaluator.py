"""TASK-191 — Agent Behavior Evaluator (M25).

Evaluates observed agent behavior against expected behavior. Based on Behavioral
Verifier T157. Fail-closed: mismatch -> INSUFFICIENT; UNKNOWN never promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aios.evaluation._common import EvaluationError, _hash


@dataclass(frozen=True)
class BehaviorSpec:
    spec_id: str
    expected: Any
    actual: Any

    def __post_init__(self) -> None:
        if not self.spec_id:
            raise EvaluationError("spec_id must be non-empty")


@dataclass(frozen=True)
class BehaviorEvalReport:
    report_id: str
    spec_ref: str
    status: str  # PASS | INSUFFICIENT


class AgentBehaviorEvaluator:
    """Evaluate observed behavior against expected behavior."""

    def evaluate(self, spec: BehaviorSpec) -> BehaviorEvalReport:
        if not isinstance(spec, BehaviorSpec):
            raise EvaluationError("spec must be a BehaviorSpec")
        match = spec.expected == spec.actual
        status = "PASS" if match else "INSUFFICIENT"
        report_id = _hash(f"{spec.spec_id}|{status}")
        return BehaviorEvalReport(report_id=report_id, spec_ref=spec.spec_id, status=status)
