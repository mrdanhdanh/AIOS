"""Tests for deterministic RenderReplay harness (TASK-079, M11)."""

from __future__ import annotations

import pytest

from aios.replay.replay import Recorder, Replayer, ReplayError


def _evaluator(inputs):
    # Deterministic: verdict derived purely from inputs.
    return "pass" if "good" in inputs else "fail"


def test_record_then_replay_matches():
    rec = Recorder()
    h = rec.record("run-1", {"cmd": "good"}, {"ev": "snap"}, "1.0.0", "strict", "pass")
    assert h
    rep = Replayer(rec).replay("run-1", _evaluator, "ev-ref")
    assert rep.matches_original is True
    assert rep.replay_verdict == "pass"


def test_replay_mismatch_flags_nondeterminism():
    rec = Recorder()
    # original recorded as "pass" but evaluator would now produce "fail"
    rec.record("run-2", {"cmd": "bad"}, {}, "1.0.0", "strict", "pass")
    rep = Replayer(rec).replay("run-2", _evaluator, "ev-ref")
    assert rep.matches_original is False
    assert any("non-determinism" in n for n in rep.notes)


def test_replay_unknown_run_raises():
    with pytest.raises(ReplayError):
        Replayer(Recorder()).replay("missing", _evaluator)


def test_recorded_inputs_hash_stable():
    rec = Recorder()
    a = rec.record("r", {"x": 1}, {}, "1.0", "")
    b = rec.record("r2", {"x": 1}, {}, "1.0", "")
    assert a == b  # same normalized inputs -> same hash


def test_deterministic_same_input_same_verdict():
    rec = Recorder()
    rec.record("d", {"k": "v"}, {}, "1.0", "c", "pass")
    r1 = Replayer(rec).replay("d", _evaluator)
    r2 = Replayer(rec).replay("d", _evaluator)
    assert r1.replay_verdict == r2.replay_verdict
    assert r1.recorded_inputs_hash == r2.recorded_inputs_hash
