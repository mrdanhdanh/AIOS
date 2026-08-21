"""Tests for Tool Registry — AC-014-01/02/03/04/11 (TASK-014)."""

import threading
import pytest

from aios.tool.contracts import ToolContract, ToolError, ToolHealth, ToolType
from aios.tool.registry import ToolRegistry


def _tool(tool_id, caps=None, priority=0, health="healthy", enabled=True, tool_type="python", version="1.0.0"):
    return ToolContract.create(
        tool_id=tool_id,
        tool_type=tool_type,
        capabilities=caps or ["execute_code"],
        priority=priority,
        health=health,
        enabled=enabled,
        version=version,
    )


# -- Basic CRUD --

def test_registry_register_get_list():
    reg = ToolRegistry()
    c = _tool("python.local")
    reg.register(c)
    assert reg.get("python.local").tool_id == "python.local"
    assert len(reg.list()) == 1
    assert len(reg) == 1
    assert "python.local" in reg


def test_registry_duplicate_reject():
    reg = ToolRegistry()
    reg.register(_tool("tool-a"))
    with pytest.raises(ToolError):
        reg.register(_tool("tool-a"))


def test_registry_unknown_reject():
    reg = ToolRegistry()
    with pytest.raises(ToolError):
        reg.get("no_such")
    with pytest.raises(ToolError):
        reg.unregister("no_such")


def test_registry_unregister():
    reg = ToolRegistry()
    reg.register(_tool("tool-a", caps=["execute_code"]))
    reg.unregister("tool-a")
    assert "tool-a" not in reg
    assert len(reg) == 0
    # Capability index cleaned
    assert reg.find_by_capability("execute_code") == []


def test_registry_register_non_contract_reject():
    reg = ToolRegistry()
    with pytest.raises(ToolError):
        reg.register("not-a-contract")  # type: ignore


def test_registry_clear():
    reg = ToolRegistry()
    reg.register(_tool("tool-a"))
    reg.register(_tool("tool-b"))
    reg.clear()
    assert len(reg) == 0
    assert reg.capabilities() == []


# -- Capability declaration (AC-014-02) --

def test_tool_declares_multiple_capabilities():
    reg = ToolRegistry()
    c = _tool("python.local", caps=["execute_code", "run_python", "run_tests"])
    reg.register(c)
    assert len(c.capabilities) == 3
    # Each capability maps to this tool
    for cap in ["execute_code", "run_python", "run_tests"]:
        tools = reg.find_by_capability(cap)
        assert len(tools) == 1
        assert tools[0].tool_id == "python.local"


def test_tool_declares_single_capability():
    reg = ToolRegistry()
    reg.register(_tool("shell.local", caps=["execute_shell"], tool_type="shell"))
    tools = reg.find_by_capability("execute_shell")
    assert len(tools) == 1


# -- Dynamic discovery (AC-014-03) --

def test_dynamic_discovery_capability_to_tools():
    reg = ToolRegistry()
    reg.register(_tool("python.local", caps=["execute_code"], priority=10))
    reg.register(_tool("docker.python", caps=["execute_code"], priority=5, tool_type="docker"))
    # Discovery: execute_code → [python.local, docker.python] sorted by priority desc
    tools = reg.find_by_capability("execute_code")
    assert len(tools) == 2
    assert tools[0].tool_id == "python.local"  # higher priority first
    assert tools[1].tool_id == "docker.python"


def test_dynamic_discovery_no_hardcode():
    reg = ToolRegistry()
    reg.register(_tool("python.local", caps=["execute_code"]))
    reg.register(_tool("python.sandbox", caps=["execute_code"]))
    reg.register(_tool("docker.python", caps=["execute_code"], tool_type="docker"))
    mapping = reg.list_capabilities()
    assert "execute_code" in mapping
    assert set(mapping["execute_code"]) == {"python.local", "python.sandbox", "docker.python"}


def test_capabilities_list():
    reg = ToolRegistry()
    reg.register(_tool("tool-a", caps=["execute_code"]))
    reg.register(_tool("tool-b", caps=["http_request"], tool_type="rest"))
    caps = reg.capabilities()
    assert "execute_code" in caps
    assert "http_request" in caps
    assert caps == sorted(caps)


def test_find_by_capability_empty():
    reg = ToolRegistry()
    assert reg.find_by_capability("nonexistent") == []


def test_lookup_aliases():
    reg = ToolRegistry()
    reg.register(_tool("tool-a", caps=["execute_code"]))
    assert reg.lookup_by_capability("execute_code")[0].tool_id == "tool-a"
    assert reg.get_by_capability("execute_code")[0].tool_id == "tool-a"


# -- Multi-tool capability (AC-014-04) --

def test_multi_tool_capability():
    reg = ToolRegistry()
    reg.register(_tool("python.local", caps=["execute_code"], priority=10))
    reg.register(_tool("python.sandbox", caps=["execute_code"], priority=90))
    reg.register(_tool("docker.python", caps=["execute_code"], priority=50, tool_type="docker"))
    tools = reg.find_by_capability("execute_code")
    assert len(tools) == 3
    # Sorted by priority desc
    assert tools[0].tool_id == "python.sandbox"  # 90
    assert tools[1].tool_id == "docker.python"  # 50
    assert tools[2].tool_id == "python.local"  # 10


def test_multi_tool_different_capabilities():
    reg = ToolRegistry()
    reg.register(_tool("python.local", caps=["execute_code", "run_python"]))
    reg.register(_tool("shell.local", caps=["execute_shell"], tool_type="shell"))
    reg.register(_tool("git.local", caps=["git_read", "git_status"], tool_type="git"))
    assert len(reg.find_by_capability("execute_code")) == 1
    assert len(reg.find_by_capability("execute_shell")) == 1
    assert len(reg.find_by_capability("git_read")) == 1
    assert len(reg.find_by_capability("git_status")) == 1


