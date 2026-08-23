"""TASK-205 — Artifact Lineage (M26).

Artifact lineage / provenance graph, converging Artifact (T130) and Evidence
(T001 Rule 5). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from aios.coding_edition._common import CodingEditionError, _hash


@dataclass
class LineageNode:
    """A node in the artifact lineage DAG (T205)."""

    artifact_id: str
    producer: str
    content_hash: str
    parents: tuple = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.artifact_id:
            raise CodingEditionError("artifact_id is required (T001 Rule 1, immutable).")
        if not self.content_hash:
            raise CodingEditionError("content_hash is required (provenance).")


class ArtifactLineage:
    """Deterministic artifact lineage tracker (T205)."""

    def __init__(self) -> None:
        self._nodes: Dict[str, LineageNode] = {}

    def record(self, producer: str, content: str, parents: Optional[List[str]] = None) -> LineageNode:
        """Record a new artifact with provenance (fail-closed)."""
        parents = parents or []
        for p in parents:
            if p not in self._nodes:
                raise CodingEditionError(f"parent artifact not found: {p}")
        node = LineageNode(
            artifact_id=f"art-{uuid.uuid4().hex[:10]}",
            producer=producer,
            content_hash=_hash(content),
            parents=tuple(parents),
        )
        self._nodes[node.artifact_id] = node
        return node

    def get(self, artifact_id: str) -> LineageNode:
        if artifact_id not in self._nodes:
            raise CodingEditionError(f"artifact not found: {artifact_id}")
        return self._nodes[artifact_id]

    def get_chain(self, artifact_id: str) -> List[LineageNode]:
        """Return the full provenance chain (ancestors first, deterministic)."""
        if artifact_id not in self._nodes:
            raise CodingEditionError(f"artifact not found: {artifact_id}")
        chain: List[LineageNode] = []
        seen: set = set()
        frontier = [artifact_id]
        while frontier:
            nid = frontier.pop(0)
            if nid in seen:
                continue
            seen.add(nid)
            node = self._nodes[nid]
            chain.append(node)
            frontier.extend(node.parents)
        # Deterministic order: by artifact_id.
        return sorted(chain, key=lambda n: n.artifact_id)

    def provenance_hash(self, artifact_id: str) -> str:
        chain = self.get_chain(artifact_id)
        payload = "|".join(f"{n.artifact_id}:{n.content_hash}" for n in chain)
        return _hash(payload)
