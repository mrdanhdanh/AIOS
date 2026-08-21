"""Tool adapters — 6 offline mock adapters (TASK-014, M2).

Each adapter wraps a :class:`ToolContract` and provides a deterministic
offline ``execute`` that returns a standardized :class:`ToolResult`.

No real process execution, no network, no Docker, no Git — all offline
mocks so tests run without Internet or external services.

Layering: ``tool`` layer — stdlib + ``aios.core`` only.
Never imports ``runtime`` / ``agent`` / ``orchestrator`` / ``capability``.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from .contracts import ToolContract, ToolError, ToolHealth, ToolResult, ToolType

__all__ = [
    "BaseToolAdapter",
    "PythonTool",
    "DockerTool",
    "RestTool",
    "McpTool",
    "ShellTool",
    "GitTool",
    "TOOL_ADAPTERS",
    "create_mock_tool",
]


class BaseToolAdapter:
    """Base for all Tool adapters — offline mock execution."""

    tool_type: ToolType = ToolType.PYTHON
    # Subclasses declare which capabilities they provide
    capabilities: List[str] = []

    def __init__(self, contract: ToolContract) -> None:
        if not isinstance(contract, ToolContract):
            raise ToolError("contract must be ToolContract")
        contract.validate()
        self.contract = contract
        self._call_count: int = 0
        self._call_log: List[Dict[str, Any]] = []

    @property
    def tool_id(self) -> str:
        return self.contract.tool_id

    @property
    def health(self) -> ToolHealth:
        h = self.contract.health
        if isinstance(h, str):
            try:
                h = ToolHealth(h)
            except ValueError:
                return ToolHealth.UNKNOWN
        return h

    def is_available(self) -> bool:
        if not self.contract.enabled:
            return False
        h = self.health
        return h.is_eligible()

    def execute(
        self,
        capability: str,
        input_data: Any = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """Execute a capability — offline mock, deterministic."""
        self._call_count += 1
        self._call_log.append(
            {"capability": capability, "input": input_data, "constraints": constraints or {}}
        )
        # Validate capability is declared
        if capability not in self.contract.capabilities:
            return ToolResult.failure(
                tool_id=self.tool_id,
                capability=capability,
                error=f"capability {capability!r} not supported by tool {self.tool_id!r}",
                retryable=False,
            )
        # Check health / enabled
        if not self.contract.enabled:
            return ToolResult.failure(
                tool_id=self.tool_id,
                capability=capability,
                error=f"tool {self.tool_id!r} is disabled",
                retryable=False,
            )
        h = self.health
        if not h.is_eligible():
            return ToolResult.failure(
                tool_id=self.tool_id,
                capability=capability,
                error=f"tool {self.tool_id!r} health {h.value!r} not eligible",
                retryable=False,
            )
        # Simulate timeout if input_data signals it
        if isinstance(input_data, dict) and input_data.get("simulate_timeout"):
            return ToolResult.failure(
                tool_id=self.tool_id,
                capability=capability,
                error="tool timeout",
                retryable=True,
            )
        if isinstance(input_data, dict) and input_data.get("simulate_failure"):
            return ToolResult.failure(
                tool_id=self.tool_id,
                capability=capability,
                error=input_data.get("error", "tool execution failure"),
                retryable=input_data.get("retryable", False),
            )
        # Success — deterministic mock output
        t0 = time.monotonic()
        output = self._mock_output(capability, input_data, constraints)
        dt = (time.monotonic() - t0) * 1000
        return ToolResult.success(
            tool_id=self.tool_id,
            capability=capability,
            output=output,
            metadata={"tool_type": self.contract.tool_type.value if isinstance(self.contract.tool_type, ToolType) else str(self.contract.tool_type)},
            duration_ms=dt,
            resource_usage={},
            evidence_ref=f"ev-{uuid.uuid4().hex[:12]}",
        )

    def _mock_output(self, capability: str, input_data: Any, constraints: Optional[Dict[str, Any]]) -> Any:
        """Override in subclasses for specific mock behavior."""
        return f"[{self.tool_id}:{capability}] mock output for {input_data!r}"

    @property
    def call_count(self) -> int:
        return self._call_count

    def reset(self) -> None:
        self._call_count = 0
        self._call_log.clear()


# ---------------------------------------------------------------------------
# Concrete adapters
# ---------------------------------------------------------------------------

class PythonTool(BaseToolAdapter):
    """Python execution tool — offline mock."""

    tool_type = ToolType.PYTHON
    capabilities = ["run_python", "execute_code", "run_tests"]

    def _mock_output(self, capability: str, input_data: Any, constraints: Optional[Dict[str, Any]]) -> Any:
        if capability == "run_tests":
            return {"tests_run": 1, "passed": 1, "failed": 0, "output": f"[python:{self.tool_id}] tests passed"}
        code = input_data if isinstance(input_data, str) else str(input_data)
        return f"[python:{self.tool_id}] executed: {code[:100]}"


class DockerTool(BaseToolAdapter):
    """Docker/container execution tool — offline mock (no real Docker)."""

    tool_type = ToolType.DOCKER
    capabilities = ["execute_container", "run_python", "run_tests"]

    def _mock_output(self, capability: str, input_data: Any, constraints: Optional[Dict[str, Any]]) -> Any:
        if capability == "execute_container":
            return {"container": "mock", "output": f"[docker:{self.tool_id}] container executed {input_data!r}"}
        if capability == "run_tests":
            return {"tests_run": 1, "passed": 1, "failed": 0, "output": f"[docker:{self.tool_id}] tests passed"}
        return f"[docker:{self.tool_id}] executed: {input_data!r}"


class RestTool(BaseToolAdapter):
    """REST/HTTP tool — offline mock (no real network)."""

    tool_type = ToolType.REST
    capabilities = ["http_request", "call_api"]

    def _mock_output(self, capability: str, input_data: Any, constraints: Optional[Dict[str, Any]]) -> Any:
        # input_data expected to be dict with url/method, but we mock
        url = input_data.get("url", "http://mock.local") if isinstance(input_data, dict) else str(input_data)
        return {"status": 200, "body": f"[rest:{self.tool_id}] mock response for {url}", "headers": {}}


class McpTool(BaseToolAdapter):
    """MCP tool — offline mock (no real MCP server)."""

    tool_type = ToolType.MCP
    capabilities = ["mcp_call", "call_tool", "mcp_invoke"]

    def _mock_output(self, capability: str, input_data: Any, constraints: Optional[Dict[str, Any]]) -> Any:
        tool_name = input_data.get("tool", "mock_tool") if isinstance(input_data, dict) else str(input_data)
        return {"mcp_tool": tool_name, "output": f"[mcp:{self.tool_id}] mock result for {tool_name}"}


class ShellTool(BaseToolAdapter):
    """Shell execution tool — offline mock (no real subprocess)."""

    tool_type = ToolType.SHELL
    capabilities = ["execute_shell", "run_command"]

    def _mock_output(self, capability: str, input_data: Any, constraints: Optional[Dict[str, Any]]) -> Any:
        cmd = input_data if isinstance(input_data, str) else str(input_data)
        # Never actually execute shell — just mock
        return {"command": cmd, "stdout": f"[shell:{self.tool_id}] mock stdout for {cmd[:50]}", "stderr": "", "exit_code": 0}


class GitTool(BaseToolAdapter):
    """Git tool — offline mock (no real git)."""

    tool_type = ToolType.GIT
    capabilities = ["git_read", "git_diff", "git_status", "git_commit"]

    def _mock_output(self, capability: str, input_data: Any, constraints: Optional[Dict[str, Any]]) -> Any:
        if capability == "git_status":
            return {"branch": "main", "status": "clean", "output": f"[git:{self.tool_id}] mock status"}
        if capability == "git_diff":
            return {"diff": f"[git:{self.tool_id}] mock diff", "files": []}
        if capability == "git_commit":
            msg = input_data.get("message", "mock commit") if isinstance(input_data, dict) else str(input_data)
            return {"commit": f"mock-{uuid.uuid4().hex[:8]}", "message": msg}
        # git_read
        return {"content": f"[git:{self.tool_id}] mock read for {input_data!r}"}


# Registry of tool_type -> adapter class
TOOL_ADAPTERS: Dict[str, type] = {
    ToolType.PYTHON.value: PythonTool,
    ToolType.DOCKER.value: DockerTool,
    ToolType.REST.value: RestTool,
    ToolType.MCP.value: McpTool,
    ToolType.SHELL.value: ShellTool,
    ToolType.GIT.value: GitTool,
}


def create_mock_tool(
    tool_id: str,
    tool_type: str | ToolType = ToolType.PYTHON,
    capabilities: Optional[List[str]] = None,
    priority: int = 0,
    health: str | ToolHealth = ToolHealth.HEALTHY,
    enabled: bool = True,
    version: str = "1.0.0",
) -> tuple[ToolContract, BaseToolAdapter]:
    """Helper to create a ToolContract + adapter for testing."""
    if isinstance(tool_type, str):
        try:
            tool_type = ToolType(tool_type)
        except ValueError as exc:
            raise ToolError(f"Unknown tool type {tool_type!r}") from exc
    if isinstance(health, str):
        try:
            health = ToolHealth(health)
        except ValueError as exc:
            raise ToolError(f"Unknown health {health!r}") from exc
    # Default capabilities based on tool_type if not provided
    if capabilities is None:
        adapter_cls = TOOL_ADAPTERS.get(tool_type.value, BaseToolAdapter)
        capabilities = list(getattr(adapter_cls, "capabilities", []))
        if not capabilities:
            capabilities = ["execute_code"]
    contract = ToolContract.create(
        tool_id=tool_id,
        name=tool_id,
        version=version,
        tool_type=tool_type,
        description=f"Mock {tool_type.value} tool {tool_id}",
        capabilities=capabilities,
        health=health,
        priority=priority,
        enabled=enabled,
    )
    adapter_cls = TOOL_ADAPTERS.get(contract.tool_type.value if isinstance(contract.tool_type, ToolType) else str(contract.tool_type), BaseToolAdapter)
    adapter = adapter_cls(contract)
    return contract, adapter
