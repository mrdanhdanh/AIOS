"""Tests for execution observation (T146)."""

import pytest

from aios.coding_loop import ExecutionObservation
from aios.coding_loop._common import CodingLoopError


def test_capture_with_provenance():
    o = ExecutionObservation()
    obs = o.capture("exec1", "loop1", ("line1", "line2"), evidence_ref="ev1")
    assert obs.observation_id
    assert obs.execution_ref == "exec1"
    assert obs.loop_ref == "loop1"
    prov = o.provenance(obs.observation_id)
    assert prov["evidence_ref"] == "ev1"
    assert prov["content_hash"]


def test_capture_missing_evidence_rejected():
    o = ExecutionObservation()
    with pytest.raises(CodingLoopError):
        o.capture("exec1", "loop1", ("x",), evidence_ref=None)  # fail-closed


def test_capture_missing_loop_link_rejected():
    o = ExecutionObservation()
    with pytest.raises(CodingLoopError):
        o.capture("exec1", "", ("x",), evidence_ref="ev1")


def test_duplicate_observation_id_rejected():
    o = ExecutionObservation()
    o.capture("exec1", "loop1", ("x",), evidence_ref="ev1", observation_id="obs1")
    with pytest.raises(CodingLoopError):
        o.capture("exec2", "loop1", ("y",), evidence_ref="ev1", observation_id="obs1")


def test_deterministic_same_execution_same_trace():
    o1 = ExecutionObservation()
    o2 = ExecutionObservation()
    a = o1.capture("exec1", "loop1", ("alpha", "beta"), evidence_ref="ev1")
    b = o2.capture("exec1", "loop1", ("alpha", "beta"), evidence_ref="ev1")
    assert a.trace == b.trace  # deterministic


def test_secret_redacted():
    o = ExecutionObservation()
    obs = o.capture("exec1", "loop1", ("password=secret123",), evidence_ref="ev1")
    assert "secret123" not in obs.trace[0]
    assert "***REDACTED***" in obs.trace[0]


def test_get_unknown_rejected():
    o = ExecutionObservation()
    with pytest.raises(CodingLoopError):
        o.get("nope")
