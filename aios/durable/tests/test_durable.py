"""Tests for TASK-066 Durable Execution 1.0.

Covers every Acceptance Criterion and every Test Matrix row:

  AC1  durable checkpoint persists across restart
  AC2  resume ONLY from a verified checkpoint (fail-closed)
  AC3  resume does not double-execute a done step (idempotency)
  AC4  checkpoint carries provenance evidence
  AC5  same checkpoint + protocol -> same state (deterministic)
  AC6  integrates with Runtime state store (T065) + Recovery (T055)
  AC7  no parallel execution store (reuses runtime state-store concepts)
  AC8  no invariant violation (package tests stay green)

  Matrix:
    crash mid-step            -> resume from most recent verified
    unverified checkpoint     -> no resume (fail-closed)
    resume done step          -> idempotent, no double-execute
    restart                   -> checkpoint recovered
    same checkpoint+protocol  -> same state (deterministic)
    checkpoint has evidence   -> provenance complete
"""

from __future__ import annotations

import os
import tempfile

from aios.autonomous_recovery.contracts import RecoveryStrategy, RecoveryVerdict
from aios.runtime.state import ExecutionState, RunStatus

from aios.durable import (
    Checkpoint,
    CheckpointStore,
    IdempotencyGuard,
    ResumeError,
    ResumeProtocol,
)
from aios.durable.integration import (
    build_resume_attempt,
    checkpoint_from_execution_state,
    runtime_state_hash,
)


def _cp(
    execution_id: str,
    step_id: str,
    verified: bool,
    created_at: str,
    evidence_ref: str = "ev-1",
    state_hash: str = "h",
    checkpoint_id: str | None = None,
) -> Checkpoint:
    return Checkpoint(
        execution_id=execution_id,
        step_id=step_id,
        state_hash=state_hash,
        verified=verified,
        created_at=created_at,
        evidence_ref=evidence_ref,
        checkpoint_id=checkpoint_id or f"dcp-{step_id}",
    )


# --------------------------------------------------------------------------- #
# AC1 + Matrix row "restart" : durable checkpoint persists across restart
# --------------------------------------------------------------------------- #
def test_checkpoint_persists_across_restart() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "chk.json")
        store = CheckpointStore(path)
        store.save(_cp("e1", "s1", True, "2026-01-01T00:00:00+00:00"))

        # Simulate a process restart: a brand-new store reading the same file.
        store2 = CheckpointStore(path)
        loaded = store2.load("e1")
        assert len(loaded) == 1
        assert loaded[0].verified is True
        assert loaded[0].execution_id == "e1"
        assert loaded[0].step_id == "s1"


def test_store_recovers_multiple_checkpoints_after_restart() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "chk.json")
        store = CheckpointStore(path)
        store.save(_cp("e1", "s1", True, "2026-01-01T00:00:00+00:00"))
        store.save(_cp("e1", "s2", True, "2026-01-01T00:00:01+00:00"))

        store2 = CheckpointStore(path)
        assert len(store2.load("e1")) == 2


# --------------------------------------------------------------------------- #
# AC2 + Matrix row "unverified checkpoint" : fail-closed, no resume
# --------------------------------------------------------------------------- #
def test_resume_only_from_verified() -> None:
    store = CheckpointStore()
    store.save(_cp("e1", "s1", True, "2026-01-01T00:00:00+00:00"))
    store.save(_cp("e1", "s2", True, "2026-01-01T00:00:01+00:00"))
    proto = ResumeProtocol(store)
    cp = proto.resume("e1")
    assert cp.step_id == "s2"
    assert cp.verified is True


def test_resume_fail_closed_on_unverified_only() -> None:
    store = CheckpointStore()
    store.save(_cp("e1", "s1", False, "2026-01-01T00:00:00+00:00"))
    proto = ResumeProtocol(store)
    try:
        proto.resume("e1")
        assert False, "expected ResumeError"
    except ResumeError:
        pass


def test_resume_fail_closed_on_no_checkpoints() -> None:
    store = CheckpointStore()
    proto = ResumeProtocol(store)
    try:
        proto.resume("missing")
        assert False, "expected ResumeError"
    except ResumeError:
        pass


def test_can_resume_probe() -> None:
    store = CheckpointStore()
    store.save(_cp("e1", "s1", False, "2026-01-01T00:00:00+00:00"))
    proto = ResumeProtocol(store)
    assert proto.can_resume("e1") is False
    store.save(_cp("e1", "s2", True, "2026-01-01T00:00:01+00:00"))
    assert proto.can_resume("e1") is True


