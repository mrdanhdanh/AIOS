"""Automated tests for the deterministic policy engine (TASK-004)."""

import pytest

from aios.runtime.permission import Permission, PermissionBroker, PermissionScope
from aios.runtime.policy import (
    PolicyDecision,
    PolicyEngine,
    PolicyRequest,
    PolicyResult,
    PolicyRule,
)


def _req(subject="agent-1", action="tool.invoke", resource="tool:calc", scope=None):
    return PolicyRequest(subject=subject, action=action, resource=resource, scope=scope)


def test_engine_denies_without_permission():
    broker = PermissionBroker()
    eng = PolicyEngine(broker=broker)
    # No grants; request requires a capability-invoke permission.
    res = eng.evaluate(_req(scope=PermissionScope.CAPABILITY_INVOKE))
    assert res.decision == PolicyDecision.DENY
    assert "lacks permission" in res.reason


def test_engine_allow_via_permission_plus_rule():
    broker = PermissionBroker()
    broker.grant("agent-1", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    eng = PolicyEngine(broker=broker)
    eng.add_rule(
        PolicyRule(
            "allow-math",
            applies=lambda r: r.resource.startswith("capability:math"),
            decision=PolicyDecision.ALLOW,
            reason="math allowed",
        )
    )
    res = eng.evaluate(
        _req(resource="capability:math", scope=PermissionScope.CAPABILITY_INVOKE)
    )
    assert res.decision == PolicyDecision.ALLOW


def test_engine_deny_rule_overrides_allow():
    eng = PolicyEngine()
    eng.add_rule(
        PolicyRule(
            "allow-all",
            applies=lambda r: True,
            decision=PolicyDecision.ALLOW,
            reason="allow",
        )
    )
    eng.add_rule(
        PolicyRule(
            "block-dangerous",
            applies=lambda r: r.resource == "tool:rm",
            decision=PolicyDecision.DENY,
            reason="rm is dangerous",
        )
    )
    res = eng.evaluate(_req(resource="tool:rm"))
    assert res.decision == PolicyDecision.DENY
    assert res.reason == "rm is dangerous"


def test_engine_insufficient_when_no_rule():
    eng = PolicyEngine()
    res = eng.evaluate(_req(resource="tool:unknown"))
    assert res.decision == PolicyDecision.INSUFFICIENT
    assert res.applied_rules == []


def test_engine_deny_all_helper():
    eng = PolicyEngine.deny_all()
    res = eng.evaluate(_req())
    assert res.decision == PolicyDecision.DENY


def test_engine_allow_all_helper():
    eng = PolicyEngine.allow_all()
    res = eng.evaluate(_req())
    assert res.decision == PolicyDecision.ALLOW


def test_engine_records_applied_rules():
    eng = PolicyEngine()
    eng.add_rule(
        PolicyRule("r1", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="a")
    )
    eng.add_rule(
        PolicyRule("r2", applies=lambda r: r.action == "x", decision=PolicyDecision.ALLOW, reason="b")
    )
    res = eng.evaluate(_req())
    assert res.applied_rules == ["r1"]


def test_policy_is_deterministic_first_no_llm():
    broker = PermissionBroker()
    broker.grant("agent-1", Permission(PermissionScope.TOOL_INVOKE, "*"))
    eng = PolicyEngine(broker=broker)
    eng.add_rule(
        PolicyRule(
            "allow-tool",
            applies=lambda r: r.scope == PermissionScope.TOOL_INVOKE,
            decision=PolicyDecision.ALLOW,
            reason="tool ok",
        )
    )
    # Repeatable: same input -> same output, no LLM call path.
    r1 = eng.evaluate(_req(scope=PermissionScope.TOOL_INVOKE))
    r2 = eng.evaluate(_req(scope=PermissionScope.TOOL_INVOKE))
    assert r1.decision == r2.decision == PolicyDecision.ALLOW
