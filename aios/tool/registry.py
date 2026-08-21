"""Tool Registry — dynamic discovery of Tool ↔ Capability mapping (TASK-014, M2).

Registry is the discovery source for Tools. A single capability can map to
many tools; tools declare capabilities and the registry builds the reverse
index automatically.

Offline-first, deterministic, thread-safe via :class:`threading.RLock`.
No LLM, no network.

Layering: ``tool`` layer — stdlib + ``aios.core`` only.
Never imports ``runtime`` / ``agent`` / ``orchestrator`` / ``capability``.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from aios.core.version import SemVer, VersionError

from .contracts import ToolContract, ToolError, ToolHealth, ToolType

__all__ = ["ToolRegistry"]


@dataclass(order=True)
class _ToolEntry:
    # For sorting: priority descending, seq asc, tool_id asc
    # We store negative priority for descending sort via dataclass ordering
    sort_priority: int
    seq: int
    tool_id: str = field(compare=False)
    contract: ToolContract = field(compare=False)


class ToolRegistry:
    """Thread-safe registry of :class:`ToolContract` with dynamic capability index."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._tools: Dict[str, ToolContract] = {}
        # capability -> list[tool_id] (maintained on register/unregister)
        self._cap_index: Dict[str, List[str]] = {}
        self._seq: int = 0

    # -- helpers ---------------------------------------------------------
    def _rebuild_cap_index_for(self, tool_id: str, old_caps: List[str] | None = None, new_caps: List[str] | None = None) -> None:
        """Update capability index for a tool's capabilities."""
        if old_caps:
            for cap in old_caps:
                lst = self._cap_index.get(cap, [])
                if tool_id in lst:
                    lst.remove(tool_id)
                if not lst:
                    self._cap_index.pop(cap, None)
        if new_caps:
            for cap in new_caps:
                self._cap_index.setdefault(cap, [])
                if tool_id not in self._cap_index[cap]:
                    self._cap_index[cap].append(tool_id)

    def _sorted_tools_for_capability(self, capability: str) -> List[ToolContract]:
        """Return ToolContracts for capability sorted by priority desc, seq asc, tool_id asc."""
        tool_ids = self._cap_index.get(capability, [])
        contracts = [self._tools[tid] for tid in tool_ids if tid in self._tools]
        # Sort: priority descending, then health eligibility, then tool_id
        # Higher priority wins; tie-break by seq (registration order) then tool_id
        # We need seq — store in contract metadata or track separately
        # For now, sort by priority desc, then tool_id asc (deterministic)
        # To preserve registration order, we use _seq via internal map
        # Build seq map
        # Since we don't store seq per tool, we approximate with tool_id order
        # Instead, maintain _tool_seq dict
        return sorted(contracts, key=lambda c: (-c.priority, c.tool_id))

    # -- CRUD ------------------------------------------------------------
    def register(self, contract: ToolContract) -> None:
        if not isinstance(contract, ToolContract):
            raise ToolError("contract must be ToolContract")
        contract.validate()
        with self._lock:
            tid = contract.tool_id
            if tid in self._tools:
                raise ToolError(f"tool already registered: {tid!r}")
            self._tools[tid] = contract
            self._seq += 1
            # Store seq in metadata for deterministic ordering
            contract.metadata["_seq"] = self._seq
            for cap in contract.capabilities:
                self._cap_index.setdefault(cap, []).append(tid)

    def unregister(self, tool_id: str) -> None:
        with self._lock:
            contract = self._tools.get(tool_id)
            if contract is None:
                raise ToolError(f"unknown tool: {tool_id!r}")
            # Remove from capability index
            for cap in contract.capabilities:
                lst = self._cap_index.get(cap, [])
                if tool_id in lst:
                    lst.remove(tool_id)
                if not lst:
                    self._cap_index.pop(cap, None)
            del self._tools[tool_id]

    def get(self, tool_id: str) -> ToolContract:
        with self._lock:
            c = self._tools.get(tool_id)
        if c is None:
            raise ToolError(f"unknown tool: {tool_id!r}")
        return c

    def list(self) -> List[ToolContract]:
        with self._lock:
            return sorted(self._tools.values(), key=lambda c: c.tool_id)

    def find(self, query: str) -> List[ToolContract]:
        if not isinstance(query, str) or not query.strip():
            raise ToolError("query must be a non-empty string")
        q = query.lower()
        with self._lock:
            out: List[ToolContract] = []
            for c in self._tools.values():
                hay = " ".join([c.tool_id, c.name, c.description, " ".join(c.capabilities)]).lower()
                # also include metadata string values
                for v in c.metadata.values():
                    if isinstance(v, str):
                        hay += " " + v.lower()
                if q in hay:
                    out.append(c)
            return sorted(out, key=lambda c: c.tool_id)

    def find_by_capability(self, capability: str) -> List[ToolContract]:
        """Lookup tools by capability (dynamic discovery)."""
        if not isinstance(capability, str) or not capability.strip():
            raise ToolError("capability must be a non-empty string")
        with self._lock:
            tool_ids = list(self._cap_index.get(capability, []))
            contracts = [self._tools[tid] for tid in tool_ids if tid in self._tools]
        # Sort by priority descending, then seq asc, then tool_id asc
        # Use stored _seq for tie-break
        def sort_key(c: ToolContract):
            seq = c.metadata.get("_seq", 0)
            return (-c.priority, seq, c.tool_id)
        return sorted(contracts, key=sort_key)

    # Alias for spec compatibility
    def lookup_by_capability(self, capability: str) -> List[ToolContract]:
        return self.find_by_capability(capability)

    def get_by_capability(self, capability: str) -> List[ToolContract]:
        return self.find_by_capability(capability)

    def list_capabilities(self) -> Dict[str, List[str]]:
        """Return mapping Capability -> Tool[] (tool_ids)."""
        with self._lock:
            return {cap: list(tids) for cap, tids in self._cap_index.items()}

    def capabilities(self) -> List[str]:
        with self._lock:
            return sorted(self._cap_index.keys())

    # -- enable/disable --------------------------------------------------
    def enable(self, tool_id: str) -> None:
        with self._lock:
            c = self._tools.get(tool_id)
            if c is None:
                raise ToolError(f"unknown tool: {tool_id!r}")
            c.enabled = True
            c.updated_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()

    def disable(self, tool_id: str) -> None:
        with self._lock:
            c = self._tools.get(tool_id)
            if c is None:
                raise ToolError(f"unknown tool: {tool_id!r}")
            c.enabled = False
            c.updated_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()

    def is_enabled(self, tool_id: str) -> bool:
        return self.get(tool_id).enabled

    # -- health ----------------------------------------------------------
    def set_health(self, tool_id: str, health: ToolHealth | str) -> None:
        if isinstance(health, str):
            try:
                health = ToolHealth(health)
            except ValueError as exc:
                raise ToolError(f"Unknown health {health!r}") from exc
        if not isinstance(health, ToolHealth):
            raise ToolError(f"health must be ToolHealth, got {type(health).__name__}")
        with self._lock:
            c = self._tools.get(tool_id)
            if c is None:
                raise ToolError(f"unknown tool: {tool_id!r}")
            c.health = health
            c.updated_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()

    def get_health(self, tool_id: str) -> ToolHealth:
        c = self.get(tool_id)
        h = c.health
        if isinstance(h, str):
            try:
                h = ToolHealth(h)
            except ValueError:
                return ToolHealth.UNKNOWN
        return h

    def set_priority(self, tool_id: str, priority: int) -> None:
        if not isinstance(priority, int):
            raise ToolError("priority must be int")
        with self._lock:
            c = self._tools.get(tool_id)
            if c is None:
                raise ToolError(f"unknown tool: {tool_id!r}")
            c.priority = priority
            c.updated_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()

    def get_priority(self, tool_id: str) -> int:
        return self.get(tool_id).priority

    # -- metadata --------------------------------------------------------
    def get_metadata(self, tool_id: str) -> Dict[str, object]:
        return dict(self.get(tool_id).to_dict())

    # -- version / compatibility -----------------------------------------
    def check_version(self, tool_id: str, version: str) -> bool:
        """Check if tool's version equals given version."""
        c = self.get(tool_id)
        return c.version == version

    def is_compatible(self, tool_id: str, required_range: str) -> bool:
        """Check if tool's version satisfies required_range (e.g. '>=1.0.0,<2.0.0')."""
        from aios.core.contracts import Contract
        c = self.get(tool_id)
        contract = Contract(name=f"tool:{tool_id}", version_range=required_range)
        return contract.is_satisfied_by(c.version)

    def check_compatibility(self, tool_id: str, required_range: str) -> None:
        """Raise ToolError if not compatible."""
        from aios.core.contracts import ContractError
        c = self.get(tool_id)
        from aios.core.contracts import Contract
        contract = Contract(name=f"tool:{tool_id}", version_range=required_range)
        try:
            from aios.core.contracts import check_compatibility
            check_compatibility(contract, c.version)
        except ContractError as exc:
            raise ToolError(str(exc)) from exc

    # -- misc ------------------------------------------------------------
    def __len__(self) -> int:
        with self._lock:
            return len(self._tools)

    def __contains__(self, tool_id: str) -> bool:
        with self._lock:
            return tool_id in self._tools

    def clear(self) -> None:
        with self._lock:
            self._tools.clear()
            self._cap_index.clear()
            self._seq = 0
