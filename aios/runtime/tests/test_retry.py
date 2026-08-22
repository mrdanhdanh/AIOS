"""Tests for bounded retry with backoff + escalation (TASK-065 hardening)."""

import pytest

from aios.runtime.retry import BoundedRetry, RetryBudgetExceeded, RetryConfig


def test_recovers_on_transient_error():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("transient")
        return "ok"

    r = BoundedRetry(RetryConfig(max_attempts=5, backoff="none"))
    assert r.run(flaky) == "ok"
    assert calls["n"] == 3


def test_exhaustion_escalates():
    escalated = []

    def always_fail():
        raise ValueError("nope")

    r = BoundedRetry(
        RetryConfig(max_attempts=2, backoff="none"),
        escalate=lambda msg, attempts, exc: escalated.append((msg, attempts)),
    )
    with pytest.raises(RetryBudgetExceeded):
        r.run(always_fail)
    assert len(escalated) == 1
    assert escalated[0][1] == 2


def test_non_retryable_stops_immediately():
    calls = {"n": 0}

    def fail():
        calls["n"] += 1
        raise RuntimeError("fatal")

    r = BoundedRetry(
        RetryConfig(max_attempts=5, backoff="none", retryable_errors=["transient"])
    )
    with pytest.raises(RetryBudgetExceeded):
        r.run(fail)
    assert calls["n"] == 1


def test_deterministic():
    counts = []
    for _ in range(2):
        c = {"n": 0}

        def f():
            c["n"] += 1
            raise ValueError("x")

        r = BoundedRetry(RetryConfig(max_attempts=3, backoff="none"))
        try:
            r.run(f)
        except RetryBudgetExceeded:
            pass
        counts.append(c["n"])
    assert counts[0] == counts[1] == 3
