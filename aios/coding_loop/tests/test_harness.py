"""Tests for the autonomous coding harness (T154)."""

import pytest

from aios.coding_loop import AutonomousCodingHarness, HarnessStatus
from aios.coding_loop._common import CodingLoopError


def test_run_loop_end_to_end_pass():
    h = AutonomousCodingHarness(policy_ref="pol1", baseline=0.5)
    run = h.run(
        execution_ref="exec1",
        trace=("SyntaxError: bad token",),
        progress_metric=0.9,
        output_hash="abc123",
    )
    assert run.status == HarnessStatus.PASS.value
    assert run.safety_ref is not None  # safety decision recorded


def test_run_loop_fail_on_unknown():
    h = AutonomousCodingHarness(policy_ref="pol1", baseline=0.5)
    # Ambiguous trace -> UNKNOWN diagnosis -> not promotable -> FAIL (fail-closed, T078).
    run = h.run(
        execution_ref="exec1",
        trace=("nothing relevant here",),
        progress_metric=0.9,
        output_hash="abc123",
    )
    assert run.status == HarnessStatus.FAIL.value


def test_run_loop_fail_on_regression():
    h = AutonomousCodingHarness(policy_ref="pol1", baseline=0.5)
    # Clear trace but regressed progress -> verification FAIL -> harness FAIL.
    run = h.run(
        execution_ref="exec1",
        trace=("SyntaxError: bad token",),
        progress_metric=0.1,
        output_hash="abc123",
    )
    assert run.status == HarnessStatus.FAIL.value


def test_run_immutable_run_id():
    h = AutonomousCodingHarness(policy_ref="pol1")
    run = h.run("exec1", ("err",), 0.9, "abc", run_id="run1")
    assert run.run_id == "run1"
    with pytest.raises(CodingLoopError):
        h.run("exec1", ("err",), 0.9, "abc", run_id="run1")  # duplicate


def test_run_requires_evidence():
    h = AutonomousCodingHarness(policy_ref="pol1")
    run = h.run("exec1", ("err",), 0.9, "abc")
    assert run.evidence_ref  # provenance present


def test_run_deterministic_same_input_same_output():
    h1 = AutonomousCodingHarness(policy_ref="pol1", baseline=0.5)
    h2 = AutonomousCodingHarness(policy_ref="pol1", baseline=0.5)
    a = h1.run("exec1", ("Timeout exceeded",), 0.9, "abc")
    b = h2.run("exec1", ("Timeout exceeded",), 0.9, "abc")
    assert a.status == b.status  # deterministic (T029)


def test_run_provenance_hash():
    h = AutonomousCodingHarness(policy_ref="pol1", baseline=0.5)
    run = h.run("exec1", ("SyntaxError",), 0.9, "abc")
    prov = h.provenance(run.run_id)
    assert prov["content_hash"]
    assert prov["status"] == run.status
    assert prov["authority"] == "aios"
