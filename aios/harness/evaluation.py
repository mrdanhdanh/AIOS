"""Evaluation harness — evaluator suite for output/trajectory assessment.

AC-032-01: Output correct + trajectory correct → PASS.
AC-032-02: Output wrong → FAIL.
AC-032-05: Missing evidence → INCONCLUSIVE.
AC-032-10: UNKNOWN/INCONCLUSIVE never auto-promoted to PASS.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class EvalVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    INCONCLUSIVE = "inconclusive"


class EvaluatorType(str, Enum):
    DETERMINISTIC = "deterministic"
    SEMANTIC = "semantic"
    LLM_JUDGE = "llm_judge"
    HUMAN = "human"
    COMPOSITE = "composite"


@dataclass
class Metric:
    """A single evaluation metric."""
    name: str
    value: float = 0.0
    threshold: float = 0.0
    unit: str = ""
    is_hard: bool = False  # Hard metric failure → overall FAIL

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "value": self.value, "threshold": self.threshold, "is_hard": self.is_hard}


@dataclass
class EvaluationCase:
    """A single evaluation case."""
    case_id: str = ""
    input_data: str = ""
    expected_output: str = ""
    actual_output: str = ""
    metrics: list[Metric] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"case_id": self.case_id, "metrics": [m.to_dict() for m in self.metrics]}


@dataclass
class EvaluationResult:
    """Result of evaluating a case."""
    case_id: str = ""
    verdict: EvalVerdict = EvalVerdict.INCONCLUSIVE
    metrics: list[Metric] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {"case_id": self.case_id, "verdict": self.verdict.value, "metrics": [m.to_dict() for m in self.metrics]}


class EvaluationSuite:
    """Suite of evaluation cases with evaluator logic."""

    def __init__(self) -> None:
        self._cases: list[EvaluationCase] = []
        self._results: list[EvaluationResult] = []

    def add_case(self, case: EvaluationCase) -> None:
        self._cases.append(case)

    def evaluate(self, evaluator_fn: Callable[[EvaluationCase], EvaluationResult] | None = None) -> list[EvaluationResult]:
        """Evaluate all cases."""
        results = []
        for case in self._cases:
            if evaluator_fn:
                result = evaluator_fn(case)
            else:
                # Default deterministic evaluator
                result = self._default_evaluate(case)
            self._results.append(result)
            results.append(result)
        return results

    def _default_evaluate(self, case: EvaluationCase) -> EvaluationResult:
        """Simple exact-match evaluator."""
        if not case.actual_output:
            return EvaluationResult(case_id=case.case_id, verdict=EvalVerdict.INCONCLUSIVE)
        passed = case.actual_output.strip() == case.expected_output.strip()
        return EvaluationResult(
            case_id=case.case_id,
            verdict=EvalVerdict.PASS if passed else EvalVerdict.FAIL,
            metrics=[Metric(name="exact_match", value=1.0 if passed else 0.0, threshold=1.0, is_hard=True)],
            provenance=[f"eval:{case.case_id}"],
        )

    def get_results(self) -> list[EvaluationResult]:
        return list(self._results)
