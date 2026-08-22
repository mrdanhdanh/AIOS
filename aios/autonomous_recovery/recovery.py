"""Recovery Controller + Failure Classification (TASK-055).

Fail-closed: a recovery attempt whose post-condition cannot be *verified* is
never treated as recovered. The Autonomy Governor (T054) remains the authority
for approval; this controller only orchestrates recovery primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from aios.autonomous_recovery.circuit import CircuitBreaker
from aios.autonomous_recovery.contracts import (
    FailureClass,
    RecoveryAttempt,
    RecoveryStrategy,
    RecoveryVerdict,
)


class FailureClassifier:
    """Deterministic classification of a failure (spec §1)."""

    # Order matters: more specific/actionable classes are checked first so
    # that shared keywords (e.g. "unavailable") resolve to the right class.
    _KEYWORDS = {
        FailureClass.DEPENDENCY: ("capability", "tool", "model", "provider", "dependency"),
        FailureClass.POLICY: ("policy", "permission", "denied", "forbidden"),
        FailureClass.STATE: ("corrupt", "inconsistent", "state"),
        FailureClass.RESOURCE: ("resource", "memory", "cpu", "quota", "exhausted"),
        FailureClass.LOGICAL: ("expected", "condition", "assertion", "logic"),
        FailureClass.TRANSIENT: ("timeout", "temporary", "unavailable", "retryable", "transient"),
    }

    def classify(self, failure: str) -> FailureClass:
        f = (failure or "").lower()
        for cls, kws in self._KEYWORDS.items():
            if any(k in f for k in kws):
                return cls
        return FailureClass.UNKNOWN


@dataclass
class RecoveryPolicy:
    retry_max_attempts: int = 3
    fallback_allowed: bool = True
    rollback_allowed: bool = True
    human_approval_after: int = 2
    safe_stop_enabled: bool = True


class RecoveryController:
    def __init__(
        self,
        policy: RecoveryPolicy | None = None,
        breaker: CircuitBreaker | None = None,
        governor_decision: Callable[[RecoveryStrategy, dict], bool] | None = None,
    ) -> None:
        self._classifier = FailureClassifier()
        self._policy = policy or RecoveryPolicy()
        self._breaker = breaker or CircuitBreaker()
        # governor_decision(strategy, context) -> True if allowed
        self._governor = governor_decision

    def decide_strategy(self, failure_class: FailureClass, attempt_count: int) -> RecoveryStrategy:
        if failure_class == FailureClass.TRANSIENT:
            if attempt_count < self._policy.retry_max_attempts:
                return RecoveryStrategy.RETRY
            return RecoveryStrategy.FALLBACK if self._policy.fallback_allowed else RecoveryStrategy.SAFE_STOP
        if failure_class == FailureClass.RESOURCE:
            return RecoveryStrategy.FALLBACK if self._policy.fallback_allowed else RecoveryStrategy.SAFE_STOP
        if failure_class == FailureClass.DEPENDENCY:
            return RecoveryStrategy.FALLBACK if self._policy.fallback_allowed else RecoveryStrategy.ESCALATE
        if failure_class == FailureClass.POLICY:
            return RecoveryStrategy.ESCALATE
        if failure_class == FailureClass.STATE:
            return RecoveryStrategy.ROLLBACK if self._policy.rollback_allowed else RecoveryStrategy.SAFE_STOP
        if failure_class == FailureClass.LOGICAL:
            return RecoveryStrategy.RETRY if attempt_count < self._policy.retry_max_attempts else RecoveryStrategy.ESCALATE
        # UNKNOWN -> fail-closed
        return RecoveryStrategy.SAFE_STOP

    def attempt(
        self,
        execution_id: str,
        failure: str,
        pre_state: dict[str, Any],
        recovery_action: Callable[[RecoveryStrategy], dict[str, Any]],
        verify: Callable[[dict[str, Any], dict[str, Any]], bool],
        evidence: list[str] | None = None,
    ) -> RecoveryAttempt:
        classification = self._classifier.classify(failure)
        attempt = RecoveryAttempt(
            execution_id=execution_id,
            failure=failure,
            classification=classification,
            pre_state=dict(pre_state),
            evidence=list(evidence or []),
        )

        # Circuit breaker gate (no infinite retry).
        if not self._breaker.allow_request():
            attempt.strategy = RecoveryStrategy.SAFE_STOP
            attempt.policy_decision = "circuit_open"
            attempt.outcome = RecoveryVerdict.NOT_RECOVERED
            attempt.verification = "blocked:circuit_open"
            return attempt

        strategy = self.decide_strategy(classification, self._breaker.failure_count)
        attempt.strategy = strategy
        attempt.policy_decision = "policy"

        # Governor authority for approval-required strategies.
        if strategy in (RecoveryStrategy.ESCALATE, RecoveryStrategy.ROLLBACK, RecoveryStrategy.FALLBACK):
            if self._governor is not None and not self._governor(strategy, {"execution_id": execution_id}):
                attempt.policy_decision = "governor_denied"
                attempt.outcome = RecoveryVerdict.NOT_RECOVERED
                attempt.verification = "blocked:governor"
                return attempt

        if strategy == RecoveryStrategy.SAFE_STOP:
            attempt.outcome = RecoveryVerdict.NOT_RECOVERED
            attempt.verification = "safe_stop"
            return attempt

        # Execute recovery action.
        try:
            post_state = recovery_action(strategy)
        except Exception as exc:  # fail-closed on action error
            self._breaker.record_failure()
            attempt.outcome = RecoveryVerdict.NOT_RECOVERED
            attempt.verification = f"action_error:{exc}"
            return attempt

        attempt.post_state = dict(post_state)
        # Verification — fail-closed: unverified != recovered.
        verified = False
        try:
            verified = bool(verify(post_state, pre_state))
        except Exception:
            verified = False
        attempt.verification = "verified" if verified else "unverified"

        if verified:
            self._breaker.record_success()
            attempt.outcome = RecoveryVerdict.RECOVERED
        else:
            self._breaker.record_failure()
            attempt.outcome = RecoveryVerdict.NOT_RECOVERED
        return attempt

    @property
    def breaker(self) -> CircuitBreaker:
        return self._breaker
