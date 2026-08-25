"""Tests for StubGuard (TASK-227)."""

from aios.runtime.stub_guard import StubGuard, VALID, SKIP_MARKERS


def test_valid_statuses_clean():
    g = StubGuard()
    g.record("a", "OK")
    g.record("b", "COMPLETED")
    g.record("c", "FAILED", "reason")
    assert g.is_clean()
    assert g.violations() == []


def test_skip_detected():
    g = StubGuard()
    g.record("x", "SKIPPED", "no reason")
    assert g.is_skip("SKIPPED")
    assert not g.is_clean()
    v = g.violations()
    assert len(v) == 1 and v[0].step_id == "x"


def test_null_stub_markers():
    g = StubGuard()
    for marker in ("null", "stub", "_NullOrchestrator", "skip"):
        assert g.is_skip(marker)


def test_unknown_status_rejected():
    g = StubGuard()
    g.record("z", "WEIRD")
    assert not g.is_clean()


def test_report_lists_violations():
    g = StubGuard()
    g.record("a", "OK")
    g.record("b", "SKIPPED", "stub")
    r = g.report()
    assert "SKIPPED" in r and "b" in r


def test_reset_clears():
    g = StubGuard()
    g.record("a", "SKIPPED")
    g.reset()
    assert g.is_clean()


def test_empty_inputs_rejected():
    g = StubGuard()
    try:
        g.record("", "OK")
        assert False, "expected ValueError"
    except ValueError:
        pass
    try:
        g.record("a", "")
        assert False, "expected ValueError"
    except ValueError:
        pass
