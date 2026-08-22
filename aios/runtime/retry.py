"""Bounded retry with backoff and escalation (TASK-065 hardening).

Provides :class:`BoundedRetry` — a deterministic, bounded retry primitive with
exponential/fixed/none backoff. Exceeding ``max_attempts`` triggers an
``escalate`` callback (no infinite loop). Every attempt failure emits an
observability trace. Deterministic: same error + same policy -> same behaviour
(no randomness, capped deterministic delays).

Layering: runtime layer — relative import of :mod:`.observability` only.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .observability import ObservabilityHook

__all__ = ["RetryBudgetExceeded", "BoundedRetry", "RetryConfig"]


class RetryBudgetExceeded(Exception):
    """Raised when retry attempts are exhausted (escalation trigger)."""


@dataclass
class RetryConfig:
    """Bounded retry configuration (deterministic)."""

    max_attempts: int = 3
    backoff: str = "exponential"  # exponential | fixed | none
    base_delay: float = 0.01
    max_delay: float = 0.1
    retryable_errors: Optional[list[str]] = None


class BoundedRetry:
    """Deterministic bounded retry with escalation on exhaustion."""

    def __init__(
        self,
        config: Optional[RetryConfig] = None,
        *,
        escalate: Optional[Callable[[str, int, Optional[BaseException]], None]] = None,
        observability: Optional[ObservabilityHook] = None,
        component: str = "retry",
    ) -> None:
        self._config = config or RetryConfig()
        self._escalate = escalate
        self._obs = observability or ObservabilityHook(component=component)
        self._component = component

    # ------------------------------------------------------------------ #
    def _is_retryable(self, exc: BaseException) -> bool:
        if self._config.retryable_errors is None:
            return True
        name = type(exc).__name__.lower()
        msg = str(exc).lower()
        return any(
            token in name or token in msg for token in self._config.retryable_errors
        )

    def _backoff_delay(self, attempt: int) -> float:
        if self._config.backoff == "none":
            return 0.0
        if self._config.backoff == "fixed":
            return self._config.base_delay
        # exponential: base * 2^(attempt-1), capped deterministically
        delay = self._config.base_delay * (2 ** (attempt - 1))
        return min(delay, self._config.max_delay)

    def run(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Run *fn* with bounded retry. No infinite loop.

        On exhaustion, calls ``escalate`` (if set) and raises
        :class:`RetryBudgetExceeded`. Every failure emits an observability trace.
        """
        attempts = 0
        last_exc: Optional[BaseException] = None
        max_attempts = self._config.max_attempts
        while attempts < max_attempts:
            attempts += 1
            try:
                return fn(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - surfaced deterministically
                last_exc = exc
                self._obs.trace_failure(
                    exc,
                    component=self._component,
                    evidence_ref=f"attempt-{attempts}",
                    attempt=attempts,
                    max_attempts=max_attempts,
                    retryable=self._is_retryable(exc),
                )
                if not self._is_retryable(exc):
                    break
                if attempts >= max_attempts:
                    break
                delay = self._backoff_delay(attempts)
                if delay > 0:
                    time.sleep(delay)
        # Exhausted -> escalate then raise (no infinite loop).
        if self._escalate is not None:
            try:
                self._escalate(
                    f"retry budget exceeded after {attempts} attempts",
                    attempts,
                    last_exc,
                )
            except Exception:  # pragma: no cover - escalation must not mask
                pass
        raise RetryBudgetExceeded(
            f"Retry budget exceeded after {attempts} attempts: {last_exc}"
        ) from last_exc
