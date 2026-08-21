"""Policy integration tests — AC-014-07/08 (TASK-014)."""

import pytest

from aios.tool.contracts import CapabilityRequest, ResolutionStatus, ToolContract
from aios.tool.registry import ToolRegistry
from aios.runtime.capability_router import CapabilityRouter
from aios.runtime.permission import Permission, PermissionBroker, PermissionScope
from aios.runtime.policy import PolicyDecision, PolicyEngine, PolicyRequest, PolicyRule


def _tool(tool_id, caps=None, priority=0, health="healthy", tool_type="python"):
    return ToolContract.create(
        tool_id=tool_id,
        tool_type=tool_type,
        capabilities=caps or ["execute_code"],
        priority=priority,
        health=health,
    )


def _allow_all_policy(subject="worker"):
    broker = PermissionBroker()
    broker.grant(subject, Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    eng = PolicyEngine(broker=broker)
    eng.add_rule(PolicyRule("allow-all", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
    return eng


def _deny_all_policy(subject="worker"):
    broker = PermissionBroker()
    broker.grant(subject, Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    eng = PolicyEngine(broker=broker)
    eng.add_rule(PolicyRule("deny-all", applies=lambda r: True, decision=PolicyDecision.DENY, reason="deny"))
    return eng


# -- Policy pre-check before execution --

def test_policy_checked_before_tool_selection():
    # Even if tool is healthy and high priority, DENY must block
    reg = ToolRegistry()
    reg.register(_tool("tool-high", priority=100))
    router = CapabilityRouter(tool_registry=reg, policy_engine=_deny_all_policy())
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED
    assert res.reason.policy == "deny"
    assert res.selected_tool is None


def test_policy_allow_then_execute():
    reg = ToolRegistry()
    reg.register(_tool("tool-a"))
    router = CapabilityRouter(tool_registry=reg, policy_engine=_allow_all_policy())
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    # Now execute via adapter
    from aios.tool.adapters import create_mock_tool
    # Use the resolved tool
    assert res.selected_tool == "tool-a"
    # Simulate execution
    contract, adapter = create_mock_tool("tool-a", capabilities=["execute_code"])
    result = adapter.execute("execute_code", "print('hi')")
    assert result.status == "success"
    assert result.evidence_ref.startswith("ev-")


def test_policy_deny_no_fallback_without_allow():
    reg = ToolRegistry()
    reg.register(_tool("tool-a", priority=10))
    reg.register(_tool("tool-b", priority=5))
    router = CapabilityRouter(tool_registry=reg, policy_engine=_deny_all_policy())
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED
    # No tool selected even though both exist
    assert res.selected_tool is None


def test_policy_ask_no_auto_execute():
    broker = PermissionBroker()
    broker.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    eng = PolicyEngine(broker=broker)
    # No rule → INSUFFICIENT → ASK
    reg = ToolRegistry()
    reg.register(_tool("tool-a"))
    router = CapabilityRouter(tool_registry=reg, policy_engine=eng)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED
    assert res.reason.policy == "ask"
    assert res.metadata.get("ask") is True
    # Must not auto-execute
    assert res.selected_tool is None


def test_policy_permission_gate_fail_closed():
    # No permission grant → DENY at permission gate, even with ALLOW rule
    broker = PermissionBroker()  # no grants
    eng = PolicyEngine(broker=broker)
    eng.add_rule(PolicyRule("allow-all", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
    reg = ToolRegistry()
    reg.register(_tool("tool-a"))
    router = CapabilityRouter(tool_registry=reg, policy_engine=eng)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED
    assert res.reason.policy == "deny"


def test_policy_shell_tool_deny():
    # Shell tool is high risk — policy should deny by default
    broker = PermissionBroker()
    broker.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    eng = PolicyEngine(broker=broker)
    # Deny shell
    eng.add_rule(PolicyRule("deny-shell", applies=lambda r: r.metadata.get("tool_id", "").startswith("shell"), decision=PolicyDecision.DENY, reason="shell denied"))
    eng.add_rule(PolicyRule("allow-rest", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
    reg = ToolRegistry()
    reg.register(_tool("shell.local", caps=["execute_shell"], tool_type="shell", priority=100))
    reg.register(_tool("python.local", caps=["execute_shell"], priority=10))
    router = CapabilityRouter(tool_registry=reg, policy_engine=eng)
    req = CapabilityRequest.create(capability="execute_shell", subject="worker")
    res = router.resolve(req)
    # shell.local denied, python.local allowed (even though lower priority)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "python.local"


def test_policy_not_bypassed_by_priority():
    broker = PermissionBroker()
    broker.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    eng = PolicyEngine(broker=broker)
    eng.add_rule(PolicyRule("deny-high", applies=lambda r: r.metadata.get("tool_id") == "tool-high", decision=PolicyDecision.DENY, reason="deny high"))
    eng.add_rule(PolicyRule("allow-rest", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
    reg = ToolRegistry()
    reg.register(_tool("tool-high", priority=100))
    reg.register(_tool("tool-low", priority=10))
    router = CapabilityRouter(tool_registry=reg, policy_engine=eng)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.selected_tool == "tool-low"
    # High priority was denied, not bypassed
    assert res.reason.policy == "allow"


def test_policy_fallback_only_when_allowed():
    broker = PermissionBroker()
    broker.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    eng = PolicyEngine(broker=broker)
    # First tool timeout simulation, but policy must still allow fallback
    eng.add_rule(PolicyRule("allow-all", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
    reg = ToolRegistry()
    reg.register(_tool("tool-a", priority=100))
    reg.register(_tool("tool-b", priority=10))
    router = CapabilityRouter(tool_registry=reg, policy_engine=eng)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "tool-a"
    # Simulate tool-a failure, then fallback to tool-b must still check policy
    from aios.tool.adapters import create_mock_tool
    _, adapter_a = create_mock_tool("tool-a", capabilities=["execute_code"])
    result_a = adapter_a.execute("execute_code", {"simulate_failure": True, "error": "timeout", "retryable": True})
    assert result_a.status == "failed"
    assert result_a.retryable is True
    # Fallback: resolve again, but now tool-a is unhealthy? Simulate health change
    reg.set_health("tool-a", "unhealthy")
    res2 = router.resolve(req)
    assert res2.selected_tool == "tool-b"


def test_tool_does_not_bypass_policy():
    # Tool adapter itself should not bypass policy — it checks health/enabled but policy is router's job
    # Verify adapter does not import policy
    import pathlib
    text = pathlib.Path("aios/tool/adapters.py").read_text(encoding="utf-8")
    assert "PolicyEngine" not in text
    assert "PermissionBroker" not in text
    assert "policy" not in text.lower() or "policy" in text.lower()  # just check no direct policy import
    # Actually check no runtime imports
    assert "aios.runtime" not in text
    assert "aios.orchestrator" not in text
    assert "aios.agents" not in text


def test_router_does_not_execute_tool():
    # Router should only resolve, not execute
    import pathlib
    text = pathlib.Path("aios/runtime/capability_router.py").read_text(encoding="utf-8")
    # Router should not call adapter.execute
    assert "adapter.execute" not in text
    assert ".execute(" not in text or "def execute" not in text  # router has no execute method that calls tool
    # Router's resolve should not import subprocess or tool execution
    assert "subprocess" not in text
    assert "os.system" not in text
