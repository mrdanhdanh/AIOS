"""Tests for Tool Contract — AC-014-01/02/11 (TASK-014)."""

import pytest

from aios.tool.contracts import (
    TOOL_CONTRACT,
    CapabilityRequest,
    CapabilityResolution,
    ResolutionReason,
    ResolutionStatus,
    ToolCapabilityDeclarationError,
    ToolContract,
    ToolError,
    ToolHealth,
    ToolResult,
    ToolType,
    check_tool_contracts,
)
from aios.core.contracts import ContractError


# -- ToolType / ToolHealth --

def test_tool_type_all():
    assert set(ToolType.all()) == {ToolType.PYTHON, ToolType.DOCKER, ToolType.REST, ToolType.MCP, ToolType.SHELL, ToolType.GIT}
    for t in ToolType.all():
        assert ToolType(t.value) == t


def test_tool_health_all_and_eligible():
    assert set(ToolHealth.all()) == {ToolHealth.UNKNOWN, ToolHealth.HEALTHY, ToolHealth.DEGRADED, ToolHealth.UNHEALTHY, ToolHealth.DISABLED}
    assert ToolHealth.HEALTHY.is_eligible() is True
    assert ToolHealth.DEGRADED.is_eligible() is True
    assert ToolHealth.UNHEALTHY.is_eligible() is False
    assert ToolHealth.DISABLED.is_eligible() is False
    assert ToolHealth.UNKNOWN.is_eligible() is False


def test_tool_health_unknown_not_promoted():
    # UNKNOWN must never be considered healthy
    assert not ToolHealth.UNKNOWN.is_eligible()
    # String conversion
    assert ToolHealth("unknown") == ToolHealth.UNKNOWN
    assert ToolHealth("healthy") == ToolHealth.HEALTHY


# -- ToolContract --

def test_tool_contract_create_minimal():
    c = ToolContract.create("python.local", tool_type="python", capabilities=["execute_code"])
    assert c.tool_id == "python.local"
    assert c.version == "1.0.0"
    assert c.tool_type == ToolType.PYTHON
    assert c.health == ToolHealth.HEALTHY
    assert c.enabled is True
    c.validate()


def test_tool_contract_all_types():
    for t in ToolType.all():
        c = ToolContract.create(f"tool-{t.value}", tool_type=t, capabilities=["execute_code"])
        assert c.tool_type == t


def test_tool_contract_invalid_id():
    with pytest.raises(ToolError):
        ToolContract.create("", tool_type="python")
    with pytest.raises(ToolError):
        ToolContract.create("bad id!", tool_type="python")


def test_tool_contract_invalid_version():
    with pytest.raises(ToolError):
        ToolContract.create("tool-a", version="not-semver", tool_type="python")


def test_tool_contract_invalid_tool_type():
    with pytest.raises(ToolError):
        ToolContract.create("tool-a", tool_type="invalid_type")


def test_tool_contract_invalid_capability():
    with pytest.raises(ToolCapabilityDeclarationError):
        ToolContract.create("tool-a", tool_type="python", capabilities=["bad-capability!"])
    with pytest.raises(ToolCapabilityDeclarationError):
        ToolContract.create("tool-a", tool_type="python", capabilities=[""])
    with pytest.raises(ToolCapabilityDeclarationError):
        ToolContract.create("tool-a", tool_type="python", capabilities=["123bad"])


def test_tool_contract_multiple_capabilities():
    c = ToolContract.create("tool-multi", tool_type="python", capabilities=["execute_code", "run_python", "run_tests"])
    assert len(c.capabilities) == 3
    assert "execute_code" in c.capabilities
    assert "run_python" in c.capabilities


def test_tool_contract_invalid_permission():
    with pytest.raises(ToolError):
        ToolContract.create("tool-a", tool_type="python", capabilities=["execute_code"], permissions=["unknown.perm"])


def test_tool_contract_valid_permissions_and_resources():
    c = ToolContract.create(
        "tool-b",
        tool_type="python",
        capabilities=["execute_code"],
        permissions=["filesystem.read", "process.execute"],
        resources={"cpu": 2, "memory": "2GB"},
    )
    c.validate()


def test_tool_contract_invalid_resources():
    with pytest.raises(ToolError):
        ToolContract.create("tool-c", tool_type="python", capabilities=["execute_code"], resources={"cpu": 0})
    with pytest.raises(ToolError):
        ToolContract.create("tool-c", tool_type="python", capabilities=["execute_code"], resources={"memory": "bad"})


def test_tool_contract_health_values():
    for h in ToolHealth.all():
        c = ToolContract.create("tool-h", tool_type="python", capabilities=["execute_code"], health=h)
        assert c.health == h
    # String health
    c = ToolContract.create("tool-h2", tool_type="python", capabilities=["execute_code"], health="degraded")
    assert c.health == ToolHealth.DEGRADED


