"""Advanced Stuck Detection (TASK-061).

A detection layer for the Autonomous Loop that identifies stuck / loop /
oscillation / plateau / resource-burn / deadlock states and triggers
fail-closed escalation. Detect ≠ Decide ≠ Recover: the detector emits a
signal, the Stuck Policy maps it to a candidate action, and the Governor
(T054) / Recovery (T055) decide whether the action is *allowed*.
"""

from aios.stuck_detection.contracts import (
    StuckKind,
    StuckPolicy,
    StuckSeverity,
    StuckSignal,
)
from aios.stuck_detection.detector import StuckDetector, StuckGate

__all__ = [
    "StuckKind",
    "StuckPolicy",
    "StuckSeverity",
    "StuckSignal",
    "StuckDetector",
    "StuckGate",
]