# -- Enable/disable --

def test_enable_disable():
    reg = ToolRegistry()
    reg.register(_tool("tool-a", enabled=True))
    assert reg.is_enabled("tool-a") is True
    reg.disable("tool-a")
    assert reg.is_enabled("tool-a") is False
    assert reg.get("tool-a").enabled is False
    reg.enable("tool-a")
    assert reg.is_enabled("tool-a") is True


def test_enable_unknown_reject():
    reg = ToolRegistry()
    with pytest.raises(ToolError):
        reg.enable("no_such")
    with pytest.raises(ToolError):
        reg.disable("no_such")


# -- Health --

def test_set_get_health():
    reg = ToolRegistry()
    reg.register(_tool("tool-a", health="healthy"))
    assert reg.get_health("tool-a") == ToolHealth.HEALTHY
    reg.set_health("tool-a", "degraded")
    assert reg.get_health("tool-a") == ToolHealth.DEGRADED
    reg.set_health("tool-a", ToolHealth.UNHEALTHY)
    assert reg.get_health("tool-a") == ToolHealth.UNHEALTHY
    reg.set_health("tool-a", "disabled")
    assert reg.get_health("tool-a") == ToolHealth.DISABLED
    reg.set_health("tool-a", "unknown")
    assert reg.get_health("tool-a") == ToolHealth.UNKNOWN


def test_set_health_unknown_reject():
    reg = ToolRegistry()
    reg.register(_tool("tool-a"))
    with pytest.raises(ToolError):
        reg.set_health("tool-a", "invalid_health")


def test_set_health_unknown_tool():
    reg = ToolRegistry()
    with pytest.raises(ToolError):
        reg.set_health("no_such", "healthy")


# -- Priority --

def test_set_get_priority():
    reg = ToolRegistry()
    reg.register(_tool("tool-a", priority=10))
    assert reg.get_priority("tool-a") == 10
    reg.set_priority("tool-a", 100)
    assert reg.get_priority("tool-a") == 100
    # Verify ordering updated
    reg.register(_tool("tool-b", priority=50))
    tools = reg.find_by_capability("execute_code")
    assert tools[0].tool_id == "tool-a"  # 100 > 50


def test_set_priority_invalid():
    reg = ToolRegistry()
    reg.register(_tool("tool-a"))
    with pytest.raises(ToolError):
        reg.set_priority("tool-a", "high")  # type: ignore


# -- Metadata --

def test_get_metadata():
    reg = ToolRegistry()
    reg.register(_tool("tool-a"))
    meta = reg.get_metadata("tool-a")
    assert meta["tool_id"] == "tool-a"
    assert "capabilities" in meta


# -- Version / compatibility --

def test_check_version():
    reg = ToolRegistry()
    reg.register(_tool("tool-a", version="1.2.3"))
    assert reg.check_version("tool-a", "1.2.3") is True
    assert reg.check_version("tool-a", "1.2.4") is False


def test_is_compatible():
    reg = ToolRegistry()
    reg.register(_tool("tool-a", version="1.2.3"))
    assert reg.is_compatible("tool-a", ">=1.0.0,<2.0.0") is True
    assert reg.is_compatible("tool-a", ">=2.0.0,<3.0.0") is False


def test_check_compatibility_raise():
    reg = ToolRegistry()
    reg.register(_tool("tool-a", version="1.2.3"))
    reg.check_compatibility("tool-a", ">=1.0.0,<2.0.0")  # ok
    with pytest.raises(ToolError):
        reg.check_compatibility("tool-a", ">=2.0.0,<3.0.0")


# -- Search --

def test_find():
    reg = ToolRegistry()
    reg.register(_tool("python.local", caps=["execute_code"]))
    reg.register(_tool("docker.python", caps=["execute_code"], tool_type="docker"))
    results = reg.find("python")
    assert len(results) == 2
    results = reg.find("docker")
    assert len(results) == 1


def test_find_empty_reject():
    reg = ToolRegistry()
    with pytest.raises(ToolError):
        reg.find("")
    with pytest.raises(ToolError):
        reg.find("   ")


def test_find_by_capability_invalid():
    reg = ToolRegistry()
    with pytest.raises(ToolError):
        reg.find_by_capability("")
    with pytest.raises(ToolError):
        reg.find_by_capability("   ")


# -- Thread safety --

def test_thread_safety_concurrent_register():
    reg = ToolRegistry()
    errors: list = []

    def worker(idx: int):
        try:
            c = _tool(f"tool-{idx}", caps=[f"cap_{idx}"])
            reg.register(c)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert len(reg) == 20


def test_thread_safety_concurrent_capability_lookup():
    reg = ToolRegistry()
    for i in range(10):
        reg.register(_tool(f"tool-{i}", caps=["shared_cap"]))

    errors: list = []
    results: list = []

    def worker():
        try:
            tools = reg.find_by_capability("shared_cap")
            results.append(len(tools))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert all(r == 10 for r in results)


# -- Evidence: list_capabilities --

def test_list_capabilities_evidence():
    reg = ToolRegistry()
    reg.register(_tool("python.local", caps=["execute_code", "run_python"]))
    reg.register(_tool("shell.local", caps=["execute_shell"], tool_type="shell"))
    mapping = reg.list_capabilities()
    assert "execute_code" in mapping
    assert "run_python" in mapping
    assert "execute_shell" in mapping
    assert mapping["execute_code"] == ["python.local"]
