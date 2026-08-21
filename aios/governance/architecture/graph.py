"""Architecture dependency graph (TASK-016).

Builds Module A → Module B graph from scan results, supports traversal,
reverse dependency, cycle detection, forbidden edge detection, layer violation
detection, topological sort.

Layering: governance — stdlib only, no runtime/agent imports.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Tuple

from .guard import ALLOWED_IMPORT_LAYERS, LAYER_ORDER, classify_module


class ArchitectureGraphError(Exception):
    pass


class DependencyGraph:
    """Directed graph of module dependencies.

    Edge A → B means "A depends on B" (A imports B).
    """

    def __init__(self) -> None:
        self._edges: Dict[str, Set[str]] = defaultdict(set)
        self._nodes: Set[str] = set()
        # Keep layer info per node
        self._layers: Dict[str, str] = {}

    # ------------------------------------------------------------------ #
    # Construction
    # ------------------------------------------------------------------ #
    def add_node(self, node: str, layer: Optional[str] = None) -> None:
        self._nodes.add(node)
        self._edges.setdefault(node, set())
        if layer:
            self._layers[node] = layer
        elif node not in self._layers:
            self._layers[node] = classify_module(node)

    def add_edge(self, from_node: str, to_node: str) -> None:
        if from_node == to_node:
            # Self-loop is a cycle of length 1
            self._nodes.add(from_node)
            self._edges[from_node].add(to_node)
            self._layers.setdefault(from_node, classify_module(from_node))
            self._layers.setdefault(to_node, classify_module(to_node))
            return
        self._nodes.add(from_node)
        self._nodes.add(to_node)
        self._edges[from_node].add(to_node)
        self._edges.setdefault(to_node, set())
        self._layers.setdefault(from_node, classify_module(from_node))
        self._layers.setdefault(to_node, classify_module(to_node))

    def add_module_result(self, module_path: str, imports: List[str]) -> None:
        """Add a module and its imports as edges."""
        layer = classify_module(module_path)
        self.add_node(module_path, layer)
        for imp in imports:
            if imp and imp != "<dynamic>":
                self.add_edge(module_path, imp)

    @classmethod
    def from_scan_results(cls, scan_results) -> "DependencyGraph":
        """Build graph from list of ModuleScanResult."""
        g = cls()
        for r in scan_results:
            imports = [imp.name for imp in r.imports if imp.name and imp.name != "<dynamic>"]
            g.add_module_result(r.module_path, imports)
        return g

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #
    @property
    def nodes(self) -> Set[str]:
        return set(self._nodes)

    @property
    def edges(self) -> List[Tuple[str, str]]:
        result = []
        for src, dsts in self._edges.items():
            for dst in dsts:
                result.append((src, dst))
        return result

    def dependencies_of(self, node: str) -> Set[str]:
        return set(self._edges.get(node, set()))

    def dependents_of(self, node: str) -> Set[str]:
        """Reverse dependencies: who depends on node."""
        result = set()
        for src, dsts in self._edges.items():
            if node in dsts:
                result.add(src)
        return result

    def get_closure(self, node: str) -> Set[str]:
        """Transitive closure of dependencies (BFS)."""
        closure: Set[str] = set()
        queue = deque(self._edges.get(node, set()))
        while queue:
            cur = queue.popleft()
            if cur in closure:
                continue
            closure.add(cur)
            for nxt in self._edges.get(cur, set()):
                if nxt not in closure:
                    queue.append(nxt)
        return closure

    def reverse_closure(self, node: str) -> Set[str]:
        """Transitive reverse closure (who transitively depends on node)."""
        closure: Set[str] = set()
        queue = deque(self.dependents_of(node))
        while queue:
            cur = queue.popleft()
            if cur in closure:
                continue
            closure.add(cur)
            for nxt in self.dependents_of(cur):
                if nxt not in closure:
                    queue.append(nxt)
        return closure

    def traversal(self, start: str, order: str = "bfs") -> List[str]:
        """Traverse from start node."""
        visited: Set[str] = set()
        result: List[str] = []
        if order == "bfs":
            queue = deque([start])
            while queue:
                cur = queue.popleft()
                if cur in visited:
                    continue
                visited.add(cur)
                result.append(cur)
                for nxt in sorted(self._edges.get(cur, set())):
                    if nxt not in visited:
                        queue.append(nxt)
        else:  # dfs
            stack = [start]
            while stack:
                cur = stack.pop()
                if cur in visited:
                    continue
                visited.add(cur)
                result.append(cur)
                for nxt in sorted(self._edges.get(cur, set()), reverse=True):
                    if nxt not in visited:
                        stack.append(nxt)
        return result

    # ------------------------------------------------------------------ #
    # Cycle detection
    # ------------------------------------------------------------------ #
    def detect_cycle(self) -> Optional[List[str]]:
        """Detect a cycle via DFS. Returns cycle path or None."""
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

    def has_cycle(self) -> bool:
        return self.detect_cycle() is not None

    def find_all_cycles(self) -> List[List[str]]:
        """Find all cycles (up to 10 to avoid explosion)."""
        cycles: List[List[str]] = []
        # Use simple DFS with path tracking, limit to 10
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {n: WHITE for n in self._nodes}
        path: List[str] = []

        def dfs(node: str) -> None:
            if len(cycles) >= 10:
                return
            color[node] = GRAY
            path.append(node)
            for nxt in self._edges.get(node, ()):
                if len(cycles) >= 10:
                    break
                c = color.get(nxt, WHITE)
                if c == GRAY:
                    idx = path.index(nxt)
                    cycles.append(path[idx:] + [nxt])
                elif c == WHITE:
                    dfs(nxt)
            path.pop()
            color[node] = BLACK

        for node in list(self._nodes):
            if color[node] == WHITE:
                dfs(node)
                if len(cycles) >= 10:
                    break
        return cycles

    def topological_sort(self) -> List[str]:
        """Topological sort (Kahn). Raises if cycle exists."""
        cycle = self.detect_cycle()
        if cycle:
            raise ArchitectureGraphError(f"Cycle detected: {' -> '.join(cycle)}")
        in_degree: Dict[str, int] = {n: 0 for n in self._nodes}
        for src, dsts in self._edges.items():
            for dst in dsts:
                in_degree[dst] = in_degree.get(dst, 0) + 1
        queue = deque([n for n, d in in_degree.items() if d == 0])
        result: List[str] = []
        while queue:
            cur = queue.popleft()
            result.append(cur)
            for nxt in list(self._edges.get(cur, set())):
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)
        if len(result) != len(self._nodes):
            raise ArchitectureGraphError("Graph has cycle, topological sort impossible")
        return result

    # ------------------------------------------------------------------ #
    # Forbidden / layer checks
    # ------------------------------------------------------------------ #
    def find_forbidden_edges(self, forbidden: Dict[str, Set[str]]) -> List[Tuple[str, str, str]]:
        """Find edges that match forbidden source→target layer pairs.

        forbidden: {source_layer: {target_layer, ...}}
        Returns list of (from_node, to_node, reason).
        """
        violations: List[Tuple[str, str, str]] = []
        for src, dsts in self._edges.items():
            src_layer = self._layers.get(src, classify_module(src))
            for dst in dsts:
                dst_layer = self._layers.get(dst, classify_module(dst))
                if src_layer in forbidden and dst_layer in forbidden[src_layer]:
                    violations.append((src, dst, f"{src_layer} -> {dst_layer} forbidden"))
        return violations

    def find_layer_violations(self, allowed: Optional[Dict[str, List[str]]] = None) -> List[Tuple[str, str, str]]:
        """Find edges violating ALLOWED_IMPORT_LAYERS."""
        if allowed is None:
            allowed = ALLOWED_IMPORT_LAYERS
        violations: List[Tuple[str, str, str]] = []
        for src, dsts in self._edges.items():
            src_layer = self._layers.get(src, classify_module(src))
            if src_layer not in LAYER_ORDER:
                continue
            allowed_targets = allowed.get(src_layer, [])
            for dst in dsts:
                dst_layer = self._layers.get(dst, classify_module(dst))
                if dst_layer in LAYER_ORDER and dst_layer not in allowed_targets:
                    violations.append((src, dst, f"Layer '{src_layer}' imports '{dst_layer}' module '{dst}' (upward/skip)"))
        return violations

    def find_reverse_dependencies(self) -> List[Tuple[str, str, str]]:
        """Find reverse dependencies (lower layer importing higher layer).

        E.g., Tool → Agent, Runtime → Orchestrator, Capability → Agent.
        """
        reverse_forbidden = {
            "tool": {"agent", "orchestrator", "worker", "runtime", "skill", "capability"},
            "capability": {"agent", "orchestrator", "worker", "runtime", "skill"},
            "skill": {"agent", "orchestrator", "worker", "runtime"},
            "runtime": {"agent", "orchestrator", "worker"},
            "worker": {"agent", "orchestrator"},
            "orchestrator": {"agent"},
        }
        return self.find_forbidden_edges(reverse_forbidden)

    # ------------------------------------------------------------------ #
    # Serialization
    # ------------------------------------------------------------------ #
    def to_dict(self) -> Dict:
        return {
            "nodes": sorted(self._nodes),
            "edges": sorted(self.edges),
            "layers": dict(self._layers),
            "has_cycle": self.has_cycle(),
            "cycle": self.detect_cycle(),
        }

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, node: str) -> bool:
        return node in self._nodes


__all__ = ["DependencyGraph", "ArchitectureGraphError"]
