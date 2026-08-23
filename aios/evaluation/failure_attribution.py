"""TASK-193 — Failure Attribution (M25).

Attributes a failure to a root-cause category. Fail-closed: unknown cause ->
UNKNOWN (never promoted to PASS); empty failure id raises EvaluationError.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.evaluation._common import EvaluationError, _hash

KNOWN_CAUSES = ("logic", "timeout", "dependency", "config", "data", "permission")


@dataclass(frozen=True)
class Failure:
    failure_id: str
    symptom: str
    cause: str  # one of KNOWN_CAUSES or "unknown"

    def __post_init__(self) -> None:
        if not self.failure_id:
            raise EvaluationError("failure_id must be non-empty")
        if not self.symptom:
            raise EvaluationError("symptom must be non-empty")


@dataclass(frozen=True)
class AttributionReport:
    report_id: str
    failure_ref: str
    cause: str
    status: str  # ATTRIBUTED | UNKNOWN


class FailureAttributor:
    """Attribute a failure to a root-cause category."""

    def attribute(self, failure: Failure) -> AttributionReport:
        if not isinstance(failure, Failure):
            raise EvaluationError("failure must be a Failure")
        if failure.cause not in KNOWN_CAUSES:
            status = "UNKNOWN"
        else:
            status = "ATTRIBUTED"
        report_id = _hash(f"{failure.failure_id}|{status}")
        return AttributionReport(report_id=report_id, failure_ref=failure.failure_id, cause=failure.cause, status=status)
