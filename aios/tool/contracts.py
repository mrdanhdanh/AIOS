"""Tool + Capability contracts — versioned interfaces (TASK-014, M2).

Defines the unified Tool Contract, health model, result contract and
capability resolution contract. All Tool metadata is validated here so
registry and router can fail-closed on invalid contracts.

Layering: ``tool`` layer — stdlib + ``aios.core`` only.
Never imports ``runtime`` / ``agent`` / ``orchestrator`` / ``capability``.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.core.contracts import Contract, check_compatibility
from aios.core.version import SemVer, VersionError

__all__ = [
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
    "ToolCandidate",
    "check_tool_contracts",
]

# ---------------------------------------------------------------------------
# Contracts
# ---------------------------------------------------------------------------

TOOL_CONTRACT = Contract(
    name="tool.registry",
    version_range=">=1.0.0,<2.0.0",
    description="Tool registry — unified Tool Contract + health + capability declaration (TASK-014).",
)

_TOOL_VERSION = "1.0.0"


def check_tool_contracts(version: str | None = None) -> None:
    """Verify tool contract against ``version`` (or 1.0.0)."""
    ver = version or _TOOL_VERSION
    check_compatibility(TOOL_CONTRACT, ver)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ToolType(str, Enum):
    """Six Tool types per TASK-014 §3.1."""

    PYTHON = "python"
    DOCKER = "docker"
    REST = "rest"
    MCP = "mcp"
    SHELL = "shell"
    GIT = "git"

    @classmethod
    def all(cls) -> List["ToolType"]:
        return list(cls)


class ToolHealth(str, Enum):
    """Five health states per TASK-014 §7."""

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DISABLED = "disabled"

    @classmethod
    def all(cls) -> List["ToolHealth"]:
        return list(cls)

    def is_eligible(self) -> bool:
        """Return True if this health state is eligible for routing.

        Per spec:
          HEALTHY  -> eligible
          DEGRADED -> eligible (if policy allows — router decides)
          UNHEALTHY -> reject
          DISABLED -> reject
          UNKNOWN -> reject (fail-closed, never promoted to healthy)
        """
        return self in (ToolHealth.HEALTHY, ToolHealth.DEGRADED)


class ResolutionStatus(str, Enum):
    """Outcome of capability resolution."""

    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"


# ---------------------------------------------------------------------------
# Validation vocabularies
# ---------------------------------------------------------------------------

_TOOL_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_\-\.]*$")
_CAP_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
_MEMORY_RE = re.compile(r"^\d+(KB|MB|GB)$")

ALLOWED_PERMISSIONS = {
    "filesystem.read",
    "filesystem.write",
    "process.execute",
    "network.read",
    "network.write",
    "capability:invoke",
    "tool:invoke",
    "memory:read",
    "memory:write",
}


class ToolError(Exception):
    """Raised on tool validation or execution errors."""


class ToolCapabilityDeclarationError(ToolError):
    """Raised when a tool declares an invalid capability."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Tool Contract
# ---------------------------------------------------------------------------

