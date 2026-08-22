"""Tests for TASK-054 Autonomy Governor."""
from __future__ import annotations

from aios.autonomy_governor.contracts import (
    ApprovalRequest,
    AutonomyAction,
    AutonomyBudget,
    AutonomyDecision,
    AutonomyMode,
    AutonomyPolicy,
    AutonomyRisk,
)
from aios.autonomy_governor.governor import ActionContext, AutonomyGovernor


def _gov(mode=AutonomyMode.SUPERVISED, actions=None, scope=None):
    policy = AutonomyPolicy(mode=mode, actions=actions or {"read": "allow", "write": "ask", "execute": "ask"})
    return AutonomyGovernor(policy=policy, allowed_scope=scope or {"targets": ["ws:/proj"]})


def test_read_allowed():
    g = _gov()
    d = g.decide(ActionContext(action=AutonomyAction.READ, target="ws:/proj/x"))
    assert d == AutonomyDecision.ALLOW


def test_write_requires_approval():
    g = _gov()
    d = g.decide(ActionContext(action=AutonomyAction.WRITE, target="ws:/proj/x"))
    assert d == AutonomyDecision.ASK


def test_write_with_valid_approval_allowed():
    g = _gov()
    ap = ApprovalRequest(action="write", target="ws:/proj/x", risk=AutonomyRisk.MEDIUM)
    d = g.decide(ActionContext(action=AutonomyAction.WRITE, target="ws:/proj/x", approval=ap))
    assert d == AutonomyDecision.ALLOW


def test_scope_violation_blocked():
    g = _gov()
    d = g.decide(ActionContext(action=AutonomyAction.READ, target="external:/other"))
    assert d == AutonomyDecision.BLOCK


def test_disabled_mode_blocks_all():
    g = _gov(mode=AutonomyMode.DISABLED)
    d = g.decide(ActionContext(action=AutonomyAction.READ, target="ws:/proj/x"))
    assert d == AutonomyDecision.BLOCK


def test_budget_exceeded_blocks():
    budget = AutonomyBudget(max_steps=1, steps=2)
    g = AutonomyGovernor(policy=AutonomyPolicy(mode=AutonomyMode.AUTONOMOUS, actions={"read": "allow"}),
                         budget=budget, allowed_scope={"targets": ["ws:/proj"]})
    d = g.decide(ActionContext(action=AutonomyAction.READ, target="ws:/proj/x"))
    assert d == AutonomyDecision.BLOCK


def test_critical_action_asks_without_approval():
    g = _gov(mode=AutonomyMode.BOUNDED, actions={"destructive": "ask"})
    d = g.decide(ActionContext(action=AutonomyAction.DESTRUCTIVE, target="ws:/proj/x", reversible=False))
    assert d == AutonomyDecision.ASK


def test_critical_with_approval_allowed():
    g = _gov(mode=AutonomyMode.BOUNDED, actions={"destructive": "ask"})
    ap = ApprovalRequest(action="destructive", target="ws:/proj/x", risk=AutonomyRisk.CRITICAL)
    d = g.decide(ActionContext(action=AutonomyAction.DESTRUCTIVE, target="ws:/proj/x", reversible=False, approval=ap))
    assert d == AutonomyDecision.ALLOW


def test_unknown_action_treated_critical():
    g = _gov()
    a = g.classify_action("something_unknown")
    assert a == AutonomyAction.DESTRUCTIVE


def test_risk_scoring_levels():
    g = _gov()
    lvl, score = g.score_risk(ActionContext(action=AutonomyAction.READ))
    assert lvl == AutonomyRisk.LOW
    lvl2, _ = g.score_risk(ActionContext(action=AutonomyAction.DESTRUCTIVE, reversible=False, privilege_required=True))
    assert lvl2 == AutonomyRisk.CRITICAL


def test_approval_expiry_and_reuse():
    ap = ApprovalRequest(action="write", target="ws:/proj/x")
    import time
    ap.expires_at = time.time() - 1
    assert not ap.is_valid()
    ap2 = ApprovalRequest(action="write", target="ws:/proj/x")
    ap2.used = True
    assert not ap2.is_valid()
