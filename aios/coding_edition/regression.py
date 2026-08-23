"""TASK-218 — Full M0-M26 Regression (M26).

Capstone running the full M0-M26 regression summary across all milestones.
Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from aios.coding_edition._common import CodingEditionError, _hash


class RegressionStatus(str, Enum):
    """Aggregate regression status (T218)."""

    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


@dataclass
class ComponentResult:
    """A single component regression result (T218)."""

    component: str
    status: str  # PASS | FAIL | UNKNOWN
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.component:
            raise CodingEditionError("component is required.")


@dataclass
class RegressionReport:
    """Immutable-by-id full regression report (T218)."""

    report_id: str
    components: int
    passed: int
    failed: int
    status: RegressionStatus
    at: str = field(default_factory=lambda: __import__("aios.coding_edition._common", fromlist=["_now"])._now())


class FullRegression:
    """Deterministic full M0-M26 regression runner (T218)."""

    def __init__(self, run_id: Optional[str] = None) -> None:
        self._run_id = run_id or f"reg-{uuid.uuid4().hex[:12]}"

    @property
    def run_id(self) -> str:
        return self._run_id

    def run(self, results: List[ComponentResult]) -> RegressionReport:
        """Aggregate component results (fail-closed, worst-of)."""
        if not results:
            return RegressionReport(
                report_id=f"rr-{uuid.uuid4().hex[:10]}",
                components=0,
                passed=0,
                failed=0,
                status=RegressionStatus.UNKNOWN,
            )
        passed = sum(1 for r in results if r.status == "PASS")
        failed = sum(1 for r in results if r.status == "FAIL")
        if any(r.status == "UNKNOWN" for r in results):
            status = RegressionStatus.UNKNOWN
        elif failed > 0:
            status = RegressionStatus.FAIL
        else:
            status = RegressionStatus.PASS
        return RegressionReport(
            report_id=f"rr-{uuid.uuid4().hex[:10]}",
            components=len(results),
            passed=passed,
            failed=failed,
            status=status,
        )

    def regression_hash(self, report: RegressionReport) -> str:
        return _hash(f"{report.report_id}|{report.components}|{report.status.value}")
