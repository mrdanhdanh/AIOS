"""Execution graph contracts."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeState(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class GraphNode:
    node_id: str = ""
    name: str = ""
    state: NodeState = NodeState.PENDING
    capabilities: list[str] = field(default_factory=list)
    resources: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"node_id": self.node_id, "name": self.name, "state": self.state.value, "capabilities": self.capabilities}


@dataclass
class GraphEdge:
    source: str = ""
    target: str = ""
    edge_type: str = "hard"

    def to_dict(self) -> dict[str, Any]:
        return {"source": self.source, "target": self.target, "edge_type": self.edge_type}


@dataclass
class ExecutionGraph:
    graph_id: str = ""
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    entry_nodes: list[str] = field(default_factory=list)
    terminal_nodes: list[str] = field(default_factory=list)
    topological_order: list[str] = field(default_factory=list)
    content_hash: str = ""
    provenance: list[str] = field(default_factory=list)

    def compute_hash(self) -> str:
        content = f"{self.graph_id}:{','.join(n.node_id for n in self.nodes)}"
        self.content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self.content_hash

    def get_node(self, node_id: str) -> GraphNode | None:
        for n in self.nodes:
            if n.node_id == node_id:
                return n
        return None

    def get_successors(self, node_id: str) -> list[str]:
        return [e.target for e in self.edges if e.source == node_id]

    def get_predecessors(self, node_id: str) -> list[str]:
        return [e.source for e in self.edges if e.target == node_id]

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "entry_nodes": self.entry_nodes,
            "terminal_nodes": self.terminal_nodes,
            "topological_order": self.topological_order,
            "content_hash": self.content_hash,
        }
