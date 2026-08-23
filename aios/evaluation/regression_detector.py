"""TASK-190 — Regression Detector (M25).

Detects regression by comparing current value to baseline. Direction-aware via
higher_is_better. Based on Regression Verifier T159. Fail-closed: missing
baseline -> UNKNOWN (never promoted to PASS).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from aios.evaluation._common import EvaluationError, _hash


@dataclass(frozen=True)
class RegressionCheck:
    subject: str
    current: float
    baseline: Optional[float]
    higher_is_better: bool = True

    def __post_init__(self) -> None:
        if not self.subject:
            raise EvaluationError("subject must be non-empty")


@dataclass(frozen=True)
class RegressionReport:
    report_id: str
    subject: str
    status: str  # PASS | INSUFFICIENT | UNKNOWN
    delta: Optional[float]


class RegressionDetector:
    """Detect regression by comparing current to baseline."""

    def detect(self, check: RegressionCheck) -> RegressionReport:
        if not isinstance(check, RegressionCheck):
            raise EvaluationError("check must be a RegressionCheck")
        if check.baseline is None:
            return RegressionReport(report_id=_hash(f"{check.subject}|UNKNOWN"), subject=check.subject, status="UNKNOWN", delta=None)
        delta = check.current - check.baseline
        if check.higher_is_better:
            regressed = check.current < check.baseline
        else:
            regressed = check.current > check.baseline
        status = "INSUFFICIENT" if regressed else "PASS"
        report_id = _hash(f"{check.subject}|{status}|{delta:.4f}")
        return RegressionReport(report_id=report_id, subject=check.subject, status=status, delta=delta)