@dataclass
class ToolContract:
    """Unified Tool Contract per TASK-014 §3.1."""

    tool_id: str
    name: str = ""
    version: str = "1.0.0"
    tool_type: ToolType | str = ToolType.PYTHON
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    resources: Dict[str, object] = field(default_factory=dict)
    health: ToolHealth | str = ToolHealth.HEALTHY
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        tool_id: str,
        name: str = "",
        version: str = "1.0.0",
        tool_type: ToolType | str = ToolType.PYTHON,
        description: str = "",
        capabilities: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        resources: Optional[Dict[str, object]] = None,
        health: ToolHealth | str = ToolHealth.HEALTHY,
        priority: int = 0,
        enabled: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "",
    ) -> "ToolContract":
        # Normalize enums from strings
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
        obj = cls(
            tool_id=tool_id,
            name=name or tool_id,
            version=version,
            tool_type=tool_type,
            description=description or "",
            capabilities=list(capabilities or []),
            permissions=list(permissions or []),
            resources=dict(resources or {}),
            health=health,
            priority=priority,
            enabled=enabled,
            metadata=dict(metadata or {}),
            source=source or "",
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if not isinstance(self.tool_id, str) or not self.tool_id.strip():
            raise ToolError("tool_id must be a non-empty string")
        if not _TOOL_ID_RE.match(self.tool_id):
            raise ToolError(f"tool_id {self.tool_id!r} must match {_TOOL_ID_RE.pattern}")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ToolError("name must be a non-empty string")
        try:
            SemVer.parse(self.version)
        except VersionError as exc:
            raise ToolError(f"Invalid version {self.version!r}: {exc}") from exc
        if isinstance(self.tool_type, str):
            try:
                self.tool_type = ToolType(self.tool_type)
            except ValueError as exc:
                raise ToolError(f"Unknown tool type {self.tool_type!r}") from exc
        if not isinstance(self.tool_type, ToolType):
            raise ToolError(f"tool_type must be ToolType, got {type(self.tool_type).__name__}")
        if not isinstance(self.description, str):
            raise ToolError("description must be a string")
        if not isinstance(self.capabilities, list):
            raise ToolError("capabilities must be a list")
        for cap in self.capabilities:
            if not isinstance(cap, str) or not cap.strip():
                raise ToolCapabilityDeclarationError(f"capability {cap!r} must be a non-empty string")
            if not _CAP_ID_RE.match(cap):
                raise ToolCapabilityDeclarationError(
                    f"capability {cap!r} must match {_CAP_ID_RE.pattern}"
                )
        if not isinstance(self.permissions, list):
            raise ToolError("permissions must be a list")
        for p in self.permissions:
            if not isinstance(p, str) or not p.strip():
                raise ToolError(f"permission {p!r} must be a non-empty string")
            if p not in ALLOWED_PERMISSIONS:
                raise ToolError(f"permission {p!r} not in allowed {sorted(ALLOWED_PERMISSIONS)}")
        if not isinstance(self.resources, dict):
            raise ToolError("resources must be a mapping")
        if self.resources:
            cpu = self.resources.get("cpu")
            mem = self.resources.get("memory")
            if cpu is not None:
                if not isinstance(cpu, int) or cpu <= 0:
                    raise ToolError(f"resources.cpu must be positive int, got {cpu!r}")
            if mem is not None:
                if not isinstance(mem, str) or not _MEMORY_RE.match(mem):
                    raise ToolError(f"resources.memory must match <int><KB|MB|GB>, got {mem!r}")
        if isinstance(self.health, str):
            try:
                self.health = ToolHealth(self.health)
            except ValueError as exc:
                raise ToolError(f"Unknown health {self.health!r}") from exc
        if not isinstance(self.health, ToolHealth):
            raise ToolError(f"health must be ToolHealth, got {type(self.health).__name__}")
        if not isinstance(self.priority, int):
            raise ToolError("priority must be int")
        if not isinstance(self.enabled, bool):
            raise ToolError("enabled must be bool")
        if not isinstance(self.metadata, dict):
            raise ToolError("metadata must be a mapping")
        if not isinstance(self.source, str):
            raise ToolError("source must be a string")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "version": self.version,
            "tool_type": self.tool_type.value if isinstance(self.tool_type, ToolType) else str(self.tool_type),
            "description": self.description,
            "capabilities": list(self.capabilities),
            "permissions": list(self.permissions),
            "resources": dict(self.resources),
            "health": self.health.value if isinstance(self.health, ToolHealth) else str(self.health),
            "priority": self.priority,
            "enabled": self.enabled,
            "metadata": dict(self.metadata),
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ---------------------------------------------------------------------------
# Tool Result
# ---------------------------------------------------------------------------

@dataclass
class ToolResult:
    """Standardized Tool execution result per TASK-014 §10."""

    status: str  # "success" | "failed"
    tool_id: str
    capability: str
    output: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    evidence_ref: str = ""
    error: Optional[str] = None
    retryable: bool = False

    def __post_init__(self) -> None:
        if self.status not in ("success", "failed"):
            raise ToolError(f"ToolResult status must be 'success' or 'failed', got {self.status!r}")
        if not isinstance(self.tool_id, str) or not self.tool_id.strip():
            raise ToolError("ToolResult tool_id must be a non-empty string")
        if not isinstance(self.capability, str) or not self.capability.strip():
            raise ToolError("ToolResult capability must be a non-empty string")

    @classmethod
    def success(
        cls,
        tool_id: str,
        capability: str,
        output: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        duration_ms: float = 0.0,
        resource_usage: Optional[Dict[str, Any]] = None,
        evidence_ref: str = "",
    ) -> "ToolResult":
        return cls(
            status="success",
            tool_id=tool_id,
            capability=capability,
            output=output,
            metadata=dict(metadata or {}),
            duration_ms=duration_ms,
            resource_usage=dict(resource_usage or {}),
            evidence_ref=evidence_ref or f"ev-{uuid.uuid4().hex[:12]}",
            error=None,
            retryable=False,
        )

    @classmethod
    def failure(
        cls,
        tool_id: str,
        capability: str,
        error: str,
        retryable: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        duration_ms: float = 0.0,
        evidence_ref: str = "",
    ) -> "ToolResult":
        return cls(
            status="failed",
            tool_id=tool_id,
            capability=capability,
            output=None,
            metadata=dict(metadata or {}),
            duration_ms=duration_ms,
            resource_usage={},
            evidence_ref=evidence_ref or f"ev-{uuid.uuid4().hex[:12]}",
            error=error,
            retryable=retryable,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "tool_id": self.tool_id,
            "capability": self.capability,
            "output": self.output,
            "metadata": dict(self.metadata),
            "duration_ms": self.duration_ms,
            "resource_usage": dict(self.resource_usage),
            "evidence_ref": self.evidence_ref,
            "error": self.error,
            "retryable": self.retryable,
        }

    @property
    def is_success(self) -> bool:
        return self.status == "success"


# ---------------------------------------------------------------------------
# Capability Resolution Contract
# ---------------------------------------------------------------------------

@dataclass
class CapabilityRequest:
    """Request for capability resolution per TASK-014 §8."""

    capability: str
    constraints: Dict[str, Any] = field(default_factory=dict)
    subject: str = "worker"
    resource: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: f"req-{uuid.uuid4().hex[:12]}")

    def __post_init__(self) -> None:
        if not isinstance(self.capability, str) or not self.capability.strip():
            raise ToolError("CapabilityRequest capability must be a non-empty string")
        if not _CAP_ID_RE.match(self.capability):
            raise ToolError(f"capability {self.capability!r} must match {_CAP_ID_RE.pattern}")
        if not isinstance(self.constraints, dict):
            raise ToolError("constraints must be a mapping")
        if not isinstance(self.metadata, dict):
            raise ToolError("metadata must be a mapping")

    @classmethod
    def create(
        cls,
        capability: str,
        constraints: Optional[Dict[str, Any]] = None,
        subject: str = "worker",
        resource: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> "CapabilityRequest":
        return cls(
            capability=capability,
            constraints=dict(constraints or {}),
            subject=subject,
            resource=resource or capability,
            metadata=dict(metadata or {}),
            request_id=request_id or f"req-{uuid.uuid4().hex[:12]}",
        )


@dataclass
class ToolCandidate:
    """A candidate Tool for a capability."""

    tool_id: str
    health: ToolHealth | str
    priority: int
    enabled: bool
    eligible: bool = False
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "health": self.health.value if isinstance(self.health, ToolHealth) else str(self.health),
            "priority": self.priority,
            "enabled": self.enabled,
            "eligible": self.eligible,
            "reason": self.reason,
        }