def test_tool_contract_priority_and_enabled():
    c = ToolContract.create("tool-p", tool_type="python", capabilities=["execute_code"], priority=100, enabled=False)
    assert c.priority == 100
    assert c.enabled is False
    c2 = ToolContract.create("tool-p2", tool_type="python", capabilities=["execute_code"], priority=50)
    assert c2.priority == 50


def test_tool_contract_invalid_priority():
    with pytest.raises(ToolError):
        ToolContract.create("tool-a", tool_type="python", capabilities=["execute_code"], priority="high")  # type: ignore


def test_tool_contract_to_dict():
    c = ToolContract.create("tool-dict", tool_type="python", capabilities=["execute_code"], health="healthy", priority=10)
    d = c.to_dict()
    assert d["tool_id"] == "tool-dict"
    assert d["tool_type"] == "python"
    assert d["health"] == "healthy"
    assert d["priority"] == 10
    assert "execute_code" in d["capabilities"]


def test_tool_contract_provenance():
    c = ToolContract.create("tool-prov", tool_type="python", capabilities=["execute_code"], metadata={"owner": "team-a"}, source="registry:tool")
    d = c.to_dict()
    assert d["metadata"]["owner"] == "team-a"
    assert d["source"] == "registry:tool"


# -- ToolResult --

def test_tool_result_success():
    r = ToolResult.success(tool_id="python.local", capability="execute_code", output="hello")
    assert r.status == "success"
    assert r.is_success is True
    assert r.tool_id == "python.local"
    assert r.capability == "execute_code"
    assert r.output == "hello"
    assert r.error is None
    assert r.evidence_ref.startswith("ev-")


def test_tool_result_failure():
    r = ToolResult.failure(tool_id="python.local", capability="execute_code", error="timeout", retryable=True)
    assert r.status == "failed"
    assert r.is_success is False
    assert r.error == "timeout"
    assert r.retryable is True


def test_tool_result_invalid_status():
    with pytest.raises(ToolError):
        ToolResult(status="unknown", tool_id="t", capability="c")


def test_tool_result_invalid_tool_id():
    with pytest.raises(ToolError):
        ToolResult(status="success", tool_id="", capability="c")


def test_tool_result_to_dict():
    r = ToolResult.success(tool_id="t", capability="c", output="out", evidence_ref="ev-123")
    d = r.to_dict()
    assert d["status"] == "success"
    assert d["tool_id"] == "t"
    assert d["evidence_ref"] == "ev-123"


# -- CapabilityRequest / Resolution --

def test_capability_request_create():
    req = CapabilityRequest.create(capability="execute_code", constraints={"language": "python"})
    assert req.capability == "execute_code"
    assert req.constraints["language"] == "python"
    assert req.request_id.startswith("req-")


def test_capability_request_invalid():
    with pytest.raises(ToolError):
        CapabilityRequest.create(capability="")
    with pytest.raises(ToolError):
        CapabilityRequest.create(capability="bad-capability!")
    with pytest.raises(ToolError):
        CapabilityRequest(capability="execute_code", constraints="not-a-dict")  # type: ignore


def test_capability_resolution_resolved():
    res = CapabilityResolution(
        capability="execute_code",
        status=ResolutionStatus.RESOLVED,
        selected_tool="python.local",
        reason=ResolutionReason(health="healthy", priority=100, policy="allow", detail="ok"),
        evidence_ref="ev-123",
    )
    assert res.is_resolved is True
    assert res.selected_tool == "python.local"
    d = res.to_dict()
    assert d["status"] == "resolved"
    assert d["selected_tool"] == "python.local"


def test_capability_resolution_unresolved():
    res = CapabilityResolution(
        capability="execute_code",
        status=ResolutionStatus.UNRESOLVED,
        selected_tool=None,
        reason=ResolutionReason(health="unknown", priority=0, policy="deny", detail="no tool"),
        evidence_ref="ev-123",
    )
    assert res.is_resolved is False
    assert res.selected_tool is None


def test_capability_resolution_invalid_status():
    with pytest.raises(ToolError):
        CapabilityResolution(capability="execute_code", status="invalid")  # type: ignore


# -- Contract check --

def test_check_tool_contracts():
    check_tool_contracts("1.0.0")
    check_tool_contracts()
    with pytest.raises(ContractError):
        check_tool_contracts("2.0.0")
    with pytest.raises(ContractError):
        check_tool_contracts("0.9.9")


def test_tool_contract_version_compatibility():
    c = ToolContract.create("tool-ver", tool_type="python", capabilities=["execute_code"], version="1.2.3")
    assert c.version == "1.2.3"
    # Check via registry compatibility
    from aios.tool.registry import ToolRegistry
    reg = ToolRegistry()
    reg.register(c)
    assert reg.is_compatible("tool-ver", ">=1.0.0,<2.0.0") is True
    assert reg.is_compatible("tool-ver", ">=2.0.0,<3.0.0") is False
