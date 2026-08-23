"""TASK-189 — Baseline Manager (M25).

Stores and retrieves baselines for subjects. Fail-closed: missing baseline ->
UNKNOWN (never promoted to PASS); empty subject raises EvaluationError.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from aios.evaluation._common import EvaluationError, _hash


@dataclass(frozen=True)
class Baseline:
    subject: str
    value: float
    metric: str = "score"

    def __post_init__(self) -> None:
        if not self.subject:
            raise EvaluationError("subject must be non-empty")
        if not self.metric:
            raise EvaluationError("metric must be non-empty")


@dataclass(frozen=True)
class BaselineReport:
    report_id: str
    subject: str
    value: Optional[float]
    status: str  # PASS | UNKNOWN


class BaselineManager:
    """Manage baselines for subjects deterministically."""

    def __init__(self) -> None:
        self._baselines: Dict[str, Baseline] = {}

    def set_baseline(self, baseline: Baseline) -> BaselineReport:
        if not isinstance(baseline, Baseline):
            raise EvaluationError("baseline must be a Baseline")
        self._baselines[baseline.subject] = baseline
        report_id = _hash(f"{baseline.subject}|{baseline.value:.4f}|set")
        return BaselineReport(report_id=report_id, subject=baseline.subject, value=baseline.value, status="PASS")

    def get_baseline(self, subject: str) -> BaselineReport:
        if not subject:
            raise EvaluationError("subject must be non-empty")
        b = self._baselines.get(subject)
        status = "PASS" if b else "UNKNOWN"
        report_id = _hash(f"{subject}|{status}")
        return BaselineReport(report_id=report_id, subject=subject, value=b.value if b else None, status=status)
