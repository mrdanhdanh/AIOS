"""Tests for Tool Adapters — 6 adapters offline (TASK-014)."""

import pytest

from aios.tool.contracts import ToolContract, ToolHealth, ToolType
from aios.tool.adapters import (
    BaseToolAdapter,
    DockerTool,
    GitTool,
    McpTool,
    PythonTool,
    RestTool,
    ShellTool,
    TOOL_ADAPTERS,
    create_mock_tool,
)


# -- Base --

def test_base_adapter_requires_contract():
    with pytest.raises(Exception):
        BaseToolAdapter("not-a-contract")  # type: ignore


def test_base_adapter_health_and_availability():
    contract, adapter = create_mock_tool("tool-a", health="healthy")
    assert adapter.health == ToolHealth.HEALTHY
    assert adapter.is_available() is True
    contract2, adapter2 = create_mock_tool("tool-b", health="unhealthy")
    assert adapter2.is_available() is False
    contract3, adapter3 = create_mock_tool("tool-c", health="unknown")
    assert adapter3.is_available() is False
    contract4, adapter4 = create_mock_tool("tool-d", health="disabled")
    assert adapter4.is_available() is False
    contract5, adapter5 = create_mock_tool("tool-e", health="degraded")
    assert adapter5.is_available() is True


def test_base_adapter_disabled_not_available():
    contract, adapter = create_mock_tool("tool-a", enabled=False)
    assert adapter.is_available() is False


def test_base_adapter_execute_success():
    contract, adapter = create_mock_tool("python.local", tool_type="python", capabilities=["execute_code"])
    result = adapter.execute("execute_code", "print('hello')")
    assert result.status == "success"
    assert result.tool_id == "python.local"
    assert result.capability == "execute_code"
    assert result.evidence_ref.startswith("ev-")
    assert result.is_success is True


def test_base_adapter_execute_unsupported_capability():
    contract, adapter = create_mock_tool("python.local", capabilities=["execute_code"])
    result = adapter.execute("nonexistent_cap", "data")
    assert result.status == "failed"
    assert "not supported" in result.error


def test_base_adapter_execute_disabled():
    contract, adapter = create_mock_tool("tool-a", enabled=False)
    result = adapter.execute("execute_code", "data")
    assert result.status == "failed"
    assert "disabled" in result.error


def test_base_adapter_execute_unhealthy():
    contract, adapter = create_mock_tool("tool-a", health="unhealthy")
    result = adapter.execute("execute_code", "data")
    assert result.status == "failed"
    assert "not eligible" in result.error


def test_base_adapter_execute_unknown_health():
    contract, adapter = create_mock_tool("tool-a", health="unknown")
    result = adapter.execute("execute_code", "data")
    assert result.status == "failed"
    assert "not eligible" in result.error


def test_base_adapter_simulate_timeout():
    contract, adapter = create_mock_tool("tool-a")
    result = adapter.execute("execute_code", {"simulate_timeout": True})
    assert result.status == "failed"
    assert "timeout" in result.error
    assert result.retryable is True


def test_base_adapter_simulate_failure():
    contract, adapter = create_mock_tool("tool-a")
    result = adapter.execute("execute_code", {"simulate_failure": True, "error": "custom error", "retryable": True})
    assert result.status == "failed"
    assert result.error == "custom error"
    assert result.retryable is True


def test_base_adapter_call_count():
    contract, adapter = create_mock_tool("tool-a")
    assert adapter.call_count == 0
    adapter.execute("execute_code", "data")
    assert adapter.call_count == 1
    adapter.execute("execute_code", "data2")
    assert adapter.call_count == 2
    adapter.reset()
    assert adapter.call_count == 0


# -- PythonTool --

def test_python_tool_capabilities():
    assert "run_python" in PythonTool.capabilities
    assert "execute_code" in PythonTool.capabilities
    assert "run_tests" in PythonTool.capabilities


def test_python_tool_execute_code():
    contract, adapter = create_mock_tool("python.local", tool_type="python")
    assert isinstance(adapter, PythonTool)
    result = adapter.execute("execute_code", "x = 1")
    assert result.status == "success"
    assert "python" in result.output.lower()


def test_python_tool_run_tests():
    contract, adapter = create_mock_tool("python.local", tool_type="python")
    result = adapter.execute("run_tests", None)
    assert result.status == "success"
    assert result.output["passed"] == 1


def test_python_tool_run_python():
    contract, adapter = create_mock_tool("python.local", tool_type="python")
    result = adapter.execute("run_python", "print('hi')")
    assert result.status == "success"


# -- DockerTool --

def test_docker_tool_capabilities():
    assert "execute_container" in DockerTool.capabilities
    assert "run_python" in DockerTool.capabilities


def test_docker_tool_execute():
    contract, adapter = create_mock_tool("docker.python", tool_type="docker")
    assert isinstance(adapter, DockerTool)
    result = adapter.execute("execute_container", {"image": "python:3.11"})
    assert result.status == "success"
    assert "container" in result.output


def test_docker_tool_run_tests():
    contract, adapter = create_mock_tool("docker.python", tool_type="docker")
    result = adapter.execute("run_tests", None)
    assert result.status == "success"


# -- RestTool --

