"""Tests for FailureRecovery — AC-012-07/08 (TASK-012)."""

import pytest

from aios.orchestrator.failure_recovery import FailureCategory, FailureClassifier, FailureRecovery, FailureRecoveryError, RecoveryStrategy, RetryPolicy


class TestFailureClassifier:
    def test_transient(self):
        c = FailureClassifier()
        result = c.classify("timeout after 30s")
        assert result.category == FailureCategory.TRANSIENT
        assert result.retryable is True
        assert result.suggested_strategy == RecoveryStrategy.RETRY_SAME

    def test_resource(self):
        c = FailureClassifier()
        result = c.classify("CPU exhausted")
        assert result.category == FailureCategory.RESOURCE
        assert result.retryable is True

    def test_policy(self):
        c = FailureClassifier()
        result = c.classify("permission denied")
        assert result.category == FailureCategory.POLICY
        assert result.retryable is False
        assert result.suggested_strategy == RecoveryStrategy.FAIL

    def test_validation(self):
        c = FailureClassifier()
        result = c.classify("invalid input")
        assert result.category == FailureCategory.VALIDATION
        assert result.retryable is False

    def test_fatal(self):
        c = FailureClassifier()
        result = c.classify("corrupted state")
        assert result.category == FailureCategory.FATAL
        assert result.suggested_strategy == RecoveryStrategy.PAUSE_FOR_HUMAN

    def test_logical_default(self):
        c = FailureClassifier()
        result = c.classify("some unknown error")
        assert result.category == FailureCategory.LOGICAL
        assert result.retryable is False


class TestRetryPolicy:
    def test_validate(self):
        p = RetryPolicy(max_attempts=3, backoff_strategy="exponential", initial_ms=500, max_ms=5000)
        p.validate()

    def test_invalid_max_attempts(self):
        with pytest.raises(FailureRecoveryError):
            RetryPolicy(max_attempts=0).validate()

    def test_backoff_exponential(self):
        p = RetryPolicy(max_attempts=3, backoff_strategy="exponential", initial_ms=500, max_ms=5000)
        assert p.backoff_ms(1) == 500
        assert p.backoff_ms(2) == 1000
        assert p.backoff_ms(3) == 2000
        assert p.backoff_ms(10) == 5000  # capped

    def test_backoff_fixed(self):
        p = RetryPolicy(max_attempts=3, backoff_strategy="fixed", initial_ms=500, max_ms=5000)
        assert p.backoff_ms(1) == 500
        assert p.backoff_ms(5) == 500


class TestFailureRecovery:
    def test_should_retry_transient(self):
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=3))
        assert fr.should_retry("task-001", "timeout") is True

    def test_should_not_retry_policy(self):
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=3))
        assert fr.should_retry("task-001", "permission denied") is False

    def test_bounded_retry(self):
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=2))
        # Attempt 1
        r1 = fr.handle_failure("task-001", "timeout")
        assert r1.strategy == RecoveryStrategy.RETRY_SAME
        assert r1.attempt == 1
        # Attempt 2
        r2 = fr.handle_failure("task-001", "timeout")
        assert r2.strategy == RecoveryStrategy.RETRY_SAME
        assert r2.attempt == 2
        # Attempt 3 -> exhausted, should not retry
        r3 = fr.handle_failure("task-001", "timeout")
        assert r3.attempt == 3
        assert r3.strategy != RecoveryStrategy.RETRY_SAME

    def test_no_infinite_retry(self):
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=3))
        for i in range(10):
            fr.handle_failure("task-001", "timeout")
        assert fr.attempts("task-001") == 10
        # But strategy after max should not be RETRY_SAME
        r = fr.handle_failure("task-001", "timeout")
        assert r.strategy != RecoveryStrategy.RETRY_SAME

    def test_fallback_only_when_policy_allows(self):
        # Without policy_checker, fallback not allowed
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=1))
        fr.handle_failure("task-001", "timeout")  # attempt 1 -> RETRY_SAME
        r = fr.handle_failure("task-001", "timeout")  # attempt 2 -> should be FAIL (no fallback without policy)
        assert r.strategy == RecoveryStrategy.FAIL

        # With policy_checker allowing fallback
        fr2 = FailureRecovery(retry_policy=RetryPolicy(max_attempts=1), policy_checker=lambda tid, strat: True)
        fr2.handle_failure("task-001", "timeout")
        r2 = fr2.handle_failure("task-001", "timeout")
        assert r2.strategy in (RecoveryStrategy.FALLBACK_AGENT, RecoveryStrategy.FALLBACK_WORKFLOW)

    def test_fallback_denied_when_policy_denies(self):
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=1), policy_checker=lambda tid, strat: False)
        fr.handle_failure("task-001", "timeout")
        r = fr.handle_failure("task-001", "timeout")
        assert r.strategy == RecoveryStrategy.FAIL

    def test_history(self):
        fr = FailureRecovery()
        fr.handle_failure("task-001", "timeout")
        fr.handle_failure("task-001", "timeout")
        assert len(fr.history("task-001")) == 2
        assert len(fr.history()) == 2

    def test_clear(self):
        fr = FailureRecovery()
        fr.handle_failure("task-001", "timeout")
        fr.clear("task-001")
        assert len(fr.history("task-001")) == 0
        assert fr.attempts("task-001") == 0

    def test_to_dict(self):
        fr = FailureRecovery()
        fr.handle_failure("task-001", "timeout")
        d = fr.to_dict()
        assert "attempts" in d
        assert "history" in d
        assert "retry_policy" in d

    def test_policy_denied_no_retry(self):
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=3))
        r = fr.handle_failure("task-001", "permission denied")
        assert r.strategy == RecoveryStrategy.FAIL
        assert r.category == FailureCategory.POLICY
