"""Circuit Breaker state machine (TASK-055 §2).

CLOSED --(failure threshold)--> OPEN --(cooldown)--> HALF_OPEN
  HALF_OPEN --recovery success--> CLOSED
  HALF_OPEN --recovery failure--> OPEN
"""

from __future__ import annotations

import time

from aios.autonomous_recovery.contracts import CircuitState


class CircuitBreaker:
    def __init__(
        self,
        scope: str = "default",
        failure_threshold: int = 3,
        cooldown: float = 30.0,
        half_open_probe: int = 1,
    ) -> None:
        self.scope = scope
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
        self.half_open_probe = half_open_probe
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure: float = 0.0
        self.last_recovery: float = 0.0
        self._half_open_trials = 0

    def record_failure(self) -> None:
        self.last_failure = time.time()
        if self.state == CircuitState.OPEN:
            return
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def record_success(self) -> None:
        self.last_recovery = time.time()
        if self.state == CircuitState.HALF_OPEN:
            self._half_open_trials += 1
            if self._half_open_trials >= self.half_open_probe:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self._half_open_trials = 0
        else:
            self.failure_count = 0

    def allow_request(self) -> bool:
        """Whether a new request is permitted under the current state."""
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure >= self.cooldown:
                self.state = CircuitState.HALF_OPEN
                self._half_open_trials = 0
                return True
            return False
        # HALF_OPEN
        return True

    def to_dict(self) -> dict[str, object]:
        return {
            "scope": self.scope,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "cooldown": self.cooldown,
        }