def test_rest_tool_capabilities():
    assert "http_request" in RestTool.capabilities
    assert "call_api" in RestTool.capabilities


def test_rest_tool_execute():
    contract, adapter = create_mock_tool("rest.api", tool_type="rest")
    assert isinstance(adapter, RestTool)
    result = adapter.execute("http_request", {"url": "http://example.com", "method": "GET"})
    assert result.status == "success"
    assert result.output["status"] == 200


def test_rest_tool_call_api():
    contract, adapter = create_mock_tool("rest.api", tool_type="rest")
    result = adapter.execute("call_api", {"url": "http://api.example.com/data"})
    assert result.status == "success"


# -- McpTool --

def test_mcp_tool_capabilities():
    assert "mcp_call" in McpTool.capabilities
    assert "call_tool" in McpTool.capabilities


def test_mcp_tool_execute():
    contract, adapter = create_mock_tool("mcp.server", tool_type="mcp")
    assert isinstance(adapter, McpTool)
    result = adapter.execute("mcp_call", {"tool": "search", "args": {}})
    assert result.status == "success"
    assert "mcp" in result.output["output"].lower()


# -- ShellTool --

def test_shell_tool_capabilities():
    assert "execute_shell" in ShellTool.capabilities
    assert "run_command" in ShellTool.capabilities


def test_shell_tool_execute():
    contract, adapter = create_mock_tool("shell.local", tool_type="shell")
    assert isinstance(adapter, ShellTool)
    result = adapter.execute("execute_shell", "echo hello")
    assert result.status == "success"
    assert result.output["exit_code"] == 0
    assert "shell" in result.output["stdout"].lower()


def test_shell_tool_run_command():
    contract, adapter = create_mock_tool("shell.local", tool_type="shell")
    result = adapter.execute("run_command", "ls -la")
    assert result.status == "success"


def test_shell_tool_never_executes_real_shell():
    # Verify no subprocess import in adapter (check imports, not docstring mentions)
    import ast
    import pathlib
    text = pathlib.Path("aios/tool/adapters.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imports.append(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    assert "subprocess" not in imports, f"adapters.py should not import subprocess, got {imports}"
    assert "os.system" not in text


# -- GitTool --

def test_git_tool_capabilities():
    assert "git_read" in GitTool.capabilities
    assert "git_diff" in GitTool.capabilities
    assert "git_status" in GitTool.capabilities
    assert "git_commit" in GitTool.capabilities


def test_git_tool_execute():
    contract, adapter = create_mock_tool("git.local", tool_type="git")
    assert isinstance(adapter, GitTool)
    result = adapter.execute("git_status", None)
    assert result.status == "success"
    assert result.output["branch"] == "main"


def test_git_tool_diff():
    contract, adapter = create_mock_tool("git.local", tool_type="git")
    result = adapter.execute("git_diff", None)
    assert result.status == "success"
    assert "diff" in result.output


def test_git_tool_commit():
    contract, adapter = create_mock_tool("git.local", tool_type="git")
    result = adapter.execute("git_commit", {"message": "feat: add feature"})
    assert result.status == "success"
    assert result.output["message"] == "feat: add feature"


def test_git_tool_read():
    contract, adapter = create_mock_tool("git.local", tool_type="git")
    result = adapter.execute("git_read", {"path": "README.md"})
    assert result.status == "success"


# -- TOOL_ADAPTERS registry --

def test_tool_adapters_registry():
    assert len(TOOL_ADAPTERS) == 6
    for t in ToolType.all():
        assert t.value in TOOL_ADAPTERS


def test_create_mock_tool_all_types():
    for t in ToolType.all():
        contract, adapter = create_mock_tool(f"tool-{t.value}", tool_type=t)
        assert contract.tool_type == t
        assert adapter.tool_id == f"tool-{t.value}"
        # Each adapter should have at least one capability
        assert len(contract.capabilities) >= 1


def test_create_mock_tool_invalid_type():
    with pytest.raises(Exception):
        create_mock_tool("tool-a", tool_type="invalid")  # type: ignore


def test_create_mock_tool_invalid_health():
    with pytest.raises(Exception):
        create_mock_tool("tool-a", health="invalid")  # type: ignore


def test_create_mock_tool_custom_capabilities():
    contract, adapter = create_mock_tool("tool-custom", capabilities=["custom_cap", "another_cap"])
    assert "custom_cap" in contract.capabilities
    assert "another_cap" in contract.capabilities
    result = adapter.execute("custom_cap", "data")
    assert result.status == "success"
    result2 = adapter.execute("not_declared", "data")
    assert result2.status == "failed"


# -- Offline: no network/subprocess --

def test_adapters_offline_no_network():
    import pathlib
    text = pathlib.Path("aios/tool/adapters.py").read_text(encoding="utf-8")
    # Adapters should not import requests, httpx, docker, etc.
    assert "import requests" not in text
    assert "import docker" not in text
    assert "import subprocess" not in text
    # urllib is allowed for RestTool mock but should not actually call network
    # Our RestTool is mock, so no real network call
    contract, adapter = create_mock_tool("rest.api", tool_type="rest")
    result = adapter.execute("http_request", {"url": "http://example.com"})
    assert result.status == "success"
    # No actual network was used — just mock
    assert "mock" in result.output["body"].lower()
