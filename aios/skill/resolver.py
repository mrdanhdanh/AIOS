"""Skill Dependency Resolver — resolve direct + transitive dependencies (TASK-015, M2).

Resolver builds dependency graph, detects cycles, checks version constraints
and conflicts, and returns topological order. Fail-closed on cycle/conflict/missing.

Layering: ``skill`` layer — stdlib + ``aios.core`` only.
Never imports ``runtime`` / ``agent`` / ``orchestrator`` / ``capability`` / ``tool``.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from .contracts import SkillContract, SkillDependency, SkillError
from .registry import SkillRegistry

__all__ = ["SkillDependencyResolver", "ResolverError", "DependencyGraph", "ResolutionResult"]


class ResolverError(Exception):
    """Raised on resolver errors (cycle, conflict, missing)."""


class DependencyGraph:
    """Directed graph for skill dependencies: A -> B means A depends on B."""

    def __init__(self) -> None:
        self._edges: Dict[str, Set[str]] = {}
        self._nodes: Set[str] = set()

    def add_node(self, skill_id: str) -> None:
        self._nodes.add(skill_id)
        self._edges.setdefault(skill_id, set())

    def add_edge(self, from_id: str, to_id: str) -> None:
        if from_id == to_id:
            raise ResolverError(f"Skill '{from_id}' cannot depend on itself")
        self._nodes.add(from_id)
        self._nodes.add(to_id)
        self._edges.setdefault(from_id, set()).add(to_id)
        self._edges.setdefault(to_id, set())

    def dependencies_of(self, skill_id: str) -> Set[str]:
        return set(self._edges.get(skill_id, set()))

    def get_closure(self, skill_id: str) -> Set[str]:
        closure: Set[str] = set()
        stack = list(self._edges.get(skill_id, set()))
        while stack:
            dep = stack.pop()
            if dep in closure:
                continue
            closure.add(dep)
            stack.extend(self._edges.get(dep, set()))
        return closure

    def detect_cycle(self) -> Optional[List[str]]:
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {n: WHITE for n in self._nodes}
        path: List[str] = []

        def dfs(node: str) -> Optional[List[str]]:
            color[node] = GRAY
            path.append(node)
            for nxt in self._edges.get(node, ()):
                c = color.get(nxt, WHITE)
                if c == GRAY:
                    idx = path.index(nxt)
                    return path[idx:] + [nxt]
                if c == WHITE:
                    found = dfs(nxt)
                    if found:
                        return found
            path.pop()
            color[node] = BLACK
            return None

        for node in list(self._nodes):
            if color[node] == WHITE:
                found = dfs(node)
                if found:
                    return found
        return None

    def topological_sort(self) -> List[str]:
        """Return topological order (dependencies before dependents)."""
        visited: Set[str] = set()
        order: List[str] = []
        temp: Set[str] = set()

        def visit(node: str) -> None:
            if node in visited:
                return
            if node in temp:
                raise ResolverError(f"Cycle detected at {node!r}")
            temp.add(node)
            for dep in self._edges.get(node, set()):
                visit(dep)
            temp.remove(node)
            visited.add(node)
            order.append(node)

        for node in sorted(self._nodes):
            if node not in visited:
                visit(node)
        return order

    def nodes(self) -> Set[str]:
        return set(self._nodes)

    def edges(self) -> Dict[str, Set[str]]:
        return {k: set(v) for k, v in self._edges.items()}


class ResolutionResult:
    """Result of dependency resolution."""

    def __init__(
        self,
        skill_id: str,
        resolved: List[str],
        order: List[str],
        graph: DependencyGraph,
        conflicts: Optional[List[str]] = None,
    ) -> None:
        self.skill_id = skill_id
        self.resolved = resolved  # all skill_ids in closure + root
        self.order = order  # topological order
        self.graph = graph
        self.conflicts = conflicts or []

    @property
    def is_success(self) -> bool:
        return len(self.conflicts) == 0

    def to_dict(self) -> Dict[str, object]:
        return {
            "skill_id": self.skill_id,
            "resolved": list(self.resolved),
            "order": list(self.order),
            "conflicts": list(self.conflicts),
            "graph": {k: sorted(v) for k, v in self.graph.edges().items()},
        }


class SkillDependencyResolver:
    """Resolves skill dependencies against a registry."""

    def __init__(self, registry: Optional[SkillRegistry] = None) -> None:
        self._registry = registry if registry is not None else SkillRegistry()

    @property
    def registry(self) -> SkillRegistry:
        return self._registry

    def resolve(self, skill_id: str, available: Optional[Dict[str, SkillContract]] = None) -> ResolutionResult:
        """Resolve dependencies for ``skill_id``.

        Args:
            skill_id: root skill to resolve.
            available: optional mapping skill_id -> SkillContract for skills not yet registered
                       (e.g., during install of new skill with its dependencies).

        Returns:
            ResolutionResult with topological order.

        Raises:
            ResolverError on cycle, missing dependency, or version conflict.
        """
        # Collect all contracts: registry + available
        all_contracts: Dict[str, SkillContract] = {}
        for c in self._registry.list():
            all_contracts[c.skill_id] = c
        if available:
            for sid, c in available.items():
                all_contracts[sid] = c

        if skill_id not in all_contracts:
            raise ResolverError(f"Unknown skill: {skill_id!r}")

        graph = DependencyGraph()
        # BFS to collect transitive dependencies
        to_visit: List[str] = [skill_id]
        visited: Set[str] = set()
        conflicts: List[str] = []

        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            visited.add(current)
            graph.add_node(current)

            contract = all_contracts.get(current)
            if contract is None:
                raise ResolverError(f"Missing dependency: {current!r} required but not found")

            for dep in contract.dependencies:
                dep_id = dep.skill_id
                graph.add_edge(current, dep_id)

                # Check if dependency exists
                dep_contract = all_contracts.get(dep_id)
                if dep_contract is None:
                    raise ResolverError(f"Missing dependency: {dep_id!r} required by {current!r} but not found")

                # Check version constraint
                if not dep.is_satisfied_by(dep_contract.version):
                    conflicts.append(
                        f"Version conflict: {current!r} requires {dep_id!r} {dep.version_constraint!r} but found {dep_contract.version!r}"
                    )

                if dep_id not in visited:
                    to_visit.append(dep_id)

        # Check for cycles
        cycle = graph.detect_cycle()
        if cycle:
            raise ResolverError(f"Circular dependency detected: {' -> '.join(cycle)}")

        if conflicts:
            raise ResolverError(f"Dependency conflicts: {'; '.join(conflicts)}")

        # Topological order
        try:
            order = graph.topological_sort()
        except ResolverError as exc:
            raise ResolverError(str(exc)) from exc

        return ResolutionResult(
            skill_id=skill_id,
            resolved=sorted(visited),
            order=order,
            graph=graph,
        )

    def check_compatibility(self, skill_id: str, available: Optional[Dict[str, SkillContract]] = None) -> bool:
        """Return True if dependencies are resolvable without error."""
        try:
            self.resolve(skill_id, available=available)
            return True
        except ResolverError:
            return False

    def get_transitive_dependencies(self, skill_id: str, available: Optional[Dict[str, SkillContract]] = None) -> Set[str]:
        """Return transitive closure of dependencies."""
        result = self.resolve(skill_id, available=available)
        closure = set(result.resolved)
        closure.discard(skill_id)
        return closure

    def has_cycle(self, skill_id: str, available: Optional[Dict[str, SkillContract]] = None) -> bool:
        try:
            self.resolve(skill_id, available=available)
            return False
        except ResolverError as exc:
            return "Circular" in str(exc) or "Cycle" in str(exc)
