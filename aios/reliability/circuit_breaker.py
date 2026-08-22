"""Circuit breaker (TASK-069).

Opens (stops sending traffic to a failing dependency) when the failure rate
exceeds a threshold; probes recovery in HALF_OPEN before closing again.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpen(Exception):
    """Raised when a call is attempted while the breaker is OPEN."""


@dataclass
class _Config:
    failure_threshold: int = 3
    half_open_after: int = 1


class CircuitBreaker:
    """A simple deterministic circuit breaker."""

    def __init__(self, failure_threshold: int = 3, half_open_after: int = 1) -> None:
        self._failure_threshold = failure_threshold
        self._half_open_after = half_open_after
        self._failures = 0
        self._state = CircuitState.CLOSED

    @property
    def state(self) -> CircuitState:
        return self._state

    def allow(self) -> bool:
        return self._state != CircuitState.OPEN

    def half_open(self) -> None:
        if self._state == CircuitState.OPEN:
            self._state = CircuitState.HALF_OPEN

    def call(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if self._state == CircuitState.OPEN:
            raise CircuitOpen("circuit breaker OPEN")
        try:
            result = fn(*args, **kwargs)
        except Exception:
            self._on_failure()
            raise
        self._on_success()
        return result

    def _on_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            self._failures = 0

    def _on_failure(self) -> None:
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self._state = CircuitState.OPEN
        elif self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
