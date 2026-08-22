"""Harness Coverage + Readiness (TASK-090, M13).

Coverage map + readiness gate + gap report for the harness surface. Built on
Harness (T030/T032/T089) and Certification (T073).

Layering: ``unknown`` (infra) layer — stdlib + ``aios.harness`` +
``aios.certification`` + ``aios.behavioral`` only. No provider/filesystem/agent
imports.
"""

from aios.harness_coverage.coverage import (
    CoverageChecker,
    CoverageMap,
    CoverageReport,
    Readiness,
)

__all__ = [
    "Readiness",
    "CoverageReport",
    "CoverageMap",
    "CoverageChecker",
]