# --------------------------------------------------------------------------- #
# AC3 + Matrix row "resume done step" : idempotent, no double side-effect
# --------------------------------------------------------------------------- #
def test_idempotency_no_double_execute() -> None:
    guard = IdempotencyGuard()
    calls = {"n": 0}

    def side_effect() -> str:
        calls["n"] += 1
        return "done"

    r1 = guard.execute_once("s1", side_effect)
    assert r1.executed is True
    assert calls["n"] == 1

    # Resume / re-execute the same step -> must NOT run the action again.
    r2 = guard.execute_once("s1", side_effect)
    assert r2.executed is False
    assert calls["n"] == 1  # unchanged -> no double side-effect
    assert r2.result == "done"


def test_resume_done_step_idempotent() -> None:
    store = CheckpointStore()
    store.save(
        _cp("e1", "s1", True, "2026-01-01T00:00:00+00:00", evidence_ref="ev-1")
    )
    proto = ResumeProtocol(store)
    cp = proto.resume("e1")

    guard = IdempotencyGuard()
    guard.mark_done(cp.step_id)  # step already completed before crash
    calls = {"n": 0}

    def act() -> None:
        calls["n"] += 1

    out = guard.execute_once(cp.step_id, act)
    assert out.executed is False
    assert calls["n"] == 0


# --------------------------------------------------------------------------- #
# AC4 + Matrix row "checkpoint has evidence" : provenance complete
# --------------------------------------------------------------------------- #
def test_checkpoint_has_evidence() -> None:
    cp = _cp(
        "e1", "s1", True, "2026-01-01T00:00:00+00:00", evidence_ref="ev-abc"
    )
    assert cp.evidence_ref == "ev-abc"
    assert cp.evidence_ref  # non-empty provenance reference

    # Round-trip preserves provenance.
    cp2 = Checkpoint.from_dict(cp.to_dict())
    assert cp2.evidence_ref == cp.evidence_ref


# --------------------------------------------------------------------------- #
# AC5 + Matrix row "same checkpoint + protocol" : deterministic
# --------------------------------------------------------------------------- #
def _build_store() -> CheckpointStore:
    s = CheckpointStore()
    s.save(_cp("e1", "s1", True, "2026-01-01T00:00:00+00:00", state_hash="h1"))
    s.save(_cp("e1", "s2", True, "2026-01-01T00:00:01+00:00", state_hash="h2"))
    return s


def test_deterministic_resume() -> None:
    a = ResumeProtocol(_build_store()).resume("e1")
    b = ResumeProtocol(_build_store()).resume("e1")
    assert a.checkpoint_id == b.checkpoint_id
    assert a.state_hash == b.state_hash
    assert a.content_hash == b.content_hash


def test_checkpoint_content_hash_deterministic() -> None:
    a = _cp("e1", "s1", True, "2026-01-01T00:00:00+00:00", state_hash="h")
    b = _cp("e1", "s1", True, "2026-01-01T00:00:00+00:00", state_hash="h")
    assert a.content_hash == b.content_hash


# --------------------------------------------------------------------------- #
# AC6 + AC7 : integration with Runtime state store (T065) + Recovery (T055),
#            and reuse (no parallel store)
# --------------------------------------------------------------------------- #
def test_integration_with_runtime_state() -> None:
    state = ExecutionState(execution_id="e1", status=RunStatus.RUNNING)
    state.set_step("s1", "COMPLETED")

    cp = checkpoint_from_execution_state(state, "s1", "ev-1", verified=True)
    assert cp.execution_id == "e1"
    assert cp.step_id == "s1"
    assert cp.verified is True
    assert cp.state_hash  # derived from runtime checkpoint hash

    store = CheckpointStore()
    store.save(cp)
    resumed = ResumeProtocol(store).resume("e1")

    attempt = build_resume_attempt("e1", resumed, outcome=RecoveryVerdict.RECOVERED)
    assert attempt.strategy == RecoveryStrategy.RESUME
    assert attempt.execution_id == "e1"
    assert attempt.outcome == RecoveryVerdict.RECOVERED


def test_reuses_runtime_state_store_hash() -> None:
    # The durable checkpoint's state_hash equals the runtime checkpoint hash,
    # proving we reuse (not duplicate) the runtime state store.
    state = ExecutionState(execution_id="e1")
    state.set_step("s1", "COMPLETED")
    cp = checkpoint_from_execution_state(state, "s1", "ev-1")
    runtime_hash = runtime_state_hash(state)
    assert cp.state_hash == runtime_hash


# --------------------------------------------------------------------------- #
# Matrix row "crash mid-step" : resume from most recent verified
# --------------------------------------------------------------------------- #
def test_crash_mid_step_resume_from_verified() -> None:
    store = CheckpointStore()
    store.save(_cp("e1", "s1", True, "2026-01-01T00:00:00+00:00"))  # completed step
    store.save(
        _cp("e1", "s2", False, "2026-01-01T00:00:01+00:00")
    )  # crash mid-step (unverified)
    cp = ResumeProtocol(store).resume("e1")
    assert cp.step_id == "s1"  # most recent VERIFIED
    assert cp.verified is True
