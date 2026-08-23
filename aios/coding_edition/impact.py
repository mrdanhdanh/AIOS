"""TASK-210 — Change Impact Analysis (M26).

Compute the blast radius of a code change, converging Dependency Graph (T119)
and Context Retriever (T121). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from aios.coding_edition._common import CodingEditionError, _hash


@dataclass
class DependencyEdge:
    """A directed dependency: ``src`` depends on ``dst`` (T210)."""

    src: str
    dst: str

    def __post_init__(self) -> None:
        if not self.src or not self.dst:
            raise CodingEditionError("edge endpoints are required.")


class ImpactAnalyzer:
    """Deterministic change impact analyzer (T210)."""

    def __init__(self, run_id: Optional[str] = None) -> None:
        self._run_id = run_id or f"imp-{uuid.uuid4().hex[:12]}"
        self._edges: List[DependencyEdge] = []

    @property
    def run_id(self) -> str:
        return self._run_id

    def add_edge(self, src: str, dst: str) -> None:
        self._edges.append(DependencyEdge(src=src, dst=dst))

    def analyze(self, changed: List[str]) -> Set[str]:
        """Return the set of nodes impacted by ``changed`` (fail-closed).

        A node is impacted if it (transitively) depends on a changed node.
        """
        # Build reverse adjacency: dependents[dst] = set of src that depend on dst.
        dependents: Dict[str, Set[str]] = {}
        for e in self._edges:
            dependents.setdefault(e.dst, set()).add(e.src)
        impacted: Set[str] = set()
        frontier = list(changed)
        while frontier:
            node = frontier.pop(0)
            for dep in dependents.get(node, set()):
                if dep not in impacted:
                    impacted.add(dep)
                    frontier.append(dep)
        return impacted

    def analyzer_hash(self, changed: List[str]) -> str:
        impacted = self.analyze(changed)
        payload = "|".join(sorted(impacted))
        return _hash(f"{self._run_id}|{payload}")
