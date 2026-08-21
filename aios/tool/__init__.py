"""AIOS Tool + Capability Layer (TASK-014, M2).

Tool is the implementation; Capability is the abstraction workers see.
Workers never import Tool directly — they request a Capability, the
CapabilityRouter resolves it to a Tool via health/priority/policy.

Layering: ``tool`` layer — only imports ``aios.core`` + stdlib.
Never imports ``runtime`` / ``agent`` / ``orchestrator`` / ``capability``.

Components:
    contracts  — ToolContract, ToolHealth, ToolType, ToolResult, CapabilityRequest/Resolution
    registry   — ToolRegistry (dynamic Capability→Tool[] discovery)
    adapters   — 6 offline mock adapters (python/docker/rest/mcp/shell/git)

Runtime wiring (``aios.runtime.capability_router``) is at ``runtime`` layer
and may import ``tool`` + ``capability`` + ``runtime``.
"""

from .contracts import (
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
from .registry import ToolRegistry
from .adapters import (
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

__all__ = [
    # contracts
    "TOOL_CONTRACT",
    "ToolType",
    "ToolHealth",
    "ToolContract",
    "ToolResult",
    "ToolError",
    "ToolCapabilityDeclarationError",
    "CapabilityRequest",
    "CapabilityResolution",
    "ResolutionStatus",
    "ResolutionReason",
    "check_tool_contracts",
    # registry
    "ToolRegistry",
    # adapters
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
