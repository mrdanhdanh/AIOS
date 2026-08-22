"""Tests for TASK-055 Autonomous Recovery."""
from __future__ import annotations

from aios.autonomous_recovery.circuit import CircuitBreaker
from aios.autonomous_recovery.contracts import CircuitState, FailureClass, RecoveryStrategy, RecoveryVerdict
from aios.autonomous_recovery.recovery import FailureClassifier, RecoveryController, RecoveryPolicy


def test_classifier():
    c = FailureClassifier()
    assert c.classify("connection timeout") == FailureClass.TRANSIENT
    assert c.classify("out of memory") == FailureClass.RESOURCE
    assert c.classify("capability unavailable") == FailureClass.DEPENDENCY
    assert c.classify("permission denied") == FailureClass.POLICY
    assert c.classify("corrupted state") == FailureClass.STATE
    assert c.classify("expected condition not met") == FailureClass.LOGICAL
    assert c.classify("weird thing") == FailureClass.UNKNOWN


def test_circuit_breaker_opens_and_recovers():
    import time
    b = CircuitBreaker(failure_threshold=2, cooldown=999.0)
    b.record_failure()
    b.record_failure()
    assert b.state == CircuitState.OPEN
    assert not b.allow_request()  # cooldown not elapsed -> blocked
    # simulate cooldown elapsed
    b.last_failure = time.time() - 1000.0
    assert b.allow_request()  # transitions to HALF_OPEN
    assert b.state == CircuitState.HALF_OPEN
    b.record_success()
    assert b.state == CircuitState.CLOSED


def test_recovery_retry_then_recovered():
    ctrl = RecoveryController(policy=RecoveryPolicy(retry_max_attempts=3))
    calls = {"n": 0}

    def action(strategy):
        calls["n"] += 1
        return {"ok": True}

    def verify(post, pre):
        return post.get("ok") is True

    att = ctrl.attempt("ex1", "temporary timeout", {"s": 1}, action, verify)
    assert att.outcome == RecoveryVerdict.RECOVERED
    assert att.strategy == RecoveryStrategy.RETRY
    assert calls["n"] == 1


def test_recovery_unverified_not_recovered():
    ctrl = RecoveryController()
    def action(strategy):
        return {"ok": False}
    def verify(post, pre):
        return post.get("ok") is True
    att = ctrl.attempt("ex2", "transient failure", {}, action, verify)
    assert att.outcome == RecoveryVerdict.NOT_RECOVERED
    assert att.verification == "unverified"


def test_unknown_failure_safe_stops():
    ctrl = RecoveryController()
    att = ctrl.attempt("ex3", "mysterious failure", {}, lambda s: {}, lambda p, pre: True)
    assert att.strategy == RecoveryStrategy.SAFE_STOP
    assert att.outcome == RecoveryVerdict.NOT_RECOVERED


def test_governor_denies_escalation():
    def gov(strategy, ctx):
        return False
    ctrl = RecoveryController(governor_decision=gov)
    att = ctrl.attempt("ex4", "policy denied", {}, lambda s: {}, lambda p, pre: True)
    assert att.outcome == RecoveryVerdict.NOT_RECOVERED
    assert "governor" in att.verification


def test_circuit_open_blocks_recovery():
    b = CircuitBreaker(failure_threshold=1, cooldown=999.0)
    b.record_failure()  # now OPEN
    ctrl = RecoveryController(breaker=b)
    att = ctrl.attempt("ex5", "transient", {}, lambda s: {}, lambda p, pre: True)
    assert att.strategy == RecoveryStrategy.SAFE_STOP
    assert "circuit_open" in att.verification


def test_recovery_attempt_records_provenance():
    ctrl = RecoveryController()
    att = ctrl.attempt("ex6", "timeout", {"pre": 1}, lambda s: {"ok": True},
                       lambda p, pre: True, evidence=["ev:1"])
    assert att.evidence == ["ev:1"]
    assert att.classification == FailureClass.TRANSIENT
    assert att.execution_id == "ex6"
