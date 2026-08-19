"""Dependency graph implementation (Rule 2)."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set, Tuple


class CycleError(Exception):
    """Raised when a cyclic dependency is detected."""


class DependencyGraph:
    """Directed dependency graph of tasks.

    Edge ``A -> B`` means "A depends on B". The graph supports transitive
    closure computation, cycle detection and a readiness check driven by a
    status lookup function.
    """

    def __init__(self) -> None:
        # task_id -> set of task_ids it depends on
        self._edges: Dict[str, Set[str]] = {}

    # ------------------------------------------------------------------ #
    # Construction
    # ------------------------------------------------------------------ #
    def add_task(self, task_id: str, dependencies: Optional[Iterable[str]] = None) -> None:
        self._edges.setdefault(task_id, set())
        for dep in dependencies or []:
            self.add_edge(task_id, dep)

    def add_edge(self, task_id: str, depends_on: str) -> None:
        if task_id == depends_on:
            raise CycleError(f"Task '{task_id}' cannot depend on itself.")
        self._edges.setdefault(task_id, set()).add(depends_on)
        self._edges.setdefault(depends_on, set())

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #
    def dependencies_of(self, task_id: str) -> Set[str]:
        return set(self._edges.get(task_id, set()))

    def get_closure(self, task_id: str) -> Set[str]:
        """Return the full transitive dependency closure of ``task_id``.

        The closure does NOT include ``task_id`` itself (it is the set of tasks
        that must PASS before ``task_id`` may proceed).
        """
        closure: Set[str] = set()
        stack = list(self._edges.get(task_id, set()))
        while stack:
            dep = stack.pop()
            if dep in closure:
                continue
            closure.add(dep)
            stack.extend(self._edges.get(dep, set()))
        return closure

    def detect_cycle(self) -> Optional[List[str]]:
        """Detect a cycle. Returns the cycle path (node list) or ``None``."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {n: WHITE for n in self._edges}
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

        for node in list(self._edges):
            if color[node] == WHITE:
                found = dfs(node)
                if found:
                    return found
        return None

    def is_ready(self, task_id: str, status_fn) -> Tuple[bool, Optional[str]]:
        """Return (ready, blocking_task).

        ``ready`` is True only when every task in the dependency closure reports
        a ``PASS`` status via ``status_fn(task_id) -> str``. If not ready, the
        first non-PASS dependency encountered is returned as the blocker.
        """
        for dep in self.get_closure(task_id):
            if status_fn(dep) != "PASS":
                return False, dep
        return True, None

    def reachability(self) -> Dict[str, Set[str]]:
        """Map every task to its full closure (convenience)."""
        return {t: self.get_closure(t) for t in self._edges}