@dataclass
class ResolutionReason:
    """Why a resolution was made per TASK-014 §8."""

    health: str = ""
    priority: int = 0
    policy: str = ""  # allow | deny | ask | insufficient
    detail: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "health": self.health,
            "priority": self.priority,
            "policy": self.policy,
            "detail": self.detail,
        }


@dataclass
class CapabilityResolution:
    """Result of capability resolution per TASK-014 §8."""

    capability: str
    status: ResolutionStatus | str
    selected_tool: Optional[str] = None
    reason: ResolutionReason = field(default_factory=ResolutionReason)
    candidates: List[ToolCandidate] = field(default_factory=list)
    evidence_ref: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: str = ""

    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            try:
                self.status = ResolutionStatus(self.status)
            except ValueError as exc:
                raise ToolError(f"Unknown resolution status {self.status!r}") from exc

    @property
    def is_resolved(self) -> bool:
        return self.status == ResolutionStatus.RESOLVED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability": self.capability,
            "status": self.status.value if isinstance(self.status, ResolutionStatus) else str(self.status),
            "selected_tool": self.selected_tool,
            "reason": self.reason.to_dict() if isinstance(self.reason, ResolutionReason) else self.reason,
            "candidates": [c.to_dict() for c in self.candidates],
            "evidence_ref": self.evidence_ref,
            "metadata": dict(self.metadata),
            "request_id": self.request_id,
        }
