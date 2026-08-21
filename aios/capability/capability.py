"""Capability Registry — first-class metadata + multi-tool mapping (TASK-009, M1).

Capability is the abstraction workers see; tools are implementations behind it.
A single capability (e.g. ``execute_code``) can map to many tools
(``PythonTool``, ``DockerTool``) and agents resolve capabilities without
knowing which tool will run them.

Offline-first, deterministic, thread-safe via :class:`threading.RLock`.
No LLM, no network, no embeddings.

Layering: ``capability`` layer — stdlib + ``aios.core`` only.
Never imports ``runtime``/``agent``/``orchestrator``.
"""

from __future__ import annotations

import re
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from aios.core.version import SemVer, VersionError

__all__ = ["CapabilityError", "CapabilityContract", "CapabilityRegistry"]

# ---------------------------------------------------------------------------
# Validation vocabularies
# ---------------------------------------------------------------------------

_CAP_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
_MEMORY_RE = re.compile(r"^\d+(KB|MB|GB)$")

# Keep in sync with workflow allowed permissions so policy pre-checks stay
# coherent across the two contracts.
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


class CapabilityError(Exception):
    """Raised on capability validation or registry errors."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Contract
# ---------------------------------------------------------------------------
@dataclass
class CapabilityContract:
    """First-class capability metadata (no tool implementation)."""

    capability_id: str
    version: str = "1.0.0"
    description: str = ""
    permissions: List[str] = field(default_factory=list)
    resources: Dict[str, object] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    # provenance — where this capability was declared; required for Catalog/Graph
    source: str = ""
    metadata: Dict[str, object] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        capability_id: str,
        version: str = "1.0.0",
        description: str = "",
        permissions: Optional[List[str]] = None,
        resources: Optional[Dict[str, object]] = None,
        tags: Optional[List[str]] = None,
        source: str = "",
        metadata: Optional[Dict[str, object]] = None,
    ) -> "CapabilityContract":
        obj = cls(
            capability_id=capability_id,
            version=version,
            description=description,
            permissions=list(permissions or []),
            resources=dict(resources or {}),
            tags=list(tags or []),
            source=source or "",
            metadata=dict(metadata or {}),
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if not isinstance(self.capability_id, str) or not self.capability_id.strip():
            raise CapabilityError("capability_id must be a non-empty string")
        if not _CAP_ID_RE.match(self.capability_id):
            raise CapabilityError(
                f"capability_id {self.capability_id!r} must match {_CAP_ID_RE.pattern}"
            )
        # version must be valid SemVer
        try:
            SemVer.parse(self.version)
        except VersionError as exc:
            raise CapabilityError(f"Invalid version {self.version!r}: {exc}") from exc
        if not isinstance(self.description, str):
            raise CapabilityError("description must be a string")
        if not isinstance(self.permissions, list):
            raise CapabilityError("permissions must be a list")
        for p in self.permissions:
            if not isinstance(p, str) or not p.strip():
                raise CapabilityError(f"permission {p!r} must be a non-empty string")
            if p not in ALLOWED_PERMISSIONS:
                raise CapabilityError(
                    f"permission {p!r} not in allowed {sorted(ALLOWED_PERMISSIONS)}"
                )
        if not isinstance(self.resources, dict):
            raise CapabilityError("resources must be a mapping")
        if self.resources:
            cpu = self.resources.get("cpu")
            mem = self.resources.get("memory")
            if cpu is not None:
                if not isinstance(cpu, int) or cpu <= 0:
                    raise CapabilityError(f"resources.cpu must be positive int, got {cpu!r}")
            if mem is not None:
                if not isinstance(mem, str) or not _MEMORY_RE.match(mem):
                    raise CapabilityError(
                        f"resources.memory must match <int><KB|MB|GB>, got {mem!r}"
                    )
        if not isinstance(self.tags, list):
            raise CapabilityError("tags must be a list")
        for t in self.tags:
            if not isinstance(t, str) or not t.strip():
                raise CapabilityError(f"tag {t!r} must be a non-empty string")

    def to_dict(self) -> Dict[str, object]:
        return {
            "capability_id": self.capability_id,
            "version": self.version,
            "description": self.description,
            "permissions": list(self.permissions),
            "resources": dict(self.resources),
            "tags": list(self.tags),
            "source": self.source,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ---------------------------------------------------------------------------
# Health — 5-state per TASK-014 §7 (backward compat with M1 healthy/unhealthy)
# ---------------------------------------------------------------------------
_TOOL_HEALTH_VALUES = {"unknown", "healthy", "degraded", "unhealthy", "disabled"}
# Eligible for routing: healthy + degraded (degraded if policy allows)
_ELIGIBLE_HEALTH = {"healthy", "degraded"}


def _normalize_health(health: str) -> str:
    h = health.lower().strip() if isinstance(health, str) else str(health)
    if h not in _TOOL_HEALTH_VALUES:
        raise CapabilityError(f"health must be one of {sorted(_TOOL_HEALTH_VALUES)}, got {health!r}")
    return h


def _is_eligible_health(health: str) -> bool:
    return _normalize_health(health) in _ELIGIBLE_HEALTH


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
@dataclass(order=True)
class _ToolMapping:
    priority: int
    seq: int
    tool_id: str = field(compare=False)
    health: str = field(compare=False)  # "unknown" | "healthy" | "degraded" | "unhealthy" | "disabled"


class CapabilityRegistry:
    """Thread-safe registry of :class:`CapabilityContract` + tool mappings."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._caps: Dict[str, CapabilityContract] = {}
        # capability_id -> list[_ToolMapping] (ordered by priority, seq)
        self._tool_map: Dict[str, List[_ToolMapping]] = {}
        self._seq: int = 0

    # -- capability CRUD ---------------------------------------------------
    def register(self, contract: CapabilityContract) -> None:
        if not isinstance(contract, CapabilityContract):
            raise CapabilityError("contract must be CapabilityContract")
        contract.validate()
        with self._lock:
            cid = contract.capability_id
            if cid in self._caps:
                raise CapabilityError(f"capability already registered: {cid!r}")
            self._caps[cid] = contract
            self._tool_map.setdefault(cid, [])

    def get(self, capability_id: str, version: Optional[str] = None) -> CapabilityContract:
        with self._lock:
            cap = self._caps.get(capability_id)
        if cap is None:
            raise CapabilityError(f"unknown capability: {capability_id!r}")
        if version is not None and cap.version != version:
            raise CapabilityError(
                f"capability {capability_id!r} version mismatch: expected {version!r}, got {cap.version!r}"
            )
        return cap

    def list(self) -> List[CapabilityContract]:
        with self._lock:
            return sorted(self._caps.values(), key=lambda c: c.capability_id)

    def find(self, query: str) -> List[CapabilityContract]:
        q = query.lower()
        with self._lock:
            out: List[CapabilityContract] = []
            for c in self._caps.values():
                hay = " ".join([c.capability_id, c.description, " ".join(c.tags)]).lower()
                if q in hay:
                    out.append(c)
            return sorted(out, key=lambda c: c.capability_id)

    def remove(self, capability_id: str) -> None:
        with self._lock:
            if capability_id not in self._caps:
                raise CapabilityError(f"unknown capability: {capability_id!r}")
            del self._caps[capability_id]
            self._tool_map.pop(capability_id, None)

    def __len__(self) -> int:
        with self._lock:
            return len(self._caps)

    def __contains__(self, capability_id: str) -> bool:
        with self._lock:
            return capability_id in self._caps

    # -- tool mappings -----------------------------------------------------
    def register_tool(
        self,
        capability_id: str,
        tool_id: str,
        priority: int = 0,
        health: str = "healthy",
    ) -> None:
        if not isinstance(tool_id, str) or not tool_id.strip():
            raise CapabilityError("tool_id must be a non-empty string")
        _normalize_health(health)
        if not isinstance(priority, int):
            raise CapabilityError("priority must be int")
        with self._lock:
            if capability_id not in self._caps:
                raise CapabilityError(f"unknown capability: {capability_id!r}")
            lst = self._tool_map.setdefault(capability_id, [])
            if any(m.tool_id == tool_id for m in lst):
                raise CapabilityError(
                    f"tool {tool_id!r} already mapped to capability {capability_id!r}"
                )
            self._seq += 1
            lst.append(_ToolMapping(priority=priority, seq=self._seq, tool_id=tool_id, health=health))
            lst.sort()  # priority asc, seq asc (deterministic)

    def set_tool_health(self, capability_id: str, tool_id: str, health: str) -> None:
        _normalize_health(health)
        with self._lock:
            lst = self._tool_map.get(capability_id)
            if lst is None:
                raise CapabilityError(f"unknown capability: {capability_id!r}")
            for m in lst:
                if m.tool_id == tool_id:
                    m.health = health
                    return
            raise CapabilityError(f"tool {tool_id!r} not mapped to {capability_id!r}")

    def resolve(self, capability_id: str, *, include_unhealthy: bool = False) -> List[str]:
        """Return ordered tool_ids for capability (priority → registration order).

        When ``include_unhealthy`` is False (default), only HEALTHY + DEGRADED
        are returned (UNKNOWN/UNHEALTHY/DISABLED are rejected — fail-closed).
        """
        with self._lock:
            if capability_id not in self._caps:
                raise CapabilityError(f"unknown capability: {capability_id!r}")
            lst = list(self._tool_map.get(capability_id, []))
        if not include_unhealthy:
            lst = [m for m in lst if _is_eligible_health(m.health)]
        lst.sort()
        return [m.tool_id for m in lst]

    def list_tools(self, capability_id: str) -> List[Tuple[str, int, str]]:
        """Return (tool_id, priority, health) for capability (ordered)."""
        with self._lock:
            if capability_id not in self._caps:
                raise CapabilityError(f"unknown capability: {capability_id!r}")
            lst = sorted(self._tool_map.get(capability_id, []))
            return [(m.tool_id, m.priority, m.health) for m in lst]

    def clear(self) -> None:
        with self._lock:
            self._caps.clear()
            self._tool_map.clear()
            self._seq = 0
