"""Tests for the observability facade (TASK-065 hardening)."""

import logging

import pytest

from aios.runtime.observability import ObservabilityHook


def test_trace_failure_emits_log(caplog):
    hook = ObservabilityHook(component="test")
    with caplog.at_level(logging.ERROR, logger="aios.runtime.test"):
        hook.trace_failure("boom", evidence_ref="e1", step="s1")
    assert "boom" in caplog.text


def test_trace_failure_records_trace():
    hook = ObservabilityHook(component="test")
    hook.trace_failure("boom", evidence_ref="e1")
    assert len(hook.traces()) == 1
    assert hook.traces()[0].message == "boom"
    assert hook.traces()[0].extra.get("evidence_ref") == "e1"


def test_trace_failure_safe_when_metrics_unavailable():
    hook = ObservabilityHook(component="test2", metrics=None)
    hook.trace_failure("x")  # must not raise
    assert len(hook.traces()) == 1


def test_deterministic_trace():
    h1 = ObservabilityHook(component="d")
    h2 = ObservabilityHook(component="d")
    h1.trace_failure("same", evidence_ref="r")
    h2.trace_failure("same", evidence_ref="r")
    assert h1.traces()[0].message == h2.traces()[0].message
