"""TASK-196 — Continuous Evaluation (M25).

Capstone integrating the M25 evaluation components into a continuous loop
report. Based on Quality Dashboard T184 pattern.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.evaluation._common import EvaluationError, _hash
from aios.evaluation.evaluation_engine import DimensionScore, EvaluationEngine
from aios.evaluation.regression_detector import RegressionCheck, RegressionDetector
from aios.evaluation.evaluation_store import EvaluationStore


@dataclass(frozen=True)
class ContinuousReport:
    report_id: str
    components: int
    status: str


class ContinuousEvaluation:
    """Run the M25 evaluation components together on a subject."""

    def run(self, subject: str, scores: List[DimensionScore], current: float, baseline: float) -> ContinuousReport:
        if not subject:
            raise EvaluationError("subject must be non-empty")
        engine = EvaluationEngine()
        score_report = engine.score(scores)
        detector = RegressionDetector()
        reg_report = detector.detect(RegressionCheck(subject, current, baseline))
        store = EvaluationStore()
        components = 2
        # Overall status: worst of engine + regression.
        if score_report.status == "UNKNOWN" or reg_report.status == "UNKNOWN":
            status = "UNKNOWN"
        elif score_report.status == "INSUFFICIENT" or reg_report.status == "INSUFFICIENT":
            status = "INSUFFICIENT"
        else:
            status = "PASS"
        report_id = _hash(f"{subject}|{score_report.status}|{reg_report.status}|{components}")
        return ContinuousReport(report_id=report_id, components=components, status=status)
