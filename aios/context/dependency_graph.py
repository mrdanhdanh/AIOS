"""Dependency Graph (TASK-119, M18).

Extracts dependency edges (import/require/call) from source, stores nodes +
edges, and detects cycles (T001 Rule 2 -> BLOCK). Deterministic. Fail-closed on
cycle. Provenance (T001 Rule 5). Secret isolation (T040/T113).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, Optional

from aios.governance.evidence.store import EvidenceStore

from .common import ContextError, SecretBoundary, emit_evidence, sha256


__all__ = [
    "DependencyGraphError",
    "DepNode",
    "DepEdge",
    "DependencyGraphResult",
    "DependencyGraph",
]


class DependencyGraphError(ContextError):
    """Raised when a dependency-graph invariant is violated (fail-closed)."""


@dataclass
class DepNode:
    id: str
    kind: str  # module | symbol
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "kind": self.kind, "content_hash": self.content_hash}


@dataclass
class DepEdge:
    frm: str
    to: str
    kind: str  # import | require | call

    def to_dict(self) -> dict[str, Any]:
        return {"from": self.frm, "to": self.to, "kind": self.kind}


@dataclass
class DependencyGraphResult:
    repo_ref: str
    nodes: list[DepNode]
    edges: list[DepEdge]
    has_cycle: bool
    graph_id: str
    evidence_ref: str
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_ref": self.repo_ref,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "has_cycle": self.has_cycle,
            "graph_id": self.graph_id,
            "evidence_ref": self.evidence_ref,
            "content_hash": self.content_hash,
        }


class DependencyGraph:
    """Edge extraction + graph store + cycle detection."""

    def __init__(
        self,
        *,
        evidence_store: Optional[EvidenceStore] = None,
        run_id: str = "run-context",
        task_id: str = "TASK-119",
        producer: str = "context.dependency_graph",
    ) -> None:
        self._store = evidence_store or EvidenceStore()
        self._run_id = run_id
        self._task_id = task_id
        self._producer = producer

    def _extract_python(self, source: str, module: str) -> tuple[list[DepNode], list[DepEdge]]:
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            raise DependencyGraphError(f"python parse failed for {module}: {exc}") from exc
        nodes = [DepNode(id=module, kind="module", content_hash=sha256(source))]
        edges: list[DepEdge] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = alias.name
                    nodes.append(DepNode(id=target, kind="module", content_hash=sha256(target)))
                    edges.append(DepEdge(frm=module, to=target, kind="import"))
            elif isinstance(node, ast.ImportFrom):
                target = node.module or ""
                if target:
                    nodes.append(DepNode(id=target, kind="module", content_hash=sha256(target)))
                    edges.append(DepEdge(frm=module, to=target, kind="import"))
            elif isinstance(node, ast.Call):
                func = node.func
                callee = func.attr if isinstance(func, ast.Attribute) else (
                    func.id if isinstance(func, ast.Name) else ""
                )
                if callee:
                    edges.append(DepEdge(frm=module, to=callee, kind="call"))
        return nodes, edges

    def build(
        self,
        sources: list[tuple[str, str, str]],
        *,
        policy_ref: str = "pol-context-dep",
    ) -> DependencyGraphResult:
        """``sources``: (source_text, module_name, language)."""
        all_nodes: list[DepNode] = []
        all_edges: list[DepEdge] = []
        for source, module, lang in sources:
            if SecretBoundary.is_secret_path(module):
                raise DependencyGraphError(f"refusing to graph secret module: {module}")
            if lang == "python":
                nodes, edges = self._extract_python(source, module)
            else:
                nodes = [DepNode(id=module, kind="module", content_hash=sha256(source))]
                edges = []
            all_nodes.extend(nodes)
            all_edges.extend(edges)
        # Dedupe nodes by id (keep first content_hash).
        seen: dict[str, DepNode] = {}
        for n in all_nodes:
            seen.setdefault(n.id, n)
        nodes = list(seen.values())
        has_cycle = self._detect_cycle(nodes, all_edges)
        graph_id = f"dep-{sha256(str(len(nodes)) + str(len(all_edges)))[:16]}"
        canonical = "\n".join(f"{e.frm}->{e.to}:{e.kind}" for e in all_edges)
        overall = sha256(canonical)
        evidence_ref = emit_evidence(
            self._store,
            task_id=self._task_id,
            run_id=self._run_id,
            producer=self._producer,
            type_="dependency_graph",
            source="graph",
            content=canonical,
        )
        return DependencyGraphResult(
            repo_ref="graph",
            nodes=nodes,
            edges=all_edges,
            has_cycle=has_cycle,
            graph_id=graph_id,
            evidence_ref=evidence_ref,
            content_hash=overall,
        )

    def _detect_cycle(self, nodes: list[DepNode], edges: list[DepEdge]) -> bool:
        """DFS cycle detection over import edges only (T001 Rule 2)."""
        adj: dict[str, list[str]] = {n.id: [] for n in nodes}
        for e in edges:
            if e.kind == "import":
                adj.setdefault(e.frm, []).append(e.to)
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {nid: WHITE for nid in adj}

        def dfs(u: str) -> bool:
            color[u] = GRAY
            for v in adj.get(u, []):
                cv = color.get(v, WHITE)
                if cv == GRAY:
                    return True
                if cv == WHITE and dfs(v):
                    return True
            color[u] = BLACK
            return False

        for nid in list(adj.keys()):
            if color[nid] == WHITE and dfs(nid):
                return True
        return False
