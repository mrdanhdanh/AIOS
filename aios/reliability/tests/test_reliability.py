"""Tests for Reliability Engineering (TASK-069)."""

from __future__ import annotations

import pytest

from aios.reliability import (
    BoundedRetry,
    CircuitBreaker,
    CircuitOpen,
    ErrorBudgetExhausted,
    RetryConfig,
    SLORegistry,
    SLOMetric,
)
from aios.reliability.integration import ReliabilityProbe, register_reliability_probes


# --------------------------------------------------------------------------- #
# SLO + Error Budget
# --------------------------------------------------------------------------- #
def test_slo_registry_records_success_keeps_budget():
    reg = SLORegistry()
    reg.register(SLOMetric(name="api", objective="99.5% success", window="24h"))
    for _ in range(10):
        reg.record("api", success=True)
    assert reg.error_budget_remaining("api") == 1.0
    reg.guard("api")  # must not raise


def test_error_budget_exhausted_is_fail_closed():
    reg = SLORegistry()
    reg.register(SLOMetric(name="api", objective="99.5% success", window="24h"))
    for _ in range(5):
        reg.record("api", success=False)
    assert reg.is_exhausted("api") is True
    with pytest.raises(ErrorBudgetExhausted):
        reg.guard("api")  # degrade safe / stop new work


def test_same_metric_and_policy_is_deterministic():
    reg_a = SLORegistry()
    reg_b = SLORegistry()
    for reg in (reg_a, reg_b):
        reg.register(SLOMetric(name="api", objective="99.5% success", window="24h"))
        for _ in range(3):
            reg.record("api", success=False)
    assert reg_a.error_budget_remaining("api") == reg_b.error_budget_remaining("api")


# --------------------------------------------------------------------------- #
# Circuit Breaker
# --------------------------------------------------------------------------- #
def test_circuit_breaker_opens_on_failure_rate():
    cb = CircuitBreaker(failure_threshold=3)
    assert cb.state.value == "CLOSED"

    def boom():
        raise RuntimeError("down")

    for _ in range(3):
        with pytest.raises(RuntimeError):
            cb.call(boom)
    assert cb.state.value == "OPEN"
    with pytest.raises(CircuitOpen):
        cb.call(boom)


def test_circuit_breaker_half_open_recovers():
    cb = CircuitBreaker(failure_threshold=2)

    def boom():
        raise RuntimeError("down")

    def ok():
        return "ok"

    for _ in range(2):
        with pytest.raises(RuntimeError):
            cb.call(boom)
    assert cb.state.value == "OPEN"
    cb.half_open()
    assert cb.call(ok) == "ok"
    assert cb.state.value == "CLOSED"


# --------------------------------------------------------------------------- #
# Bounded Retry (reuse T065)
# --------------------------------------------------------------------------- #
def test_bounded_retry_recovers_then_stops():
    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("transient")
        return "done"

    retry = BoundedRetry(RetryConfig(max_attempts=5, backoff="none"))
    assert retry.run(flaky) == "done"
    assert attempts["n"] == 3


def test_bounded_retry_escalates_on_exhaustion():
    escalated = []

    def always_fail():
        raise RuntimeError("permanent")

    retry = BoundedRetry(
        RetryConfig(max_attempts=2, backoff="none"),
        escalate=lambda msg, n, exc: escalated.append((msg, n)),
    )
    with pytest.raises(Exception):
        retry.run(always_fail)
    assert escalated, "escalation callback must fire (no infinite loop)"


# --------------------------------------------------------------------------- #
# Health probe integration
# --------------------------------------------------------------------------- #
def test_reliability_probe_fails_when_budget_exhausted():
    reg = SLORegistry()
    reg.register(SLOMetric(name="api", objective="99.5% success", window="24h"))
    for _ in range(5):
        reg.record("api", success=False)
    probe = ReliabilityProbe(reg)
    with pytest.raises(ErrorBudgetExhausted):
        probe()


def test_register_reliability_probes_noop_without_healthcheck():
    reg = SLORegistry()
    reg.register(SLOMetric(name="api", objective="99.5% success", window="24h"))
    # Should not raise even if HealthCheck is unavailable / wrong type.
    register_reliability_probes(object(), reg)
