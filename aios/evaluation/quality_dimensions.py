"""TASK-187 — Quality Dimensions (M25).

Defines quality dimensions (correctness, robustness, ...) with weight + threshold
and evaluates a measured value against the threshold.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.evaluation._common import EvaluationError, _hash

KNOWN_DIMENSIONS = ("correctness", "robustness", "maintainability", "security", "efficiency", "clarity")


@dataclass(frozen=True)
class QualityDimension:
    dimension_id: str
    name: str
    weight: float
    threshold: float

    def __post_init__(self) -> None:
        if not self.dimension_id:
            raise EvaluationError("dimension_id must be non-empty")
        if not self.name:
            raise EvaluationError("name must be non-empty")
        if not (0.0 <= self.weight <= 1.0):
            raise EvaluationError(f"weight out of range: {self.weight}")
        if not (0.0 <= self.threshold <= 1.0):
            raise EvaluationError(f"threshold out of range: {self.threshold}")


@dataclass(frozen=True)
class DimensionReport:
    report_id: str
    dimension_ref: str
    value: float
    status: str  # PASS | INSUFFICIENT


class QualityDimensionEvaluator:
    """Evaluate a measured value against a quality dimension threshold."""

    def evaluate(self, dim: QualityDimension, value: float) -> DimensionReport:
        if not isinstance(dim, QualityDimension):
            raise EvaluationError("dim must be a QualityDimension")
        if not (0.0 <= value <= 1.0):
            raise EvaluationError(f"value out of range: {value}")
        status = "PASS" if value >= dim.threshold else "INSUFFICIENT"
        report_id = _hash(f"{dim.dimension_id}|{value:.4f}|{status}")
        return DimensionReport(report_id=report_id, dimension_ref=dim.dimension_id, value=value, status=status)
