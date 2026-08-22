"""Integration tests for Kill Switch (TASK-068).

Verifies integration with Autonomy Governor (T054) and the optional
Autonomy Safety (T067) / Durable (T066) bridges (which fall back locally in
this workspace).
"""

from __future__ import annotations

from aios.autonomy_governor.contracts import (
    AutonomyAction,
    AutonomyDecision,
    AutonomyMode,
    AutonomyPolicy,
)
from aios.autonomy_governor.governor import ActionContext, AutonomyGovernor

from aios.kill_switch.controller import KillSwitchController
from aios.kill_switch.integration import (
    GovernorHaltBridge,
    build_durable_persistence,
    build_safety_bridge,
)
from aios.kill_switch.tests.conftest import FakeContext, make_signal
from aios.kill_switch.contracts import HaltScope, HaltSource


def _governor() -> AutonomyGovernor:
    return AutonomyGovernor(policy=AutonomyPolicy(mode=AutonomyMode.AUTONOMOUS))


def _read_ctx() -> ActionContext:
    return ActionContext(action=AutonomyAction.READ, target="file.txt")


def test_governor_bridge_delegates_when_not_halted():
    c = KillSwitchController()
    gov = _governor()
    bridge = GovernorHaltBridge(c, gov)
    ctx = _read_ctx()
    # when not halted, the bridge delegates to the governor (no forced BLOCK)
    assert bridge.gate(ctx) == gov.decide(ctx)
    assert bridge.gate(ctx) != AutonomyDecision.BLOCK


def test_governor_bridge_allows_configured_action_when_not_halted():
    policy = AutonomyPolicy(mode=AutonomyMode.AUTONOMOUS, actions={"read": "allow"})
    gov = AutonomyGovernor(policy=policy)
    c = KillSwitchController()
    bridge = GovernorHaltBridge(c, gov)
    assert bridge.gate(_read_ctx()) == AutonomyDecision.ALLOW


def test_governor_bridge_blocks_fail_closed_when_halted():
    c = KillSwitchController()
    c.register(FakeContext("loop-1", "loop"))
    c.issue(make_signal(HaltSource.MANUAL, HaltScope.GLOBAL, "stop"))
    bridge = GovernorHaltBridge(c, _governor())
    # halt overrides the governor -> BLOCK regardless of policy
    assert bridge.gate(_read_ctx()) == AutonomyDecision.BLOCK
    assert bridge.gate_scoped(_read_ctx(), HaltScope.GLOBAL) == AutonomyDecision.BLOCK


def test_build_durable_persistence_falls_back_locally():
    # T066 durable is not present in this workspace -> local fallback
    p = build_durable_persistence()
    assert p.persist("x", {"a": 1}) == ["x"]
    assert p.get_state("x") == {"a": 1}


def test_build_safety_bridge_falls_back_to_stub():
    c = KillSwitchController()
    c.register(FakeContext("loop-1", "loop"))
    stub = build_safety_bridge(c)
    # not halted yet -> not "safe" per stub semantics (system still running)
    assert stub.is_safe() is False
    c.issue(make_signal(HaltSource.SAFETY, HaltScope.GLOBAL, "stop"))
    # halted -> safe (stopped) state
    assert stub.is_safe() is True
