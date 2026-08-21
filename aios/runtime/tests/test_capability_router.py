"""Tests for CapabilityRouter via RuntimeKernel wiring (TASK-014)."""

import pytest

from aios.core.container import Container
from aios.runtime.kernel import RuntimeKernel
from aios.tool.contracts import CapabilityRequest, ResolutionStatus, ToolContract
from aios.tool.registry import ToolRegistry
from aios.runtime.capability_router import CapabilityRouter
from aios.runtime.permission import Permission, PermissionScope
from aios.runtime.policy import PolicyDecision, PolicyEngine, PolicyRule


def test_kernel_wires_tool_registry_and_router():
    k = RuntimeKernel()
    assert k.tools is k.tools  # singleton
    assert k.router is k.router
    assert isinstance(k.tools, ToolRegistry)
    assert isinstance(k.router, CapabilityRouter)


def test_kernel_health_includes_tools():
    k = RuntimeKernel()
    h = k.health()
    assert "tools" in h
    assert h["tools"] == 0


def test_kernel_tools_isolated_per_container():
    k1 = RuntimeKernel()
    k2 = RuntimeKernel(container=Container())
    k1.tools.register(ToolContract.create("tool-isolated", tool_type="python", capabilities=["execute_code"]))
    assert len(k1.tools) == 1
    assert len(k2.tools) == 0


def test_kernel_router_uses_shared_policy():
    k = RuntimeKernel()
    # Register a tool
    k.tools.register(ToolContract.create("python.local", tool_type="python", capabilities=["execute_code"], priority=10))
    # Grant permission and allow policy
    k.permissions.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    k.policy.add_rule(PolicyRule("allow-all", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = k.router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool == "python.local"


def test_kernel_router_policy_deny():
    k = RuntimeKernel()
    k.tools.register(ToolContract.create("tool-a", tool_type="python", capabilities=["execute_code"]))
    # No grant → DENY
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = k.router.resolve(req)
    assert res.status == ResolutionStatus.UNRESOLVED


def test_kernel_full_health_after_population():
    k = RuntimeKernel()
    k.tools.register(ToolContract.create("python.local", tool_type="python", capabilities=["execute_code"]))
    k.tools.register(ToolContract.create("shell.local", tool_type="shell", capabilities=["execute_shell"]))
    h = k.health()
    assert h["tools"] == 2


def test_router_via_kernel_with_mock_adapters():
    from aios.tool.adapters import create_mock_tool
    k = RuntimeKernel()
    for tid, ttype in [("python.local", "python"), ("docker.python", "docker")]:
        contract, _ = create_mock_tool(tid, tool_type=ttype, capabilities=["execute_code"])
        k.tools.register(contract)
    k.permissions.grant("worker", Permission(PermissionScope.CAPABILITY_INVOKE, "*"))
    k.policy.add_rule(PolicyRule("allow-all", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
    req = CapabilityRequest.create(capability="execute_code", subject="worker")
    res = k.router.resolve(req)
    assert res.status == ResolutionStatus.RESOLVED
    assert res.selected_tool in ("python.local", "docker.python")
