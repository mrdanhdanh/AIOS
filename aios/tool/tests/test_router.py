"""Tests for Capability Router — AC-014-05/06/07/08/11 (TASK-014)."""

import pytest

from aios.tool.contracts import CapabilityRequest, ResolutionStatus, ToolContract, ToolHealth
from aios.tool.registry import ToolRegistry
from aios.runtime.capability_router import CapabilityRouter, RouterError
from aios.runtime.permission import Permission, PermissionBroker, PermissionScope
from aios.runtime.policy import PolicyDecision, PolicyEngine, PolicyRequest, PolicyRule


def _tool(tool_id, caps=None, priority=0, health="healthy", enabled=True, tool_type="python"):
    return ToolContract.create(
        tool_id=tool_id,
        tool_type=tool_type,
        capabilities=caps or ["execute_code"],
        priority=priority,
        health=health,
        enabled=enabled,
    )


def _router_with_tools(tools, policy=None, cap_registry=None):
    reg = ToolRegistry()
    for t in tools:
        reg.register(t)
    return CapabilityRouter(tool_registry=reg, capability_registry=cap_registry, policy_engine=policy), reg


# -- Basic resolution --

def test_router_single_tool_resolved():
    router, _ = _router_with_tools([_tool("python.local")])
    req = CapabilityRequest.create(capability="execute_code")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "python.local"
    assert res.is_resolved is True
    assert res.evidence_ref.startswith("ev-")
    assert res.request_id == req.request_id


def test_router_multi_tool_selects_highest_priority():
    router, _ = _router_with_tools([
        _tool("python.local", priority=10),
        _tool("python.sandbox", priority=90),
        _tool("docker.python", priority=50, tool_type="docker"),
    ])
    req = CapabilityRequest.create(capability="execute_code")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "python.sandbox"  # 90 highest
    assert res.reason.priority == 90
    assert res.reason.health == "healthy"
    assert res.reason.policy == "allow"


def test_router_priority_deterministic_tie_break():
    # Same priority → seq asc → tool_id asc
    router, _ = _router_with_tools([
        _tool("tool-b", priority=10),
        _tool("tool-a", priority=10),
    ])
    req = CapabilityRequest.create(capability="execute_code")
    res = router.resolve(req)
    # tool-a registered second but tool_id asc tie-break after seq?
    # Our sort: priority desc, seq asc, tool_id asc
    # tool-b seq=1, tool-a seq=2 → tool-b wins despite tool_id
    assert res.selected_tool == "tool-b"


# -- Health-aware (AC-014-05) --

def test_router_health_healthy_eligible():
    router, _ = _router_with_tools([_tool("tool-a", health="healthy")])
    res = router.resolve(CapabilityRequest.create(capability="execute_code"))
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "tool-a"


def test_router_health_degraded_eligible():
    router, _ = _router_with_tools([_tool("tool-a", health="degraded")])
    res = router.resolve(CapabilityRequest.create(capability="execute_code"))
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "tool-a"
    assert res.reason.health == "degraded"


def test_router_health_unhealthy_reject():
    router, _ = _router_with_tools([_tool("tool-a", health="unhealthy")])
    res = router.resolve(CapabilityRequest.create(capability="execute_code"))
    assert res.status == ResolutionStatus.UNRESOLVED
    assert res.selected_tool is None


def test_router_health_disabled_reject():
    router, _ = _router_with_tools([_tool("tool-a", health="disabled")])
    res = router.resolve(CapabilityRequest.create(capability="execute_code"))
    assert res.status == ResolutionStatus.UNRESOLVED


def test_router_health_unknown_reject_fail_closed():
    router, _ = _router_with_tools([_tool("tool-a", health="unknown")])
    res = router.resolve(CapabilityRequest.create(capability="execute_code"))
    assert res.status == ResolutionStatus.UNRESOLVED
    # UNKNOWN must never be promoted to healthy
    assert res.selected_tool is None


def test_router_health_disabled_tool_reject():
    router, _ = _router_with_tools([_tool("tool-a", enabled=False)])
    res = router.resolve(CapabilityRequest.create(capability="execute_code"))
    assert res.status == ResolutionStatus.UNRESOLVED


def test_router_health_filter_with_multiple():
    router, _ = _router_with_tools([
        _tool("tool-healthy", priority=10, health="healthy"),
        _tool("tool-unhealthy", priority=100, health="unhealthy"),
        _tool("tool-disabled", priority=90, health="disabled"),
        _tool("tool-unknown", priority=80, health="unknown"),
        _tool("tool-degraded", priority=5, health="degraded"),
    ])
    res = router.resolve(CapabilityRequest.create(capability="execute_code"))
    # Only healthy and degraded are eligible; healthy priority 10 > degraded 5
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "tool-healthy"


