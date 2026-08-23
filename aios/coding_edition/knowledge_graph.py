"""TASK-211 — Repository Knowledge Graph Integration (M26).

Integrate repository structure into a knowledge graph, converging Repository
Scanner (T117) and Knowledge Index (T007). Deterministic, fail-closed,
provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from aios.coding_edition._common import CodingEditionError, _hash


@dataclass
class RepoNode:
    """A node in the repository knowledge graph (T211)."""

    node_id: str
    kind: str  # module | symbol | file
    label: str

    def __post_init__(self) -> None:
        if not self.node_id:
            raise CodingEditionError("node_id is required (T001 Rule 1, immutable).")
        if not self.kind:
            raise CodingEditionError("node kind is required.")


class RepoKnowledgeGraph:
    """Deterministic repository knowledge graph (T211)."""

    def __init__(self, graph_id: Optional[str] = None) -> None:
        self._graph_id = graph_id or f"rkg-{uuid.uuid4().hex[:12]}"
        self._nodes: Dict[str, RepoNode] = {}
        self._edges: Dict[str, Set[str]] = {}

    @property
    def graph_id(self) -> str:
        return self._graph_id

    def ingest(self, nodes: List[RepoNode], edges: Optional[Dict[str, List[str]]] = None) -> None:
        """Ingest a repository scan (fail-closed)."""
        for n in nodes:
            self._nodes[n.node_id] = n
        for src, dsts in (edges or {}).items():
            if src not in self._nodes:
                raise CodingEditionError(f"edge source not ingested: {src}")
            for d in dsts:
                if d not in self._nodes:
                    raise CodingEditionError(f"edge target not ingested: {d}")
            self._edges[src] = set(dsts)

    def query(self, kind: Optional[str] = None) -> List[RepoNode]:
        """Query nodes, optionally filtered by kind (deterministic order)."""
        result = [n for n in self._nodes.values() if kind is None or n.kind == kind]
        return sorted(result, key=lambda n: n.node_id)

    def neighbors(self, node_id: str) -> List[str]:
        if node_id not in self._nodes:
            raise CodingEditionError(f"node not found: {node_id}")
        return sorted(self._edges.get(node_id, set()))

    def graph_hash(self) -> str:
        nodes = "|".join(f"{n.node_id}:{n.kind}" for n in sorted(self._nodes.values(), key=lambda x: x.node_id))
        edges = "|".join(f"{k}->{','.join(sorted(v))}" for k, v in sorted(self._edges.items()))
        return _hash(f"{self._graph_id}|{nodes}|{edges}")
