"""Autonomous Recovery (TASK-055).

Detects execution/goal failure or degradation, triggers controlled recovery,
and fails-closed when recovery is not safe. The Governor (T054) remains the
authority; this module does not create a second policy engine or control
plane.
"""

from aios.autonomous_recovery.contracts import (
    CircuitState,
    FailureClass,
    RecoveryAttempt,
    RecoveryStrategy,
    RecoveryVerdict,
)
from aios.autonomous_recovery.circuit import CircuitBreaker
from aios.autonomous_recovery.recovery import FailureClassifier, RecoveryController

__all__ = [
    "CircuitState",
    "FailureClass",
    "RecoveryAttempt",
    "RecoveryStrategy",
    "RecoveryVerdict",
    "CircuitBreaker",
    "FailureClassifier",
    "RecoveryController",
]
