"""TASK-175 — Quality Gate + Gate States (M24).

A quality gate is a deterministic state machine over check results. Fail-closed:
any UNKNOWN check blocks promotion to PASS; UNKNOWN is never promoted to PASS.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.quality_gate._common import QualityGateError, _hash

GATE_STATES = ("OPEN", "EVALUATING", "PASS", "FAIL", "BLOCKED", "UNKNOWN")
PASS_STATE = "PASS"
FAIL_STATE = "FAIL"
BLOCKED_STATE = "BLOCKED"
UNKNOWN_STATE = "UNKNOWN"


@dataclass(frozen=True)
class GateCheck:
    check_id: str
    name: str
    status: str  # PASS | FAIL | UNKNOWN

    def __post_init__(self) -> None:
        if not self.check_id:
            raise QualityGateError("check_id must be non-empty")
        if not self.name:
            raise QualityGateError("name must be non-empty")
        if self.status not in ("PASS", "FAIL", "UNKNOWN"):
            raise QualityGateError(f"invalid check status: {self.status}")


@dataclass(frozen=True)
class GateReport:
    report_id: str
    gate_id: str
    state: str
    checks: tuple
    blocking: tuple


class QualityGate:
    """Deterministic quality gate state machine."""

    def __init__(self, gate_id: str) -> None:
        if not gate_id:
            raise QualityGateError("gate_id must be non-empty")
        self.gate_id = gate_id

    def evaluate(self, checks: List[GateCheck]) -> GateReport:
        if checks is None:
            raise QualityGateError("checks must be provided")
        for c in checks:
            if not isinstance(c, GateCheck):
                raise QualityGateError("each check must be a GateCheck")
        blocking: List[str] = []
        state = PASS_STATE
        for c in checks:
            if c.status == UNKNOWN_STATE:
                state = UNKNOWN_STATE
                blocking.append(c.check_id)
            elif c.status == FAIL_STATE:
                if state != UNKNOWN_STATE:
                    state = FAIL_STATE
                blocking.append(c.check_id)
        if state == PASS_STATE and not checks:
            # No checks -> cannot assert PASS; fail-closed to UNKNOWN.
            state = UNKNOWN_STATE
        report_id = _hash(f"{self.gate_id}|{','.join(sorted(c.check_id for c in checks))}|{state}")
        return GateReport(
            report_id=report_id,
            gate_id=self.gate_id,
            state=state,
            checks=tuple(checks),
            blocking=tuple(blocking),
        )
