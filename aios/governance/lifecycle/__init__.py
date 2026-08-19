"""Task State Machine (Rule 6).

A task moves through an ordered lifecycle. Every transition into a state that
requires artifacts is only permitted when those mandatory artifacts are present.
If any mandatory artifact is missing when attempting to close (reach DONE), the
close is rejected.
"""

from .statemachine import (
    LIFECYCLE_ORDER,
    STATE_ARTIFACTS,
    LifecycleError,
    TaskLifecycle,
)

__all__ = [
    "LIFECYCLE_ORDER",
    "STATE_ARTIFACTS",
    "LifecycleError",
    "TaskLifecycle",
]
