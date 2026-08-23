"""TASK-186 — Evaluation Engine (M25).

Aggregates per-dimension scores into an overall evaluation. Fail-closed:
missing scores -> UNKNOWN; any dimension below threshold -> INSUFFICIENT;
UNKNOWN is never promoted to PASS.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from aios.evaluation._common import EvaluationError, _hash


@dataclass(frozen=True)
class DimensionScore:
    dimension: str
    score: float  # 0..1
    threshold: float  # 0..1


@dataclass(frozen=True)
class ScoreReport:
    report_id: str
    overall: float
    status: str  # PASS | INSUFFICIENT | UNKNOWN
    below: Tuple[str, ...]


class EvaluationEngine:
    """Aggregate dimension scores into an overall evaluation."""

    def score(self, scores: List[DimensionScore]) -> ScoreReport:
        if scores is None:
            raise EvaluationError("scores must be provided")
        for s in scores:
            if not isinstance(s, DimensionScore):
                raise EvaluationError("each score must be a DimensionScore")
            if not (0.0 <= s.score <= 1.0):
                raise EvaluationError(f"score out of range: {s.score}")
        if not scores:
            return ScoreReport(report_id=_hash("EMPTY|UNKNOWN"), overall=0.0, status="UNKNOWN", below=())
        below = tuple(s.dimension for s in scores if s.score < s.threshold)
        overall = sum(s.score for s in scores) / len(scores)
        if below:
            status = "INSUFFICIENT"
        else:
            status = "PASS"
        report_id = _hash(f"{overall:.4f}|{status}|{','.join(sorted(below))}")
        return ScoreReport(report_id=report_id, overall=overall, status=status, below=below)
