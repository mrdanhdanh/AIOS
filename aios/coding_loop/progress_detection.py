"""Progress + Regression Detection (TASK-150, M21).

Measures loop progress and detects regression against a baseline (Benchmark/
Regression T033) + Autonomous Recovery T055. Built on Repair Planner T149 +
Evidence T001. TASK-150 is a *detector*, not a new verifier.

Layering: ``coding_loop`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

from aios.coding_loop._common import CodingLoopError, _hash, _now
from aios.coding_loop.repair import RepairPlan


@dataclass
class ProgressReport:
    """Immutable-by-id progress/regression report (T150)."""

    report_id: str
    loop_ref: str
    plan_ref: str
    progress_metric: float
    regression_flag: bool
    evidence_ref: str
    authority: str = "aios"
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.report_id:
            raise CodingLoopError("report_id required (T001 Rule 1, immutable).")
        if not self.evidence_ref:
            raise CodingLoopError("ProgressReport requires evidence_ref (T001 Rule 5).")


class ProgressRegressionDetector:
    """Deterministic progress + regression detector (T150)."""

    def __init__(self, baseline: float = 0.0) -> None:
        self._baseline = baseline
        self._reports: Dict[str, ProgressReport] = {}

    def detect(
        self,
        loop_ref: str,
        plan_ref: str,
        progress_metric: float,
        baseline: Optional[float] = None,
        evidence_ref: Optional[str] = None,
        report_id: Optional[str] = None,
    ) -> ProgressReport:
        # Fail-closed: provenance + loop linkage required.
        if not loop_ref or not plan_ref:
            raise CodingLoopError("loop_ref and plan_ref required (T145/T149).")
        if evidence_ref is None:
            raise CodingLoopError("ProgressReport requires evidence_ref (T001 Rule 5).")
        bl = baseline if baseline is not None else self._baseline
        # Deterministic: regression when progress falls below baseline (T033).
        regression_flag = progress_metric < bl
        ev = evidence_ref
        rid = report_id or f"prog-{uuid.uuid4().hex[:12]}"
        if rid in self._reports:
            raise CodingLoopError(f"Duplicate report_id '{rid}' (T001 Rule 1).")
        rep = ProgressReport(
            report_id=rid,
            loop_ref=loop_ref,
            plan_ref=plan_ref,
            progress_metric=progress_metric,
            regression_flag=regression_flag,
            evidence_ref=ev,
        )
        self._reports[rid] = rep
        return rep

    def get(self, report_id: str) -> ProgressReport:
        if report_id not in self._reports:
            raise CodingLoopError(f"Unknown report '{report_id}'.")
        return self._reports[report_id]

    def provenance(self, report_id: str) -> dict:
        rep = self.get(report_id)
        payload = (
            f"{rep.report_id}|{rep.loop_ref}|{rep.plan_ref}|"
            f"{rep.progress_metric}|{rep.regression_flag}|{rep.evidence_ref}"
        )
        return {
            "report_id": rep.report_id,
            "loop_ref": rep.loop_ref,
            "plan_ref": rep.plan_ref,
            "progress_metric": rep.progress_metric,
            "regression_flag": rep.regression_flag,
            "evidence_ref": rep.evidence_ref,
            "authority": rep.authority,
            "content_hash": _hash(payload),
        }