def test_router_all_unhealthy_unresolved():
    router, _ = _router_with_tools([
        _tool("tool-a", health="unhealthy"),
        _tool("tool-b", health="disabled"),
    ])
    res = router.resolve(CapabilityRequest.create(capability="execute_code"))
    assert res.status == ResolutionStatus.UNRESOLVED
    assert "no eligible" in res.reason.detail.lower() or "no eligible" in res.metadata.get("error", "").lower()


# -- Priority-aware (AC-014-06) --

def test_router_priority_higher_wins():
    router, _ = _router_with_tools([
        _tool("tool-low", priority=10),
        _tool("tool-high", priority=100),
    ])
    res = router.resolve(CapabilityRequest.create(capability="execute_code"))
    assert res.selected_tool == "tool-high"


def test_router_priority_not_override_health():
    # High priority but unhealthy should not be selected
    router, _ = _router_with_tools([
        _tool("tool-high-unhealthy", priority=100, health="unhealthy"),
        _tool("tool-low-healthy", priority=10, health="healthy"),
    ])
    res = router.resolve(CapabilityRequest.create(capability="execute_code"))
    assert res.selected_tool == "tool-low-healthy"


# -- Policy-aware (AC-014-07) --

def test_router_policy_allow():
    broker = PermissionBroker()
    broker.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    policy = PolicyEngine(broker=broker)
    policy.add_rule(PolicyRule("allow-all", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
    router, _ = _router_with_tools([_tool("tool-a")], policy=policy)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.reason.policy == "allow"


def test_router_policy_deny():
    broker = PermissionBroker()
    # No grant → DENY at permission gate
    policy = PolicyEngine(broker=broker)
    policy.add_rule(PolicyRule("allow-all", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
    router, _ = _router_with_tools([_tool("tool-a")], policy=policy)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED
    assert res.reason.policy == "deny"


def test_router_policy_deny_high_priority_skip_to_next():
    broker = PermissionBroker()
    broker.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    policy = PolicyEngine(broker=broker)
    # Deny tool-high, allow tool-low
    def deny_high(req):
        return req.metadata.get("tool_id") == "tool-high"
    policy.add_rule(PolicyRule("deny-high", applies=deny_high, decision=PolicyDecision.DENY, reason="deny high"))
    policy.add_rule(PolicyRule("allow-rest", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
    router, _ = _router_with_tools([
        _tool("tool-high", priority=100),
        _tool("tool-low", priority=10),
    ], policy=policy)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "tool-low"


def test_router_policy_priority_not_override_deny():
    # High priority but policy DENY → must not be selected, even if priority high
    broker = PermissionBroker()
    broker.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    policy = PolicyEngine(broker=broker)
    policy.add_rule(PolicyRule("deny-all", applies=lambda r: True, decision=PolicyDecision.DENY, reason="deny"))
    router, _ = _router_with_tools([
        _tool("tool-high", priority=100),
        _tool("tool-low", priority=10),
    ], policy=policy)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED
    assert res.reason.policy == "deny"


def test_router_policy_ask():
    broker = PermissionBroker()
    broker.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    policy = PolicyEngine(broker=broker)
    # No decisive rule → INSUFFICIENT → ASK
    router, _ = _router_with_tools([_tool("tool-a")], policy=policy)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED
    assert res.reason.policy == "ask"
    assert res.metadata.get("ask") is True


def test_router_policy_ask_does_not_execute():
    # ASK should not auto-execute, just return UNRESOLVED
    broker = PermissionBroker()
    broker.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    policy = PolicyEngine(broker=broker)
    router, _ = _router_with_tools([_tool("tool-a")], policy=policy)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED
    assert res.selected_tool is None


# -- Fail-closed (AC-014-08) --

def test_router_capability_not_exist_unresolved():
    router, _ = _router_with_tools([_tool("tool-a", caps=["execute_code"])])
    req = CapabilityRequest.create(capability="nonexistent_cap")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED
    assert res.selected_tool is None


def test_router_no_tool_provides_capability():
    reg = ToolRegistry()
    reg.register(_tool("tool-a", caps=["execute_code"]))
    router = CapabilityRouter(tool_registry=reg)
    req = CapabilityRequest.create(capability="http_request")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED


def test_router_invalid_request_reject():
    router, _ = _router_with_tools([_tool("tool-a")])
    with pytest.raises(RouterError):
        router.resolve("not-a-request")  # type: ignore


def test_router_resolve_or_raise():
    router, _ = _router_with_tools([_tool("tool-a")])
    req = CapabilityRequest.create(capability="execute_code")
    res = router.resolve_or_raise(req)
    assert res.is_resolved is True
    # Unresolved should raise
    req2 = CapabilityRequest.create(capability="nonexistent")
    with pytest.raises(RouterError):
        router.resolve_or_raise(req2)


# -- Constraints --

def test_router_constraints_tool_type():
    router, _ = _router_with_tools([
        _tool("python.local", tool_type="python", caps=["execute_code"]),
        _tool("docker.python", tool_type="docker", caps=["execute_code"]),
    ])
    # Request with tool_type=docker should only match docker
    req = CapabilityRequest.create(capability="execute_code", constraints={"tool_type": "docker"})
    res = router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "docker.python"


def test_router_constraints_sandbox_required():
    router, _ = _router_with_tools([
        _tool("python.local", tool_type="python", caps=["execute_code"]),
        _tool("python.sandbox", tool_type="python", caps=["execute_code"]),
    ])
    req = CapabilityRequest.create(capability="execute_code", constraints={"sandbox": "required"})
    res = router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "python.sandbox"


def test_router_constraints_network_deny():
    # Tool with network permission should be rejected when network=deny
    t_net = ToolContract.create("rest.api", tool_type="rest", capabilities=["http_request"], permissions=["network.read"])
    t_local = ToolContract.create("python.local", tool_type="python", capabilities=["http_request"])
    router, _ = _router_with_tools([t_net, t_local])
    req = CapabilityRequest.create(capability="http_request", constraints={"network": "deny"})
    res = router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "python.local"


def test_router_constraints_no_match_unresolved():
    router, _ = _router_with_tools([_tool("python.local", tool_type="python")])
    req = CapabilityRequest.create(capability="execute_code", constraints={"tool_type": "docker"})
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED


# -- Evidence (AC-014-11) --

def test_router_evidence_includes_candidates_and_reason():
    router, _ = _router_with_tools([
        _tool("tool-a", priority=10),
        _tool("tool-b", priority=5),
    ])
    req = CapabilityRequest.create(capability="execute_code")
    res = router.resolve(req)
    assert res.evidence_ref.startswith("ev-")
    assert len(res.candidates) == 2
    assert res.reason.health in ("healthy", "degraded")
    assert res.reason.priority in (10, 5)
    assert res.reason.policy in ("allow", "deny", "ask")
    d = res.to_dict()
    assert "evidence_ref" in d
    assert "candidates" in d
    assert "reason" in d


def test_router_evidence_unresolved_has_reason():
    router, _ = _router_with_tools([_tool("tool-a", health="unhealthy")])
    req = CapabilityRequest.create(capability="execute_code")
    res = router.resolve(req)
    assert res.evidence_ref.startswith("ev-")
    assert res.reason.detail != ""
    assert len(res.candidates) >= 1


# -- Offline (AC-014-10) --

def test_router_offline_no_policy():
    # Without policy engine, router should still work offline
    router, _ = _router_with_tools([_tool("tool-a")], policy=None)
    req = CapabilityRequest.create(capability="execute_code")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "tool-a"


def test_router_offline_mock_tools():
    from aios.tool.adapters import create_mock_tool
    reg = ToolRegistry()
    for tid, ttype in [("python.local", "python"), ("docker.python", "docker"), ("rest.api", "rest")]:
        contract, _ = create_mock_tool(tid, tool_type=ttype, capabilities=["execute_code"])
        reg.register(contract)
    router = CapabilityRouter(tool_registry=reg)
    req = CapabilityRequest.create(capability="execute_code")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool in ("python.local", "docker.python", "rest.api")


# -- Fallback only after policy check --

def test_router_fallback_only_after_policy():
    broker = PermissionBroker()
    broker.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    policy = PolicyEngine(broker=broker)
    # First tool denied, second allowed → fallback is policy-gated
    policy.add_rule(PolicyRule("deny-first", applies=lambda r: r.metadata.get("tool_id") == "tool-a", decision=PolicyDecision.DENY, reason="deny a"))
    policy.add_rule(PolicyRule("allow-rest", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
    router, _ = _router_with_tools([
        _tool("tool-a", priority=100),
        _tool("tool-b", priority=10),
    ], policy=policy)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.selected_tool == "tool-b"
    # Verify candidates show tool-a was denied
    assert any(c.tool_id == "tool-a" for c in res.candidates)


def test_router_no_bypass_policy():
    # Even if tool is healthy and high priority, policy DENY must block it
    broker = PermissionBroker()
    broker.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    policy = PolicyEngine(broker=broker)
    policy.add_rule(PolicyRule("deny-all", applies=lambda r: True, decision=PolicyDecision.DENY, reason="deny"))
    router, _ = _router_with_tools([_tool("tool-a", priority=100)], policy=policy)
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED
    # Must not have selected tool despite high priority
    assert res.selected_tool is None
