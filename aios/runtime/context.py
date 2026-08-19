"""Runtime execution contexts (TASK-004, M1).

Six context types form the runtime's scoping substrate. They are the unit of
isolation that later services (policy, permission, artifact, audit) attach to:

    REQUEST   — a single inbound request entering the runtime
    AGENT     — the agent identity on whose behalf work runs
    WORKFLOW  — a workflow instance being executed
    CAPABILITY— a capability surface invoked by an agent
    TOOL      — a concrete tool execution
    EXECUTION — a unit of execution (a step / a run) inside a workflow

Contexts are hierarchical: a TOOL context has a CAPABILITY parent, which has an
AGENT parent, which has a REQUEST parent, which has an EXECUTION parent. The
store supports walking that chain so policy decisions can consult the full
lineage without reaching across layers.

Layering: ``agent -> orchestrator -> runtime -> capability -> tool``. This
module lives at the ``runtime`` layer and only depends on ``aios.core``
(stdlib + kernel primitives), never on agent/orchestrator layers.
"""

from __future__ import annotations

import threading
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


__all__ = ["ContextError", "ContextType", "RuntimeContext", "ContextStore"]


class ContextError(Exception):
    """Raised on invalid context operations."""


class ContextType(Enum):
    """The six runtime context types (TASK-004 scope)."""

    REQUEST = "request"
    AGENT = "agent"
    WORKFLOW = "workflow"
    CAPABILITY = "capability"
    TOOL = "tool"
    EXECUTION = "execution"

    @classmethod
    def all(cls) -> List["ContextType"]:
        return list(cls)


@dataclass
class RuntimeContext:
    """A single runtime context with optional parent linkage.

    ``attributes`` is an open bag of scoped metadata (agent_id, workflow_id,
    capability_id, tool_id, request_id, ...). It is NOT a bypass of the typed
    contract layer — it only carries correlation identifiers and provenance
    tags that the audit/policy services read.
    """

    context_id: str
    context_type: ContextType
    parent_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def create(
        cls,
        context_type: ContextType,
        parent_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        context_id: Optional[str] = None,
    ) -> "RuntimeContext":
        """Factory that mints a fresh context id when none is supplied."""
        return cls(
            context_id=context_id or f"ctx-{uuid.uuid4().hex[:12]}",
            context_type=context_type,
            parent_id=parent_id,
            attributes=dict(attributes or {}),
        )

    def set_attr(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def get_attr(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)


class ContextStore:
    """Thread-safe in-memory store for runtime contexts.

    Supports lookup by id, by type, by parent (children), and full parent-chain
    resolution. The store never imports agent/orchestrator code; it is a pure
    substrate service.
    """

    def __init__(self) -> None:
        self._contexts: Dict[str, RuntimeContext] = {}
        self._by_type: Dict[ContextType, List[str]] = defaultdict(list)
        self._children: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.RLock()

    def put(self, ctx: RuntimeContext) -> RuntimeContext:
        """Insert or replace a context (keyed by ``context_id``)."""
        if not isinstance(ctx, RuntimeContext):
            raise ContextError("ContextStore only holds RuntimeContext")
        with self._lock:
            if ctx.parent_id and ctx.parent_id not in self._contexts:
                # Parent not yet known; tolerated (lazy linking) but recorded.
                pass
            existing = self._contexts.get(ctx.context_id)
            if existing is not None and existing.context_type != ctx.context_type:
                # Keep type index consistent on replace.
                self._by_type[existing.context_type] = [
                    cid for cid in self._by_type[existing.context_type]
                    if cid != ctx.context_id
                ]
            self._contexts[ctx.context_id] = ctx
            if ctx.context_id not in self._by_type[ctx.context_type]:
                self._by_type[ctx.context_type].append(ctx.context_id)
            if ctx.parent_id:
                if ctx.context_id not in self._children[ctx.parent_id]:
                    self._children[ctx.parent_id].append(ctx.context_id)
        return ctx

    def get(self, context_id: str) -> RuntimeContext:
        with self._lock:
            ctx = self._contexts.get(context_id)
        if ctx is None:
            raise ContextError(f"Context not found: {context_id!r}")
        return ctx

    def try_get(self, context_id: str) -> Optional[RuntimeContext]:
        with self._lock:
            return self._contexts.get(context_id)

    def exists(self, context_id: str) -> bool:
        with self._lock:
            return context_id in self._contexts

    def list_by_type(self, context_type: ContextType) -> List[RuntimeContext]:
        with self._lock:
            ids = list(self._by_type.get(context_type, []))
        return [self._contexts[i] for i in ids]

    def children_of(self, parent_id: str) -> List[RuntimeContext]:
        with self._lock:
            ids = list(self._children.get(parent_id, []))
        return [self._contexts[i] for i in ids]

    def resolve_chain(self, context_id: str) -> List[RuntimeContext]:
        """Return [self, parent, grandparent, ...] up to the root context.

        Stops if a parent link is missing (lazy-linking case) rather than
        raising, so callers always get a usable lineage slice.
        """
        chain: List[RuntimeContext] = []
        with self._lock:
            cur = self._contexts.get(context_id)
            seen = set()
            while cur is not None and cur.context_id not in seen:
                chain.append(cur)
                seen.add(cur.context_id)
                cur = self._contexts.get(cur.parent_id) if cur.parent_id else None
        return chain

    def delete(self, context_id: str) -> None:
        with self._lock:
            ctx = self._contexts.pop(context_id, None)
            if ctx is None:
                return
            if context_id in self._by_type[ctx.context_type]:
                self._by_type[ctx.context_type].remove(context_id)
            self._children.pop(context_id, None)
            for kids in self._children.values():
                if context_id in kids:
                    kids.remove(context_id)

    def clear(self) -> None:
        with self._lock:
            self._contexts.clear()
            self._by_type.clear()
            self._children.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._contexts)
