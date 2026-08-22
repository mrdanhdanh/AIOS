"""Tests for TASK-067 Autonomy Safety 1.0 (bounded autonomy).

Covers every Acceptance Criterion and every Test Matrix row:
  - action in boundary            -> ALLOW (Governor)
  - action out of boundary        -> BLOCK (Governor)
  - level raised without policy   -> blocked
  - boundary violated             -> SAFE_STOP (fail-closed)
  - same context + action         -> same decision (deterministic)
  - escalate_on risk              -> escalates correctly
Plus integration with Governor (T054), Kill Switch hook (T068), Recovery (T055)
and Stuck (T061).
"""

from __future__ import annotations

from aios.autonomy_governor.contracts import (
    AutonomyAction,
    AutonomyDecision,
    AutonomyMode,
    AutonomyPolicy,
)
from aios.autonomy_governor.governor import ActionContext, AutonomyGovernor
from aios.autonomous_recovery.contracts import RecoveryStrategy
from aios.stuck_detection.contracts import StuckKind, StuckSeverity, StuckSignal

from aios.autonomy_safety import (
    AutonomyContext,
    AutonomyLevel,
    AutonomyLevelRegistry,
    BoundaryResult,
    EvaluationResult,
    LevelPolicy,
    SafeStopPolicy,
    SafeStopSignal,
    SafetyDecision,
    check_boundary,
    evaluate_action,
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _ctx(level=AutonomyLevel.L0, surfaces=("read",), escalate_on=(), evidence_ref=""):
    return AutonomyContext(
        level=level,
        allowed_surfaces=list(surfaces),
        escalate_on=list(escalate_on),
        evidence_ref=evidence_ref,
    )


# --------------------------------------------------------------------------
# AC1: every goal/loop has an autonomy level assigned + clear boundary
# --------------------------------------------------------------------------
def test_registry_assign_and_get_has_level_and_boundary():
    reg = AutonomyLevelRegistry()
    ctx = _ctx(level=AutonomyLevel.L2, surfaces=("read", "write"))
    reg.assign("goal-1", ctx)
    got = reg.get("goal-1")
    assert got is not None
    assert got.level == AutonomyLevel.L2
    # Boundary is explicit (non-empty allowed surfaces).
    assert got.allowed_surfaces == ["read", "write"]


# --------------------------------------------------------------------------
# Test Matrix: action in boundary -> ALLOW (Governor)
# --------------------------------------------------------------------------
def test_check_boundary_in_boundary_allows():
    res = check_boundary(_ctx(surfaces=("read",)), "read", target="ws:/proj/x")
    assert isinstance(res, BoundaryResult)
    assert res.decision == SafetyDecision.ALLOW
    assert res.governor_decision == AutonomyDecision.ALLOW


# --------------------------------------------------------------------------
# Test Matrix: action out of boundary -> BLOCK (Governor)
# --------------------------------------------------------------------------
def test_check_boundary_out_of_boundary_blocks():
    res = check_boundary(_ctx(surfaces=("read",)), "write", target="ws:/proj/x")
    assert res.decision == SafetyDecision.BLOCK
    # Governor is the authority that produced the block.
    assert res.governor_decision in (AutonomyDecision.BLOCK, AutonomyDecision.ASK)


def test_budget_exceeded_blocks():
    ctx = _ctx(surfaces=("read",))
    ctx.budget.max_cost = 1.0
    ctx.budget.consumed_cost = 2.0  # over budget -> out of boundary
    res = check_boundary(ctx, "read", target="ws:/proj/x")
    assert res.decision == SafetyDecision.BLOCK


# --------------------------------------------------------------------------
# Test Matrix: autonomy level raised without policy -> blocked
# --------------------------------------------------------------------------
def test_raise_level_without_policy_rejected():
    reg = AutonomyLevelRegistry()
    reg.assign("goal-2", _ctx(level=AutonomyLevel.L0, surfaces=("read",)))
    assert reg.raise_level("goal-2", AutonomyLevel.L1, policy=None) is False
    assert reg.get("goal-2").level == AutonomyLevel.L0  # unchanged


def test_raise_level_with_policy_succeeds():
    reg = AutonomyLevelRegistry()
    reg.assign("goal-3", _ctx(level=AutonomyLevel.L0, surfaces=("read",)))
    ok = reg.raise_level("goal-3", AutonomyLevel.L1, policy=LevelPolicy(justification="test"))
    assert ok is True
    assert reg.get("goal-3").level == AutonomyLevel.L1


def test_raise_level_requires_human_approval_for_l3_l4():
    reg = AutonomyLevelRegistry()
    reg.assign("goal-4", _ctx(level=AutonomyLevel.L2, surfaces=("read", "write")))
    # L3 requires human approval; without it -> rejected.
    assert reg.raise_level("goal-4", AutonomyLevel.L3, policy=LevelPolicy(justification="x")) is False
    # With human approval flag -> accepted.
    assert (
        reg.raise_level(
            "goal-4",
            AutonomyLevel.L3,
            policy=LevelPolicy(requires_human_approval=True, justification="x", approved_by="human"),
        )
        is True
    )
    assert reg.get("goal-4").level == AutonomyLevel.L3


# --------------------------------------------------------------------------
# Test Matrix: boundary violated -> SAFE_STOP (fail-closed)
# --------------------------------------------------------------------------
def test_boundary_violation_triggers_safe_stop():
    ss = SafeStopPolicy()
    result = evaluate_action(
        _ctx(surfaces=("read",)),
        "write",
        target="ws:/proj/x",
        goal="g",
        loop="l",
        safe_stop=ss,
    )
    assert isinstance(result, EvaluationResult)
    assert result.decision == SafetyDecision.SAFE_STOP
    assert result.signal is not None
    assert result.signal.violated_action == "write"
    assert result.signal.context_level == AutonomyLevel.L0.value
    assert ss.last_signal is result.signal


# --------------------------------------------------------------------------
# Test Matrix: same context + action -> same decision (deterministic)
# --------------------------------------------------------------------------
def test_deterministic_same_decision():
    ctx = _ctx(level=AutonomyLevel.L2, surfaces=("read", "write"), escalate_on=("high",))
    r1 = evaluate_action(ctx, "write", target="ws:/x")
    r2 = evaluate_action(ctx, "write", target="ws:/x")
    assert r1.decision == r2.decision
    assert r1.boundary.reason == r2.boundary.reason
    assert r1.risk_class == r2.risk_class


# --------------------------------------------------------------------------
# Test Matrix: escalate_on risk -> escalates correctly
# --------------------------------------------------------------------------
def test_escalate_on_risk_escalates():
    # "credential" scores HIGH risk in the Governor.
    ctx = _ctx(level=AutonomyLevel.L0, surfaces=("credential",), escalate_on=("high",))
    result = evaluate_action(ctx, "credential", target="ws:/x")
    assert result.decision == SafetyDecision.ESCALATE
    assert result.escalated is True
    assert result.risk_class == "high"


def test_escalate_on_not_matching_does_not_escalate():
    ctx = _ctx(level=AutonomyLevel.L0, surfaces=("read",), escalate_on=("high",))
    result = evaluate_action(ctx, "read", target="ws:/x")  # LOW risk
    assert result.decision == SafetyDecision.ALLOW
    assert result.escalated is False


# --------------------------------------------------------------------------
# AC6: integration with Governor (T054) — no parallel controller
# --------------------------------------------------------------------------
def test_boundary_delegates_to_governor():
    ctx = _ctx(level=AutonomyLevel.L0, surfaces=("read",))
    res = check_boundary(ctx, "read", target="ws:/x")
    # Replicate the Governor decision independently to prove delegation.
    g = AutonomyGovernor(
        policy=AutonomyPolicy(mode=AutonomyMode.SUPERVISED, actions={"read": "allow"}),
        allowed_scope={"capabilities": ["read"]},
    )
    gd = g.decide(ActionContext(action=AutonomyAction.READ, target="ws:/x"))
    assert res.governor_decision == gd


# --------------------------------------------------------------------------
# AC6: integration with Kill Switch (T068) hook
# --------------------------------------------------------------------------
def test_kill_switch_hook_invoked_on_safe_stop():
    calls = []

    def kill_switch(signal):
        calls.append(signal)

    ss = SafeStopPolicy(kill_switch=kill_switch)
    result = evaluate_action(
        _ctx(surfaces=("read",)), "write", target="ws:/x", safe_stop=ss
    )
    assert result.decision == SafetyDecision.SAFE_STOP
    assert len(calls) == 1
    assert calls[0] is result.signal


def test_safe_stop_fail_closed_when_kill_switch_raises():
    def kill_switch(signal):
        raise RuntimeError("kill switch down")

    ss = SafeStopPolicy(kill_switch=kill_switch)
    # Even if the hook fails, the stop stands and the signal is recorded.
    signal = ss.trigger(_ctx(surfaces=("read",)), "write", reason="boundary")
    assert isinstance(signal, SafeStopSignal)
    assert ss.last_signal is signal


# --------------------------------------------------------------------------
# AC6: integration with Recovery (T055) and Stuck (T061)
# --------------------------------------------------------------------------
def test_recovery_strategy_is_safe_stop():
    ss = SafeStopPolicy()
    assert ss.recovery_strategy() == RecoveryStrategy.SAFE_STOP


def test_safe_stop_from_stuck_signal():
    ss = SafeStopPolicy()
    stuck = StuckSignal(
        kind=StuckKind.OSCILLATION,
        severity=StuckSeverity.MAJOR,
        evidence_ref="evt-1",
    )
    signal = ss.from_stuck_signal(_ctx(surfaces=("read",)), stuck, goal="g")
    assert signal.reason.startswith("stuck_detected:oscillation")
    assert ss.last_signal is signal
