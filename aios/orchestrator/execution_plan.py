"""ExecutionPlan — artifact between Orchestrator and Runtime (TASK-010).

Validated before Execution Service receives it. Deterministic, no LLM.

Layering: orchestrator.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

__all__ = ["PlanNode", "PlanEdge", "ExecutionPlan", "ExecutionPlanError"]

_MEMORY_RE = re.compile(r"^\d+(KB|MB|GB)$")
_ALLOWED_PERMISSIONS = {
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


class ExecutionPlanError(Exception):
    pass


@dataclass(frozen=True)
class PlanNode:
    id: str
    capability: str
    description: str = ""
    type: str = "task"

    def validate(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ExecutionPlanError("node.id must be non-empty string")
        if not isinstance(self.capability, str) or not self.capability.strip():
            raise ExecutionPlanError(f"node {self.id!r} capability must be non-empty string")
        if self.type not in {"task"}:
            raise ExecutionPlanError(f"node type {self.type!r} not allowed")


@dataclass(frozen=True)
class PlanEdge:
    from_id: str
    to_id: str

    def validate(self) -> None:
        if not isinstance(self.from_id, str) or not self.from_id.strip():
            raise ExecutionPlanError("edge from_id must be non-empty")
        if not isinstance(self.to_id, str) or not self.to_id.strip():
            raise ExecutionPlanError("edge to_id must be non-empty")
        if self.from_id == self.to_id:
            raise ExecutionPlanError(f"edge self-loop {self.from_id!r}")


@dataclass
class ExecutionPlan:
    """Validated execution plan for Runtime."""

    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: Optional[str] = None
    nodes: List[PlanNode] = field(default_factory=list)
    edges: List[PlanEdge] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)
    policy: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_node(self, node: PlanNode) -> None:
        if any(n.id == node.id for n in self.nodes):
            raise ExecutionPlanError(f"duplicate node id {node.id!r}")
        node.validate()
        self.nodes.append(node)

    def add_edge(self, edge: PlanEdge) -> None:
        edge.validate()
        if not any(n.id == edge.from_id for n in self.nodes):
            raise ExecutionPlanError(f"edge from {edge.from_id!r} references unknown node")
        if not any(n.id == edge.to_id for n in self.nodes):
            raise ExecutionPlanError(f"edge to {edge.to_id!r} references unknown node")
        if any(e.from_id == edge.from_id and e.to_id == edge.to_id for e in self.edges):
            raise ExecutionPlanError(f"duplicate edge {edge.from_id!r}->{edge.to_id!r}")
        self.edges.append(edge)

    def validate(self) -> None:
        if not isinstance(self.plan_id, str) or not self.plan_id.strip():
            raise ExecutionPlanError("plan_id must be non-empty string")
        if not self.nodes:
            raise ExecutionPlanError("plan must have at least one node")
        seen = set()
        for n in self.nodes:
            n.validate()
            if n.id in seen:
                raise ExecutionPlanError(f"duplicate node id {n.id!r}")
            seen.add(n.id)
        for e in self.edges:
            e.validate()
            if e.from_id not in seen:
                raise ExecutionPlanError(f"edge from {e.from_id!r} unknown")
            if e.to_id not in seen:
                raise ExecutionPlanError(f"edge to {e.to_id!r} unknown")
        # Cycle detection (simple DFS)
        adj: Dict[str, List[str]] = {n.id: [] for n in self.nodes}
        for e in self.edges:
            adj[e.from_id].append(e.to_id)
        visited: set = set()
        stack: set = set()

        def dfs(u: str) -> bool:
            visited.add(u)
            stack.add(u)
            for v in adj.get(u, []):
                if v not in visited:
                    if dfs(v):
                        return True
                elif v in stack:
                    return True
            stack.remove(u)
            return False

        for nid in adj:
            if nid not in visited:
                if dfs(nid):
                    raise ExecutionPlanError("cycle detected in plan edges")
        for p in self.permissions:
            if p not in _ALLOWED_PERMISSIONS:
                raise ExecutionPlanError(f"permission {p!r} not allowed")
        if self.resources:
            cpu = self.resources.get("cpu")
            mem = self.resources.get("memory")
            if cpu is not None and (not isinstance(cpu, int) or cpu <= 0):
                raise ExecutionPlanError(f"resources.cpu must be positive int, got {cpu!r}")
            if mem is not None and (not isinstance(mem, str) or not _MEMORY_RE.match(mem)):
                raise ExecutionPlanError(f"resources.memory must match <int><KB|MB|GB>, got {mem!r}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "request_id": self.request_id,
            "nodes": [{"id": n.id, "capability": n.capability, "type": n.type, "description": n.description} for n in self.nodes],
            "edges": [{"from": e.from_id, "to": e.to_id} for e in self.edges],
            "permissions": list(self.permissions),
            "resources": dict(self.resources),
            "policy": dict(self.policy),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }

    @property
    def is_valid(self) -> bool:
        try:
            self.validate()
            return True
        except ExecutionPlanError:
            return False
