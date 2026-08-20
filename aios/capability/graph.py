"""Knowledge Graph v1 — in-memory manual relationship graph (TASK-009, M1).

M1 graph is intentionally minimal: in-memory storage, manual population via
API, no SQLite, no auto-build from event bus.  It proves the contract and
basic traversal; persistence/reasoning ships in M2/M4.

Offline-first, deterministic, thread-safe via :class:`threading.RLock`.
No LLM, no network.

Layering: ``capability`` layer — stdlib + ``aios.core`` only.
"""

from __future__ import annotations

import threading
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from aios.core.version import SemVer, VersionError

__all__ = [
    "GraphError",
    "NodeType",
    "EdgeType",
    "GraphNode",
    "GraphEdge",
    "KnowledgeGraph",
]


class GraphError(Exception):
    """Raised on graph validation or lookup errors."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class NodeType(str, Enum):
    """Allowed node types (M1)."""

    AGENT = "agent"
    SKILL = "skill"
    WORKFLOW = "workflow"
    CAPABILITY = "capability"
    TOOL = "tool"
    ARTIFACT = "artifact"
    MODEL = "model"
    PROMPT = "prompt"

    @classmethod
    def all(cls) -> List["NodeType"]:
        return list(cls)


# Edge types covering 2.8 examples.  Additional types allowed but validated.
class EdgeType(str, Enum):
    USES = "USES"
    IMPLEMENTED_BY = "IMPLEMENTED_BY"
    PROVIDES = "PROVIDES"
    REQUIRES = "REQUIRES"
    PRODUCES = "PRODUCES"
    DEPENDS_ON = "DEPENDS_ON"
    CONTAINS = "CONTAINS"

    @classmethod
    def all(cls) -> List["EdgeType"]:
        return list(cls)


@dataclass
class GraphNode:
    """A typed node in the knowledge graph."""

    node_id: str
    node_type: NodeType | str
    label: str = ""
    description: str = ""
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    # provenance — which registry/source produced this node
    source: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        node_id: str,
        node_type: NodeType | str,
        label: str = "",
        description: str = "",
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "",
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "GraphNode":
        if isinstance(node_type, str):
            try:
                node_type = NodeType(node_type)
            except ValueError as exc:
                raise GraphError(f"Unknown node type {node_type!r}") from exc
        obj = cls(
            node_id=node_id,
            node_type=node_type,
            label=label or "",
            description=description or "",
            version=version,
            metadata=dict(metadata or {}),
            source=source or "",
            provenance=dict(provenance or {}),
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if not isinstance(self.node_id, str) or not self.node_id.strip():
            raise GraphError("node_id must be a non-empty string")
        if isinstance(self.node_type, str):
            try:
                self.node_type = NodeType(self.node_type)
            except ValueError as exc:
                raise GraphError(f"Unknown node type {self.node_type!r}") from exc
        if not isinstance(self.node_type, NodeType):
            raise GraphError(f"node_type must be NodeType, got {type(self.node_type).__name__}")
        try:
            SemVer.parse(self.version)
        except VersionError as exc:
            raise GraphError(f"Invalid version {self.version!r}: {exc}") from exc
        if not isinstance(self.label, str):
            raise GraphError("label must be a string")
        if not isinstance(self.metadata, dict):
            raise GraphError("metadata must be a mapping")
        if not isinstance(self.source, str):
            raise GraphError("source must be a string")
        if not isinstance(self.provenance, dict):
            raise GraphError("provenance must be a mapping")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value if isinstance(self.node_type, NodeType) else str(self.node_type),
            "label": self.label,
            "description": self.description,
            "version": self.version,
            "metadata": dict(self.metadata),
            "source": self.source,
            "provenance": dict(self.provenance),
            "created_at": self.created_at,
        }


@dataclass
class GraphEdge:
    """A directed typed edge between two nodes."""

    from_id: str
    to_id: str
    edge_type: EdgeType | str
    edge_id: str = ""
    label: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        from_id: str,
        to_id: str,
        edge_type: EdgeType | str,
        edge_id: Optional[str] = None,
        label: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "",
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "GraphEdge":
        if isinstance(edge_type, str):
            try:
                edge_type = EdgeType(edge_type)
            except ValueError as exc:
                raise GraphError(f"Unknown edge type {edge_type!r}") from exc
        obj = cls(
            edge_id=edge_id or f"edge-{uuid.uuid4().hex[:12]}",
            from_id=from_id,
            to_id=to_id,
            edge_type=edge_type,
            label=label or "",
            metadata=dict(metadata or {}),
            source=source or "",
            provenance=dict(provenance or {}),
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if not isinstance(self.edge_id, str) or not self.edge_id.strip():
            raise GraphError("edge_id must be a non-empty string")
        if not isinstance(self.from_id, str) or not self.from_id.strip():
            raise GraphError("from_id must be a non-empty string")
        if not isinstance(self.to_id, str) or not self.to_id.strip():
            raise GraphError("to_id must be a non-empty string")
        if self.from_id == self.to_id:
            # self-loops not allowed in M1 (keep deterministic DAG-like)
            raise GraphError(f"edge self-loop not allowed: {self.from_id!r} -> {self.to_id!r}")
        if isinstance(self.edge_type, str):
            try:
                self.edge_type = EdgeType(self.edge_type)
            except ValueError as exc:
                raise GraphError(f"Unknown edge type {self.edge_type!r}") from exc
        if not isinstance(self.edge_type, EdgeType):
            raise GraphError(f"edge_type must be EdgeType, got {type(self.edge_type).__name__}")
        if not isinstance(self.metadata, dict):
            raise GraphError("metadata must be a mapping")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "edge_type": self.edge_type.value if isinstance(self.edge_type, EdgeType) else str(self.edge_type),
            "label": self.label,
            "metadata": dict(self.metadata),
            "source": self.source,
            "provenance": dict(self.provenance),
            "created_at": self.created_at,
        }


class KnowledgeGraph:
    """In-memory, manual, deterministic knowledge graph (M1)."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._nodes: Dict[str, GraphNode] = {}
        # edge_id -> GraphEdge
        self._edges: Dict[str, GraphEdge] = {}
        # adjacency lists for fast neighbors
        self._out: Dict[str, List[str]] = {}  # node_id -> [edge_id]
        self._in: Dict[str, List[str]] = {}  # node_id -> [edge_id]

    # -- nodes -------------------------------------------------------------
    def add_node(self, node: GraphNode) -> None:
        if not isinstance(node, GraphNode):
            raise GraphError("node must be GraphNode")
        node.validate()
        with self._lock:
            if node.node_id in self._nodes:
                raise GraphError(f"duplicate node: {node.node_id!r}")
            self._nodes[node.node_id] = node
            self._out.setdefault(node.node_id, [])
            self._in.setdefault(node.node_id, [])

    def get_node(self, node_id: str) -> GraphNode:
        with self._lock:
            n = self._nodes.get(node_id)
        if n is None:
            raise GraphError(f"unknown node: {node_id!r}")
        return n

    def has_node(self, node_id: str) -> bool:
        with self._lock:
            return node_id in self._nodes

    def list_nodes(self, node_type: Optional[NodeType | str] = None) -> List[GraphNode]:
        with self._lock:
            nodes = list(self._nodes.values())
        if node_type is not None:
            if isinstance(node_type, str):
                try:
                    node_type = NodeType(node_type)
                except ValueError as exc:
                    raise GraphError(f"Unknown node type {node_type!r}") from exc
            nodes = [n for n in nodes if n.node_type == node_type]
        return sorted(nodes, key=lambda n: n.node_id)

    def remove_node(self, node_id: str) -> None:
        with self._lock:
            if node_id not in self._nodes:
                raise GraphError(f"unknown node: {node_id!r}")
            # reject if node still has edges (caller must remove edges first)
            if self._out.get(node_id) or self._in.get(node_id):
                # also check any edge referencing this node still exists
                has_edges = any(
                    e.from_id == node_id or e.to_id == node_id for e in self._edges.values()
                )
                if has_edges:
                    raise GraphError(f"cannot remove node {node_id!r} while edges exist")
            self._nodes.pop(node_id, None)
            self._out.pop(node_id, None)
            self._in.pop(node_id, None)

    # -- edges -------------------------------------------------------------
    def add_edge(self, edge: GraphEdge) -> None:
        if not isinstance(edge, GraphEdge):
            raise GraphError("edge must be GraphEdge")
        edge.validate()
        with self._lock:
            if edge.edge_id in self._edges:
                raise GraphError(f"duplicate edge: {edge.edge_id!r}")
            if edge.from_id not in self._nodes:
                raise GraphError(f"edge from_id unknown node: {edge.from_id!r}")
            if edge.to_id not in self._nodes:
                raise GraphError(f"edge to_id unknown node: {edge.to_id!r}")
            # reject duplicate (from, to, edge_type) triple
            for eid in self._out.get(edge.from_id, []):
                existing = self._edges.get(eid)
                if existing and existing.to_id == edge.to_id and existing.edge_type == edge.edge_type:
                    raise GraphError(
                        f"duplicate edge triple: {edge.from_id!r} -{edge.edge_type.value}-> {edge.to_id!r}"
                    )
            self._edges[edge.edge_id] = edge
            self._out.setdefault(edge.from_id, []).append(edge.edge_id)
            self._out[edge.edge_id] = self._out.get(edge.edge_id, [])  # ensure dict entries
            self._in.setdefault(edge.to_id, []).append(edge.edge_id)

    def get_edge(self, edge_id: str) -> GraphEdge:
        with self._lock:
            e = self._edges.get(edge_id)
        if e is None:
            raise GraphError(f"unknown edge: {edge_id!r}")
        return e

    def get_edges(
        self,
        from_id: Optional[str] = None,
        to_id: Optional[str] = None,
        edge_type: Optional[EdgeType | str] = None,
    ) -> List[GraphEdge]:
        if isinstance(edge_type, str):
            try:
                edge_type = EdgeType(edge_type)
            except ValueError as exc:
                raise GraphError(f"Unknown edge type {edge_type!r}") from exc
        with self._lock:
            edges = list(self._edges.values())
        if from_id is not None:
            edges = [e for e in edges if e.from_id == from_id]
        if to_id is not None:
            edges = [e for e in edges if e.to_id == to_id]
        if edge_type is not None:
            edges = [e for e in edges if e.edge_type == edge_type]
        return sorted(edges, key=lambda e: e.edge_id)

    def remove_edge(self, edge_id: str) -> None:
        with self._lock:
            e = self._edges.pop(edge_id, None)
            if e is None:
                raise GraphError(f"unknown edge: {edge_id!r}")
            if e.edge_id in self._out.get(e.from_id, []):
                self._out[e.from_id].remove(e.edge_id)
            if e.edge_id in self._in.get(e.to_id, []):
                self._in[e.to_id].remove(e.edge_id)

    # -- traversal ---------------------------------------------------------
    def neighbors(self, node_id: str, direction: str = "out") -> List[GraphNode]:
        """Return neighboring nodes for ``node_id``.

        ``direction``: ``out`` (successors) | ``in`` (predecessors) | ``both``.
        Deterministic ordered by neighbor node_id.
        """
        if direction not in ("out", "in", "both"):
            raise GraphError("direction must be 'out', 'in', or 'both'")
        with self._lock:
            if node_id not in self._nodes:
                raise GraphError(f"unknown node: {node_id!r}")
            neighbor_ids: List[str] = []
            if direction in ("out", "both"):
                for eid in sorted(self._out.get(node_id, [])):
                    e = self._edges.get(eid)
                    if e:
                        neighbor_ids.append(e.to_id)
            if direction in ("in", "both"):
                for eid in sorted(self._in.get(node_id, [])):
                    e = self._edges.get(eid)
                    if e:
                        neighbor_ids.append(e.from_id)
            # dedup + deterministic
            seen: set = set()
            ordered: List[str] = []
            for nid in sorted(set(neighbor_ids)):
                if nid not in seen:
                    seen.add(nid)
                    ordered.append(nid)
            return [self._nodes[nid] for nid in ordered if nid in self._nodes]

    def find_path(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """Deterministic BFS shortest path (node_id list) or None if unreachable.

        BFS queue is ordered deterministically (neighbors sorted by node_id) so
        the same graph always yields the same path.
        """
        with self._lock:
            if from_id not in self._nodes:
                raise GraphError(f"unknown node: {from_id!r}")
            if to_id not in self._nodes:
                raise GraphError(f"unknown node: {to_id!r}")
            if from_id == to_id:
                return [from_id]
            visited: set = {from_id}
            parent: Dict[str, str] = {}
            queue: deque = deque([from_id])
            while queue:
                cur = queue.popleft()
                # deterministic neighbor order
                nbrs: List[str] = []
                for eid in sorted(self._out.get(cur, [])):
                    e = self._edges.get(eid)
                    if e:
                        nbrs.append(e.to_id)
                for nid in sorted(set(nbrs)):
                    if nid not in visited:
                        visited.add(nid)
                        parent[nid] = cur
                        if nid == to_id:
                            # reconstruct
                            path = [nid]
                            p = cur
                            while p != from_id:
                                path.append(p)
                                p = parent[p]
                            path.append(from_id)
                            path.reverse()
                            return path
                        queue.append(nid)
            return None

    def __len__(self) -> int:
        with self._lock:
            return len(self._nodes)

    @property
    def node_count(self) -> int:
        return len(self)

    @property
    def edge_count(self) -> int:
        with self._lock:
            return len(self._edges)

    def clear(self) -> None:
        with self._lock:
            self._nodes.clear()
            self._edges.clear()
            self._out.clear()
            self._in.clear()
