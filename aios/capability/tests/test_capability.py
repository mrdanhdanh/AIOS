"""Tests for Capability Registry — AC-009-01/02/10 + multi-tool + thread-safety."""

import threading
import pytest

from aios.capability.capability import CapabilityContract, CapabilityError, CapabilityRegistry


# -- Contract validation --

def test_capability_create_minimal():
    c = CapabilityContract.create("execute_code", version="1.0.0", description="Executes code")
    assert c.capability_id == "execute_code"
    assert c.version == "1.0.0"
    c.validate()


def test_capability_invalid_id():
    with pytest.raises(CapabilityError):
        CapabilityContract.create("", version="1.0.0")
    with pytest.raises(CapabilityError):
        CapabilityContract.create("123bad", version="1.0.0")
    with pytest.raises(CapabilityError):
        CapabilityContract.create("bad-id", version="1.0.0")  # hyphen not allowed


def test_capability_invalid_version():
    with pytest.raises(CapabilityError):
        CapabilityContract.create("cap_a", version="not-semver")


def test_capability_invalid_permission():
    with pytest.raises(CapabilityError):
        CapabilityContract.create("cap_a", permissions=["unknown.perm"])


def test_capability_valid_permissions_and_resources():
    c = CapabilityContract.create(
        "cap_b",
        permissions=["filesystem.read", "process.execute"],
        resources={"cpu": 2, "memory": "2GB"},
    )
    c.validate()


def test_capability_invalid_resources():
    with pytest.raises(CapabilityError):
        CapabilityContract.create("cap_c", resources={"cpu": 0})
    with pytest.raises(CapabilityError):
        CapabilityContract.create("cap_c", resources={"memory": "bad"})


def test_capability_provenance_retained():
    c = CapabilityContract.create("cap_p", source="registry:capability", metadata={"owner": "team-a"})
    d = c.to_dict()
    assert d["source"] == "registry:capability"
    assert d["metadata"]["owner"] == "team-a"


# -- Registry AC-009-01: register → resolve → inspect → list --

def test_registry_register_resolve_inspect_list():
    reg = CapabilityRegistry()
    cap = CapabilityContract.create("analyze_code", description="Analyze code")
    reg.register(cap)
    # resolve without tools → empty
    assert reg.resolve("analyze_code") == []
    # inspect
    fetched = reg.get("analyze_code")
    assert fetched.capability_id == "analyze_code"
    # list
    assert len(reg.list()) == 1
    assert len(reg) == 1
    assert "analyze_code" in reg


def test_registry_find():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("execute_code", description="Execute Python code", tags=["exec"]))
    reg.register(CapabilityContract.create("run_tests", description="Run test suite", tags=["test"]))
    results = reg.find("execute")
    assert len(results) == 1
    assert results[0].capability_id == "execute_code"
    # tag search
    assert len(reg.find("test")) == 1


def test_registry_duplicate_reject():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("dup_cap"))
    with pytest.raises(CapabilityError):
        reg.register(CapabilityContract.create("dup_cap"))


def test_registry_unknown_reject():
    reg = CapabilityRegistry()
    with pytest.raises(CapabilityError):
        reg.get("no_such")
    with pytest.raises(CapabilityError):
        reg.resolve("no_such")
    with pytest.raises(CapabilityError):
        reg.register_tool("no_such", "SomeTool")


def test_registry_remove():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("temp_cap"))
    reg.register_tool("temp_cap", "ToolA")
    reg.remove("temp_cap")
    assert "temp_cap" not in reg
    with pytest.raises(CapabilityError):
        reg.remove("temp_cap")


def test_registry_get_version_mismatch():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("ver_cap", version="1.2.3"))
    with pytest.raises(CapabilityError):
        reg.get("ver_cap", version="9.9.9")
    # correct version ok
    assert reg.get("ver_cap", version="1.2.3").version == "1.2.3"


# -- AC-009-02: multiple tools per capability --

def test_multiple_tools_per_capability():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("execute_code"))
    reg.register_tool("execute_code", "PythonTool", priority=1)
    reg.register_tool("execute_code", "DockerTool", priority=2)
    tools = reg.resolve("execute_code")
    assert tools == ["PythonTool", "DockerTool"]


def test_priority_ordering_deterministic():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("cap_x"))
    reg.register_tool("cap_x", "ToolB", priority=1)
    reg.register_tool("cap_x", "ToolA", priority=0)
    # priority asc → ToolA first
    assert reg.resolve("cap_x") == ["ToolA", "ToolB"]


def test_health_filtering():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("cap_h"))
    reg.register_tool("cap_h", "HealthyTool", priority=0, health="healthy")
    reg.register_tool("cap_h", "SickTool", priority=0, health="unhealthy")
    # default excludes unhealthy
    assert reg.resolve("cap_h") == ["HealthyTool"]
    assert reg.resolve("cap_h", include_unhealthy=True) == ["HealthyTool", "SickTool"]
    # flip health
    reg.set_tool_health("cap_h", "SickTool", "healthy")
    assert set(reg.resolve("cap_h")) == {"HealthyTool", "SickTool"}


def test_duplicate_tool_reject():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("cap_dup_tool"))
    reg.register_tool("cap_dup_tool", "ToolA")
    with pytest.raises(CapabilityError):
        reg.register_tool("cap_dup_tool", "ToolA")


def test_invalid_tool_args():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("cap_args"))
    with pytest.raises(CapabilityError):
        reg.register_tool("cap_args", "", priority=0)
    with pytest.raises(CapabilityError):
        reg.register_tool("cap_args", "ToolX", health="weird")
    with pytest.raises(CapabilityError):
        reg.register_tool("cap_args", "ToolX", priority="high")  # type: ignore


def test_list_tools_ordered():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("cap_list"))
    reg.register_tool("cap_list", "T2", priority=1)
    reg.register_tool("cap_list", "T1", priority=0)
    lst = reg.list_tools("cap_list")
    assert lst[0][0] == "T1"
    assert lst[1][0] == "T2"


# -- Fail-closed --

def test_registry_register_non_contract_reject():
    reg = CapabilityRegistry()
    with pytest.raises(CapabilityError):
        reg.register("not-a-contract")  # type: ignore


def test_registry_clear():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("cap_clear"))
    reg.register_tool("cap_clear", "ToolA")
    reg.clear()
    assert len(reg) == 0


# -- Thread safety --

def test_thread_safety_concurrent_register():
    reg = CapabilityRegistry()
    errors: list = []

    def worker(idx: int):
        try:
            cap = CapabilityContract.create(f"cap_{idx}", description=f"cap {idx}")
            reg.register(cap)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert len(reg) == 20


def test_thread_safety_concurrent_tool_register():
    reg = CapabilityRegistry()
    reg.register(CapabilityContract.create("shared_cap"))
    errors: list = []

    def worker(idx: int):
        try:
            reg.register_tool("shared_cap", f"Tool{idx}", priority=idx)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert len(reg.resolve("shared_cap", include_unhealthy=True)) == 10
