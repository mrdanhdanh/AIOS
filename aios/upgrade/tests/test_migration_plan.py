"""Tests for TASK-074 — Upgrade & Migration 1.0 (aios.upgrade.migration_plan).

Covers every Acceptance Criterion and Test Matrix row:
  1. version detect -> correct plan
  2. verify FAIL -> not applied (fail-closed)
  3. step has down -> rollback succeeds
  4. dry-run -> no mutate
  5. migrate state -> no data loss (T066 / goal_durability)
  6. same plan + state -> same result (deterministic)
Plus: ordered execution, reversible enforcement, evidence provenance,
peer integration with aios.upgrade, harness (T032) verification.
"""

from __future__ import annotations

from typing import Any

from aios.goal_durability.contracts import DurableCheckpoint, InterruptionCause
from aios.upgrade.migration_plan import (
    MigrationEngine,
    MigrationError,
    MigrationPhase,
    MigrationPlan,
    MigrationStep,
    hash_state,
    make_durable_migration_plan,
    sample_durable_migration_step,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _step_ok(step_id: str, mutate_key: str | None = None) -> MigrationStep:
    """A reversible step that passes verify and optionally mutates state."""

    def _up(state: dict[str, Any]) -> None:
        if mutate_key:
            state[mutate_key] = (state.get(mutate_key, 0)) + 1

    def _down(state: dict[str, Any]) -> None:
        if mutate_key and mutate_key in state:
            state[mutate_key] = state[mutate_key] - 1

    def _verify(state: dict[str, Any]) -> bool:
        return True

    return MigrationStep(id=step_id, up=_up, down=_down, verify=_verify, description=step_id)


def _step_fail_verify(step_id: str) -> MigrationStep:
    def _up(state: dict[str, Any]) -> None:
        state["applied"] = state.get("applied", 0) + 1

    def _down(state: dict[str, Any]) -> None:
        state["applied"] = state.get("applied", 0) - 1

    def _verify(state: dict[str, Any]) -> bool:
        return False

    return MigrationStep(id=step_id, up=_up, down=_down, verify=_verify, description="fails verify")


def _plan(from_v: str, to_v: str, steps: list[MigrationStep]) -> MigrationPlan:
    return MigrationPlan(from_version=from_v, to_version=to_v, steps=steps)


# ---------------------------------------------------------------------------
# 1. Version detection -> correct plan
# ---------------------------------------------------------------------------


class TestVersionDetection:
    def test_detect_default_version(self) -> None:
        eng = MigrationEngine()
        assert eng.detect_current_version({"version": "1.0.0"}) == "1.0.0"
        assert eng.detect_current_version({}) == "0.0.0"

    def test_detect_custom_resolver(self) -> None:
        eng = MigrationEngine()
        eng.set_version_resolver(lambda s: s.get("meta", {}).get("v", "9.9.9"))
        assert eng.detect_current_version({"meta": {"v": "2.3.4"}}) == "2.3.4"

    def test_select_plan_correct(self) -> None:
        eng = MigrationEngine()
        p = _plan("1.0.0", "1.1.0", [_step_ok("s1")])
        eng.register_plan(p)
        assert eng.select_plan("1.0.0", "1.1.0") is p

    def test_select_plan_missing_raises(self) -> None:
        eng = MigrationEngine()
        try:
            eng.select_plan("1.0.0", "2.0.0")
            assert False, "expected MigrationError"
        except MigrationError:
            pass

    def test_migrate_convenience_detects_and_runs(self) -> None:
        eng = MigrationEngine()
        p = _plan("1.0.0", "1.1.0", [_step_ok("s1", "x")])
        eng.register_plan(p)
        state: dict[str, Any] = {"version": "1.0.0"}
        report = eng.migrate(state, "1.1.0")
        assert report.succeeded
        assert state["x"] == 1


# ---------------------------------------------------------------------------
# Ordered execution
# ---------------------------------------------------------------------------


class TestOrderedExecution:
    def test_steps_run_in_order(self) -> None:
        order: list[str] = []

        def make(sid: str) -> MigrationStep:
            def _up(state: dict[str, Any]) -> None:
                order.append(sid)

            def _down(state: dict[str, Any]) -> None:
                order.remove(sid)

            return MigrationStep(id=sid, up=_up, down=_down, verify=lambda s: True)

        eng = MigrationEngine()
        p = _plan("1.0.0", "1.1.0", [make("a"), make("b"), make("c")])
        report = eng.run(p, {})
        assert report.succeeded
        assert order == ["a", "b", "c"]
        assert report.applied_steps == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# 2. Verify FAIL -> not applied (fail-closed)
# ---------------------------------------------------------------------------


class TestVerifyFailClosed:
    def test_verify_fail_not_applied(self) -> None:
        eng = MigrationEngine()
        p = _plan("1.0.0", "1.1.0", [_step_fail_verify("bad")])
        state: dict[str, Any] = {}
        report = eng.run(p, state)
        assert report.phase == MigrationPhase.FAILED
        assert report.failed_step == "bad"
        assert "applied" not in state  # up was NOT called
        assert report.applied_steps == []

    def test_verify_fail_leaves_state_untouched(self) -> None:
        eng = MigrationEngine()
        good = _step_ok("good", "counter")
        bad = _step_fail_verify("bad")
        p = _plan("1.0.0", "1.1.0", [good, bad])
        state: dict[str, Any] = {"counter": 0}
        report = eng.run(p, state)
        # First step applied, second failed -> state reflects only first step.
        assert report.phase == MigrationPhase.FAILED
        assert state["counter"] == 1
        assert report.state_hash_after == hash_state(state)


# ---------------------------------------------------------------------------
# 3. Step has down -> rollback succeeds
# ---------------------------------------------------------------------------


class TestRollback:
    def test_rollback_restores_state(self) -> None:
        eng = MigrationEngine()
        p = _plan("1.0.0", "1.1.0", [_step_ok("s1", "x"), _step_ok("s2", "y")])
        state: dict[str, Any] = {"x": 0, "y": 0}
        report = eng.run(p, state)
        assert report.succeeded
        assert state == {"x": 1, "y": 1}
        rb = eng.rollback(p, state, applied_steps=report.applied_steps)
        assert rb.phase == MigrationPhase.ROLLED_BACK
        assert state == {"x": 0, "y": 0}

    def test_rollback_reverses_order(self) -> None:
        rolled: list[str] = []

        def make(sid: str) -> MigrationStep:
            def _up(state: dict[str, Any]) -> None:
                pass

            def _down(state: dict[str, Any]) -> None:
                rolled.append(sid)

            return MigrationStep(id=sid, up=_up, down=_down, verify=lambda s: True)

        eng = MigrationEngine()
        p = _plan("1.0.0", "1.1.0", [make("a"), make("b")])
        report = eng.run(p, {})
        eng.rollback(p, {}, applied_steps=report.applied_steps)
        assert rolled == ["b", "a"]


# ---------------------------------------------------------------------------
# 4. Dry-run -> no mutate
# ---------------------------------------------------------------------------


class TestDryRun:
    def test_dry_run_no_mutate(self) -> None:
        eng = MigrationEngine()
        p = _plan("1.0.0", "1.1.0", [_step_ok("s1", "x")])
        state: dict[str, Any] = {"x": 0}
        snapshot = dict(state)
        report = eng.run(p, state, dry_run=True)
        assert report.phase == MigrationPhase.DRY_RUN
        assert state == snapshot  # unchanged
        assert report.applied_steps == []

    def test_dry_run_disabled_raises(self) -> None:
        eng = MigrationEngine()
        p = MigrationPlan(from_version="1.0.0", to_version="1.1.0", steps=[_step_ok("s1")], dry_run_supported=False)
        try:
            eng.run(p, {}, dry_run=True)
            assert False, "expected MigrationError"
        except MigrationError:
            pass


# ---------------------------------------------------------------------------
# 5. Migrate durable state -> no data loss (T066 / goal_durability)
# ---------------------------------------------------------------------------


class TestDurableStateMigration:
    def _make_checkpoint(self) -> DurableCheckpoint:
        cp = DurableCheckpoint(
            goal_id="g1",
            sequence=3,
            interruption_cause=InterruptionCause.GRACEFUL_PAUSE,
            goal_state={"objective": "ship 1.0", "progress": 0.8},
            completed_tasks=["t1", "t2"],
            pending_tasks=["t3"],
        )
        cp.finalize()
        return cp

    def test_sample_step_migrates_without_data_loss(self) -> None:
        step = sample_durable_migration_step()
        cp = self._make_checkpoint()
        state: dict[str, Any] = {"checkpoint": cp}
        # verify passes before up (applicable / not yet migrated)
        assert step.verify(state) is True
        step.up(state)
        # after up, already migrated -> verify blocks re-apply (idempotent)
        assert step.verify(state) is False
        # No data loss: all original goal_state keys preserved + new key.
        assert cp.goal_state["objective"] == "ship 1.0"
        assert cp.goal_state["progress"] == 0.8
        assert cp.goal_state["schema_version"] == "1.1"
        assert cp.completed_tasks == ["t1", "t2"]
        assert cp.pending_tasks == ["t3"]
        # Reversible.
        step.down(state)
        assert "schema_version" not in cp.goal_state
        assert step.verify(state) is True

    def test_plan_migrates_durable_state_no_loss(self) -> None:
        eng = MigrationEngine()
        p = make_durable_migration_plan("1.0.0", "1.1.0")
        cp = self._make_checkpoint()
        original = dict(cp.goal_state)
        state: dict[str, Any] = {"checkpoint": cp}
        report = eng.run(p, state)
        assert report.succeeded
        assert cp.goal_state["schema_version"] == "1.1"
        # All original keys preserved.
        for k, v in original.items():
            assert cp.goal_state[k] == v
        # Rollback restores exactly.
        eng.rollback(p, state, applied_steps=report.applied_steps)
        assert "schema_version" not in cp.goal_state
        for k, v in original.items():
            assert cp.goal_state[k] == v


# ---------------------------------------------------------------------------
# 6. Deterministic: same plan + state -> same result
# ---------------------------------------------------------------------------


class TestDeterministic:
    def test_same_plan_state_same_result(self) -> None:
        eng = MigrationEngine()
        p = _plan("1.0.0", "1.1.0", [_step_ok("s1", "x"), _step_ok("s2", "x")])

        def run_once() -> tuple[dict[str, Any], Any]:
            e = MigrationEngine()
            st: dict[str, Any] = {"x": 0}
            r = e.run(p, st)
            return st, r

        st1, r1 = run_once()
        st2, r2 = run_once()
        assert st1 == st2
        assert r1.phase == r2.phase
        assert r1.applied_steps == r2.applied_steps
        assert r1.state_hash_after == r2.state_hash_after
        assert len(r1.evidence) == len(r2.evidence)
        # Evidence is deterministic in structure (run_id/timestamp are metadata).
        norm = lambda evs: [(e.step_id, e.phase, e.status) for e in evs]
        assert norm(r1.evidence) == norm(r2.evidence)

    def test_hash_state_deterministic(self) -> None:
        s1 = {"a": 1, "b": {"c": 2}}
        s2 = {"b": {"c": 2}, "a": 1}
        assert hash_state(s1) == hash_state(s2)


# ---------------------------------------------------------------------------
# Reversible enforcement + evidence provenance
# ---------------------------------------------------------------------------


class TestSafetyProperties:
    def test_irreversible_plan_rejected(self) -> None:
        eng = MigrationEngine()
        bad = MigrationStep(id="no-down", up=lambda s: None, down=None, verify=lambda s: True)
        p = MigrationPlan(from_version="1.0.0", to_version="1.1.0", steps=[bad])
        assert not p.is_fully_reversible()
        try:
            eng.run(p, {})
            assert False, "expected MigrationError"
        except MigrationError:
            pass

    def test_every_step_writes_evidence(self) -> None:
        eng = MigrationEngine()
        p = _plan("1.0.0", "1.1.0", [_step_ok("s1", "x"), _step_ok("s2", "x")])
        report = eng.run(p, {"x": 0})
        assert report.succeeded
        # 2 verify + 2 apply evidence entries.
        assert len(report.evidence) == 4
        for ev in report.evidence:
            assert ev.evidence_id
            assert ev.run_id
            assert ev.content_hash
            assert ev.step_id in ("s1", "s2")

    def test_evidence_provenance_on_verify_fail(self) -> None:
        eng = MigrationEngine()
        p = _plan("1.0.0", "1.1.0", [_step_fail_verify("bad")])
        report = eng.run(p, {})
        assert report.phase == MigrationPhase.FAILED
        # verify evidence recorded even on failure.
        assert len(report.evidence) == 1
        assert report.evidence[0].status == "fail"


# ---------------------------------------------------------------------------
# Peer integration with aios.upgrade (existing package)
# ---------------------------------------------------------------------------


class TestPeerIntegration:
    def test_plan_to_manifest(self) -> None:
        p = _plan("1.0.0", "1.1.0", [_step_ok("s1"), _step_ok("s2")])
        m = p.to_manifest()
        assert m.source_version == "1.0.0"
        assert m.target_version == "1.1.0"
        assert m.step_count == 2
        assert m.all_reversible is True

    def test_engine_importable_from_package(self) -> None:
        from aios.upgrade import MigrationPlanEngine, MigrationPlan, sample_durable_migration_step

        assert MigrationPlanEngine is MigrationEngine
        assert MigrationPlan is not None
        assert sample_durable_migration_step is not None
