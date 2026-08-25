"""Tests for RetryGuard (TASK-226)."""

from aios.runtime.retry_guard import RetryGuard, DEFAULT_THRESHOLD


def test_threshold_default():
    g = RetryGuard()
    assert g.threshold == DEFAULT_THRESHOLD


def test_auto_stop_after_threshold():
    g = RetryGuard(threshold=3)
    assert g.observe("errA", "boom") is False
    assert g.observe("errA", "boom") is False
    assert g.observe("errA", "boom") is True
    assert g.should_stop("errA") is True
    assert g.count("errA") == 3


def test_distinct_signatures_independent():
    g = RetryGuard(threshold=2)
    assert g.observe("x") is False
    assert g.observe("y") is False
    assert g.should_stop("x") is False
    assert g.should_stop("y") is False


def test_report_root_cause():
    g = RetryGuard(threshold=2)
    g.observe("e", "disk full")
    g.observe("e", "disk full")
    r = g.report("e")
    assert "disk full" in r and "AUTO-STOP" in r


def test_reset_clears():
    g = RetryGuard(threshold=2)
    g.observe("e")
    g.observe("e")
    g.reset("e")
    assert g.should_stop("e") is False
    assert g.count("e") == 0


def test_invalid_threshold():
    try:
        RetryGuard(threshold=0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_empty_signature_rejected():
    g = RetryGuard()
    try:
        g.observe("")
        assert False, "expected ValueError"
    except ValueError:
        pass
