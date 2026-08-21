"""Failure Recovery — classification + bounded retry + fallback (TASK-012).

Orchestration-level recovery, not duplicate of Runtime retry engine.
Deterministic, bounded, policy-gated fallback.

Layering: orchestrator — may import runtime.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

__all__ = [
    "FailureCategory",
    "RecoveryStrategy",
    "FailureClassification",
    "RetryPolicy",
    "RecoveryRecord",
    "FailureClassifier",
    "FailureRecovery",
    "FailureRecoveryError",
]


class FailureRecoveryError(Exception):
    pass


class FailureCategory(str, Enum):
    TRANSIENT = "TRANSIENT"
    RESOURCE = "RESOURCE"
    POLICY = "POLICY"
    VALIDATION = "VALIDATION"
    LOGICAL = "LOGICAL"
    FATAL = "FATAL"


class RecoveryStrategy(str, Enum):
    RETRY_SAME = "RETRY_SAME"
    RETRY_WITH_MODIFIED_INPUT = "RETRY_WITH_MODIFIED_INPUT"
    FALLBACK_AGENT = "FALLBACK_AGENT"
    FALLBACK_WORKFLOW = "FALLBACK_WORKFLOW"
    PAUSE_FOR_HUMAN = "PAUSE_FOR_HUMAN"
    FAIL = "FAIL"


@dataclass
class FailureClassification:
    category: FailureCategory
    reason: str
    retryable: bool
    suggested_strategy: RecoveryStrategy


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    backoff_strategy: str = "exponential"  # exponential | fixed
    initial_ms: int = 500
    max_ms: int = 5000

    def validate(self) -> None:
        if not isinstance(self.max_attempts, int) or self.max_attempts < 1:
            raise FailureRecoveryError("max_attempts must be >= 1")
        if self.backoff_strategy not in ("exponential", "fixed"):
            raise FailureRecoveryError("backoff_strategy must be exponential or fixed")
        if not isinstance(self.initial_ms, int) or self.initial_ms < 0:
            raise FailureRecoveryError("initial_ms must be >= 0")
        if not isinstance(self.max_ms, int) or self.max_ms < 0:
            raise FailureRecoveryError("max_ms must be >= 0")

    def backoff_ms(self, attempt: int) -> int:
        """Compute backoff for attempt (1-indexed)."""
        if self.backoff_strategy == "fixed":
            return min(self.initial_ms, self.max_ms)
        # exponential: initial * 2^(attempt-1)
        val = self.initial_ms * (2 ** (attempt - 1))
        return min(val, self.max_ms)


@dataclass
class RecoveryRecord:
    task_id: str
    attempt: int
    category: FailureCategory
    strategy: RecoveryStrategy
    error: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "attempt": self.attempt,
            "category": self.category.value,
            "strategy": self.strategy.value,
            "error": self.error,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }


class FailureClassifier:
    """Classify failures into categories."""

    # Keyword → category mapping (deterministic)
    _KEYWORDS: Dict[str, FailureCategory] = {
        "timeout": FailureCategory.TRANSIENT,
        "temporary": FailureCategory.TRANSIENT,
        "connection reset": FailureCategory.TRANSIENT,
        "unavailable": FailureCategory.TRANSIENT,
        "cpu": FailureCategory.RESOURCE,
        "memory": FailureCategory.RESOURCE,
        "resource": FailureCategory.RESOURCE,
        "permission denied": FailureCategory.POLICY,
        "policy denied": FailureCategory.POLICY,
        "denied": FailureCategory.POLICY,
        "invalid input": FailureCategory.VALIDATION,
        "invalid plan": FailureCategory.VALIDATION,
        "validation": FailureCategory.VALIDATION,
        "corrupted": FailureCategory.FATAL,
        "invalid contract": FailureCategory.FATAL,
    }

    def classify(self, error: str) -> FailureClassification:
        err_l = (error or "").lower()
        for keyword, category in self._KEYWORDS.items():
            if keyword in err_l:
                retryable = category in (FailureCategory.TRANSIENT, FailureCategory.RESOURCE)
                if category == FailureCategory.TRANSIENT:
                    strategy = RecoveryStrategy.RETRY_SAME
                elif category == FailureCategory.RESOURCE:
                    strategy = RecoveryStrategy.RETRY_SAME
                elif category == FailureCategory.POLICY:
                    strategy = RecoveryStrategy.FAIL
                elif category == FailureCategory.VALIDATION:
                    strategy = RecoveryStrategy.FAIL
                elif category == FailureCategory.FATAL:
                    strategy = RecoveryStrategy.PAUSE_FOR_HUMAN
                else:
                    strategy = RecoveryStrategy.FAIL
                return FailureClassification(category=category, reason=f"matched keyword {keyword!r}", retryable=retryable, suggested_strategy=strategy)
        # Default: LOGICAL
        return FailureClassification(category=FailureCategory.LOGICAL, reason="no keyword matched, default LOGICAL", retryable=False, suggested_strategy=RecoveryStrategy.FAIL)


class FailureRecovery:
    """Orchestration-level recovery with bounded retry and policy-gated fallback."""

    def __init__(
        self,
        retry_policy: Optional[RetryPolicy] = None,
        classifier: Optional[FailureClassifier] = None,
        policy_checker: Optional[Callable[[str, RecoveryStrategy], bool]] = None,
    ) -> None:
        self.retry_policy = retry_policy or RetryPolicy()
        self.retry_policy.validate()
        self.classifier = classifier or FailureClassifier()
        self.policy_checker = policy_checker  # (task_id, strategy) -> bool (allow fallback?)
        self._lock = threading.RLock()
        self._history: Dict[str, List[RecoveryRecord]] = {}
        self._attempts: Dict[str, int] = {}

    def record_failure(self, task_id: str, error: str) -> FailureClassification:
        return self.classifier.classify(error)

    def should_retry(self, task_id: str, error: str) -> bool:
        classification = self.classifier.classify(error)
        if not classification.retryable:
            return False
        attempts = self._attempts.get(task_id, 0)
        return attempts < self.retry_policy.max_attempts

    def next_strategy(self, task_id: str, error: str) -> RecoveryStrategy:
        classification = self.classifier.classify(error)
        attempts = self._attempts.get(task_id, 0)
        if classification.retryable and attempts < self.retry_policy.max_attempts:
            return RecoveryStrategy.RETRY_SAME
        # Check fallback policy — only if policy_checker explicitly allows
        if classification.category in (FailureCategory.LOGICAL, FailureCategory.TRANSIENT, FailureCategory.RESOURCE):
            for strat in (RecoveryStrategy.FALLBACK_AGENT, RecoveryStrategy.FALLBACK_WORKFLOW):
                if self.policy_checker is not None and self.policy_checker(task_id, strat):
                    return strat
        if classification.category == FailureCategory.FATAL:
            return RecoveryStrategy.PAUSE_FOR_HUMAN
        return RecoveryStrategy.FAIL

    def handle_failure(self, task_id: str, error: str) -> RecoveryRecord:
        """Record failure, increment attempts, return recovery record with strategy."""
        classification = self.classifier.classify(error)
        with self._lock:
            attempts = self._attempts.get(task_id, 0) + 1
            self._attempts[task_id] = attempts
            # Determine strategy
            if classification.retryable and attempts <= self.retry_policy.max_attempts:
                strategy = RecoveryStrategy.RETRY_SAME
            else:
                strategy = self.next_strategy(task_id, error)
                # If next_strategy still suggests RETRY_SAME but attempts exhausted, force FAIL
                if strategy == RecoveryStrategy.RETRY_SAME and attempts > self.retry_policy.max_attempts:
                    strategy = RecoveryStrategy.FAIL
            record = RecoveryRecord(
                task_id=task_id,
                attempt=attempts,
                category=classification.category,
                strategy=strategy,
                error=error,
                metadata={"retryable": classification.retryable, "reason": classification.reason},
            )
            self._history.setdefault(task_id, []).append(record)
            return record

    def is_fallback_allowed(self, task_id: str, strategy: RecoveryStrategy) -> bool:
        if self.policy_checker is None:
            return False
        return bool(self.policy_checker(task_id, strategy))

    def history(self, task_id: Optional[str] = None) -> List[RecoveryRecord]:
        with self._lock:
            if task_id is not None:
                return list(self._history.get(task_id, []))
            out: List[RecoveryRecord] = []
            for lst in self._history.values():
                out.extend(lst)
            return sorted(out, key=lambda r: r.created_at)

    def attempts(self, task_id: str) -> int:
        with self._lock:
            return self._attempts.get(task_id, 0)

    def clear(self, task_id: Optional[str] = None) -> None:
        with self._lock:
            if task_id is not None:
                self._history.pop(task_id, None)
                self._attempts.pop(task_id, None)
            else:
                self._history.clear()
                self._attempts.clear()

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "attempts": dict(self._attempts),
                "history": {tid: [r.to_dict() for r in lst] for tid, lst in self._history.items()},
                "retry_policy": {"max_attempts": self.retry_policy.max_attempts, "backoff_strategy": self.retry_policy.backoff_strategy, "initial_ms": self.retry_policy.initial_ms, "max_ms": self.retry_policy.max_ms},
            }
