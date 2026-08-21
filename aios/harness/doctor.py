"""Harness doctor — diagnose and readiness check.

AC-034-01: Doctor distinguishes PASS/WARNING/ERROR/UNKNOWN.
AC-034-02: Readiness fail-closed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class DoctorVerdict(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"

    @property
    def is_healthy(self) -> bool:
        return self == DoctorVerdict.PASS


@dataclass
class DoctorCheck:
    """A single health check."""
    name: str
    verdict: DoctorVerdict = DoctorVerdict.UNKNOWN
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "verdict": self.verdict.value, "detail": self.detail}


@dataclass
class DiagnosisReport:
    """Overall diagnosis report."""
    overall: DoctorVerdict = DoctorVerdict.UNKNOWN
    checks: list[DoctorCheck] = field(default_factory=list)
    healthy_count: int = 0
    unhealthy_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall.value, "checks": [c.to_dict() for c in self.checks],
            "healthy_count": self.healthy_count, "unhealthy_count": self.unhealthy_count,
        }


class HarnessDoctor:
    """Diagnoses harness subsystem health."""

    def __init__(self) -> None:
        self._checks: list[tuple[str, Callable[[], DoctorCheck]]] = []

    def register(self, name: str, check_fn: Callable[[], DoctorCheck]) -> None:
        self._checks.append((name, check_fn))

    def diagnose(self) -> DiagnosisReport:
        checks = []
        for name, fn in self._checks:
            try:
                checks.append(fn())
            except Exception as e:
                checks.append(DoctorCheck(name=name, verdict=DoctorVerdict.ERROR, detail=str(e)))

        verdicts = [c.verdict for c in checks]
        if DoctorVerdict.ERROR in verdicts:
            overall = DoctorVerdict.ERROR
        elif DoctorVerdict.WARNING in verdicts:
            overall = DoctorVerdict.WARNING
        elif all(v == DoctorVerdict.PASS for v in verdicts):
            overall = DoctorVerdict.PASS
        else:
            overall = DoctorVerdict.UNKNOWN

        healthy = sum(1 for c in checks if c.verdict.is_healthy)
        return DiagnosisReport(overall=overall, checks=checks, healthy_count=healthy, unhealthy_count=len(checks) - healthy)


class ReadinessChecker:
    """Fail-closed readiness check."""

    def __init__(self) -> None:
        self._checks: list[Callable[[], bool]] = []

    def add_check(self, check: Callable[[], bool]) -> None:
        self._checks.append(check)

    def is_ready(self) -> bool:
        """Fail-closed: any check failure → not ready."""
        return all(fn() for fn in self._checks) if self._checks else False
