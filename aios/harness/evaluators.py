"""Evaluation harness — evaluator suite, trajectory assessment (T032)."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class EvalVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    INCONCLUSIVE = "inconclusive"


class TrajectoryVerdict(str, Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    INCONCLUSIVE = "inconclusive"


@dataclass
class EvaluationInput:
    """Input to an evaluator."""
    case_id: str
    input_data: str = ""
    expected_output: str = ""
    actual_output: str = ""
    trajectory: list[dict[str, Any]] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricResult:
    """Result of a single metric evaluation."""
    name: str
    value: float = 0.0
    threshold: float = 0.0
    passed: bool = True
    is_hard: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "value": self.value, "threshold": self.threshold, "passed": self.passed, "is_hard": self.is_hard}


@dataclass
class EvaluationReport:
    """Aggregated evaluation report for a case."""
    case_id: str
    verdict: EvalVerdict = EvalVerdict.INCONCLUSIVE
    metrics: list[MetricResult] = field(default_factory=list)
    trajectory_verdict: TrajectoryVerdict = TrajectoryVerdict.INCONCLUSIVE
    provenance: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id, "verdict": self.verdict.value,
            "metrics": [m.to_dict() for m in self.metrics],
            "trajectory_verdict": self.trajectory_verdict.value,
        }


class Evaluator(ABC):
    """Base evaluator. Subclasses implement evaluate()."""

    @abstractmethod
    def evaluate(self, inp: EvaluationInput) -> EvaluationReport:
        raise NotImplementedError


class DeterministicEvaluator(Evaluator):
    """Exact-match evaluator (AC-032-02)."""

    def evaluate(self, inp: EvaluationInput) -> EvaluationReport:
        match = inp.expected_output.strip() == inp.actual_output.strip()
        metric = MetricResult(name="exact_match", value=1.0 if match else 0.0, threshold=1.0, passed=match, is_hard=True)
        verdict = EvalVerdict.PASS if match else EvalVerdict.FAIL
        return EvaluationReport(case_id=inp.case_id, verdict=verdict, metrics=[metric], provenance=["deterministic"])


class SemanticEvaluator(Evaluator):
    """Semantic similarity evaluator with injected similarity function."""

    def __init__(self, similarity_fn: Callable[[str, str], float] | None = None, threshold: float = 0.8) -> None:
        self._sim = similarity_fn or (lambda a, b: 1.0 if a.strip() == b.strip() else 0.0)
        self.threshold = threshold

    def evaluate(self, inp: EvaluationInput) -> EvaluationReport:
        score = self._sim(inp.expected_output, inp.actual_output)
        passed = score >= self.threshold
        metric = MetricResult(name="semantic_similarity", value=score, threshold=self.threshold, passed=passed)
        verdict = EvalVerdict.PASS if passed else EvalVerdict.FAIL
        return EvaluationReport(case_id=inp.case_id, verdict=verdict, metrics=[metric], provenance=["semantic"])


class LLMEvaluator(Evaluator):
    """LLM-judge evaluator with injected judge function (offline-capable)."""

    def __init__(self, judge_fn: Callable[[EvaluationInput], float] | None = None) -> None:
        self._judge = judge_fn or (lambda inp: 1.0 if inp.expected_output == inp.actual_output else 0.0)

    def evaluate(self, inp: EvaluationInput) -> EvaluationReport:
        score = self._judge(inp)
        passed = score >= 0.5
        metric = MetricResult(name="llm_judge", value=score, threshold=0.5, passed=passed)
        verdict = EvalVerdict.PASS if passed else EvalVerdict.FAIL
        return EvaluationReport(case_id=inp.case_id, verdict=verdict, metrics=[metric], provenance=["llm_judge"])


class HumanEvaluator(Evaluator):
    """Human evaluator — requires explicit human decision (never auto-PASS)."""

    def __init__(self, decision_fn: Callable[[EvaluationInput], EvalVerdict] | None = None) -> None:
        self._decide = decision_fn or (lambda inp: EvalVerdict.INCONCLUSIVE)

    def evaluate(self, inp: EvaluationInput) -> EvaluationReport:
        verdict = self._decide(inp)
        return EvaluationReport(case_id=inp.case_id, verdict=verdict, metrics=[], provenance=["human"])


class CompositeEvaluator(Evaluator):
    """Combines multiple evaluators; fail-closed (any hard FAIL → FAIL)."""

    def __init__(self, evaluators: list[Evaluator] | None = None) -> None:
        self._evaluators = list(evaluators or [])

    def add(self, evaluator: Evaluator) -> None:
        self._evaluators.append(evaluator)

    def evaluate(self, inp: EvaluationInput) -> EvaluationReport:
        reports = [e.evaluate(inp) for e in self._evaluators]
        metrics: list[MetricResult] = []
        for r in reports:
            metrics.extend(r.metrics)
        if any(r.verdict == EvalVerdict.FAIL for r in reports):
            verdict = EvalVerdict.FAIL
        elif all(r.verdict == EvalVerdict.PASS for r in reports):
            verdict = EvalVerdict.PASS
        else:
            verdict = EvalVerdict.INCONCLUSIVE
        return EvaluationReport(case_id=inp.case_id, verdict=verdict, metrics=metrics, provenance=["composite"])


def evaluate_trajectory(trajectory: list[dict[str, Any]], expected: list[dict[str, Any]]) -> TrajectoryVerdict:
    """Assess whether the executed trajectory matches the expected one (AC-032-01)."""
    if not expected:
        return TrajectoryVerdict.INCONCLUSIVE
    if len(trajectory) != len(expected):
        return TrajectoryVerdict.INCORRECT
    for actual_step, expected_step in zip(trajectory, expected):
        if actual_step.get("action") != expected_step.get("action"):
            return TrajectoryVerdict.INCORRECT
    return TrajectoryVerdict.CORRECT
