"""Workflow validation — fail-closed (TASK-008)."""

from __future__ import annotations

from typing import Dict, List, Set

from .definition import ALLOWED_PERMISSIONS, WorkflowDefinition, WorkflowError


def _detect_cycle(nodes: List, edges: List) -> List[str] | None:
    adj: Dict[str, List[str]] = {n.id: [] for n in nodes}
    for e in edges:
        adj[e.from_id].append(e.to_id)
    visited: Set[str] = set()
    stack: Set[str] = set()
    parent: Dict[str, str] = {}
    cycle: List[str] | None = None

    def dfs(u: str) -> bool:
        nonlocal cycle
        visited.add(u)
        stack.add(u)
        for v in adj.get(u, []):
            if v not in visited:
                parent[v] = u
                if dfs(v):
                    return True
            elif v in stack:
                path = [v]
                cur = u
                while cur != v:
                    path.append(cur)
                    cur = parent.get(cur, "")
                    if not cur:
                        break
                path.append(v)
                path.reverse()
                cycle = path
                return True
        stack.remove(u)
        return False

    for n in nodes:
        if n.id not in visited:
            if dfs(n.id):
                break
    return cycle


def validate_definition(wd: WorkflowDefinition) -> None:
    from aios.core.version import SemVer, VersionError

    try:
        SemVer.parse(wd.version)
    except VersionError as exc:
        raise WorkflowError(f"workflow.version invalid SemVer {wd.version!r}: {exc}") from exc
    if not wd.name or not wd.name.strip():
        raise WorkflowError("workflow.name must be non-empty")
    seen: Set[str] = set()
    for n in wd.nodes:
        n.validate()
        if n.id in seen:
            raise WorkflowError(f"duplicate node id {n.id!r}")
        seen.add(n.id)
    edge_set: Set[tuple] = set()
    for e in wd.edges:
        e.validate()
        if e.from_id not in seen:
            raise WorkflowError(f"edge from {e.from_id!r} references unknown node")
        if e.to_id not in seen:
            raise WorkflowError(f"edge to {e.to_id!r} references unknown node")
        key = (e.from_id, e.to_id)
        if key in edge_set:
            raise WorkflowError(f"duplicate edge {key}")
        edge_set.add(key)
    if wd.nodes and wd.edges:
        cycle = _detect_cycle(wd.nodes, wd.edges)
        if cycle is not None:
            raise WorkflowError(f"cycle detected: {' -> '.join(cycle)}")
    if len(wd.permissions) != len(set(wd.permissions)):
        raise WorkflowError("duplicate permission entries")
    for p in wd.permissions:
        if p not in ALLOWED_PERMISSIONS:
            raise WorkflowError(f"permission {p!r} not allowed")
    if wd.resources is not None:
        wd.resources.validate()
    if wd.retries < 0:
        raise WorkflowError("retries must be >= 0")
    if wd.timeout <= 0:
        raise WorkflowError("timeout must be > 0")
