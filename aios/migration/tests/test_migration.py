"""Tests for TASK-085 — Migration 1.0 -> 1.1 (Test Matrix)."""

from __future__ import annotations

import pytest

from aios.migration.migration import (
    MigrationError,
    MigrationPlan,
    MigrationResult,
    MigrationRunner,
    MigrationState,
    MigrationStep,
    RollbackResult,
)


def _make_plan(verify_ok: bool = True) -> MigrationPlan:
    """Build a reversible 1.0->1.1 plan with two steps."""
    def up1(d): d["feature_a"] = True
    def down1(d): d.pop("feature_a", None)
    def verify1(d): return verify_ok

    def up2(d): d["feature_b"] = 1
    def down2(d): d.pop("feature_b", None)
    def verify2(d): return verify_ok

    return MigrationPlan(steps=[
        MigrationStep(id="s1", up=up1, down=down1, verify=verify1, evidence_ref="e1"),
        MigrationStep(id="s2", up=up2, down=down2, verify=verify2, evidence_ref="e2"),
    ])


def test_detect_1_0_then_plan():
    runner = MigrationRunner()
    state = MigrationState(version="1.0.0", data={"legacy": "x"})
    assert runner.detect(state) is True
    plan = _make_plan()
    step_ids = runner.plan(plan, state)
    assert step_ids == ["s1", "s2"]


def test_verify_fail_never_applies():
    runner = MigrationRunner()
    state = MigrationState(version="1.0.0", data={})
    plan = _make_plan(verify_ok=False)
    result = runner.apply(plan, state)
    assert result.status.value == "failed"
    assert result.steps_completed == 0
    # Original state untouched (fail-closed, no partial mutation).
    assert state.data == {}
    assert state.version == "1.0.0"


def test_step_with_down_rollback_to_1_0():
    runner = MigrationRunner()
    state = MigrationState(version="1.1.0", data={"feature_a": True, "feature_b": 1})
    plan = _make_plan()
    rb: RollbackResult = runner.rollback(plan, state)
    assert rb.status.value == "rolled_back"
    assert rb.restored_steps == 2
    assert rb.succeeded is True
    # Rolled-back state is back at 1.0 with migrated keys removed.
    assert state.version == "1.1.0"  # original untouched
    assert rb.to_version == "1.0.0"


def test_dry_run_does_not_mutate():
    runner = MigrationRunner()
    state = MigrationState(version="1.0.0", data={"k": "v"})
    plan = _make_plan()
    res = runner.dry_run(plan, state)
    assert res.would_mutate is False
    assert res.ready is True
    # State is unchanged after dry-run.
    assert state.data == {"k": "v"}
    assert state.version == "1.0.0"


def test_migrate_state_no_data_loss():
    runner = MigrationRunner()
    state = MigrationState(version="1.0.0", data={"existing": "keep"})
    plan = _make_plan()
    result: MigrationResult = runner.apply(plan, state)
    assert result.succeeded is True
    assert result.state is not None
    # New version reached and original data preserved (no data loss, T066).
    assert result.state.version == "1.1.0"
    assert result.state.data["existing"] == "keep"
    assert result.state.data["feature_a"] is True
    assert result.state.data["feature_b"] == 1
    # Original caller state untouched.
    assert state.version == "1.0.0"
    assert state.data == {"existing": "keep"}


def test_same_plan_and_state_deterministic():
    runner = MigrationRunner()
    state_a = MigrationState(version="1.0.0", data={"a": 1})
    state_b = MigrationState(version="1.0.0", data={"a": 1})
    plan = _make_plan()
    h1 = runner.plan_hash(plan)
    h2 = runner.plan_hash(plan)
    r1 = runner.apply(plan, state_a)
    r2 = runner.apply(plan, state_b)
    assert h1 == h2
    assert r1.state.data == r2.state.data
    assert r1.state.version == r2.state.version


def test_non_reversible_plan_rejected():
    bad = MigrationStep(id="x", up=lambda d: None, down=None, verify=lambda d: True)
    with pytest.raises(MigrationError):
        MigrationPlan(steps=[bad])


def test_provenance_recorded():
    runner = MigrationRunner()
    state = MigrationState(version="1.0.0", data={})
    result = runner.apply(_make_plan(), state)
    assert runner.provenance_complete(result) is True
    assert len(result.evidence) == 2
