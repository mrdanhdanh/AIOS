"""Graph Compiler — compiles ExecutionPlan to acyclic DAG.

AC-027-01: ExecutionPlan → ExecutionGraph.
AC-027-02: Always acyclic.
AC-027-04: Self-loop rejected.
AC-027-07: Entry/terminal identified.
AC-027-08: Topological ordering.
AC-027-13: Does not execute tasks.
"""

from __future__ import annotations

from typing import Any

from aios.execution_graph.contracts import ExecutionGraph, GraphEdge, GraphNode, NodeState


class GraphCompiler:
    """Compiles ExecutionPlan into an acyclic ExecutionGraph."""

    def compile(self, plan_data: dict[str, Any]) -> ExecutionGraph:
        """Compile plan data into ExecutionGraph.

        Args:
            plan_data: Dict with 'plan_id', 'steps' (list of dicts with 'step_id', 'name', 'dependencies', etc.)
        """
        plan_id = plan_data.get("plan_id", "")
        steps = plan_data.get("steps", [])

        # Create nodes
        nodes = []
        for step in steps:
            nodes.append(GraphNode(
                node_id=step["step_id"],
                name=step.get("name", step["step_id"]),
                capabilities=step.get("required_capabilities", []),
            ))

        # Create edges from dependencies
        edges = []
        for step in steps:
            for dep in step.get("dependencies", []):
                edges.append(GraphEdge(source=dep, target=step["step_id"]))

        # Validate
        self._validate_graph(nodes, edges)

        # Find entry and terminal nodes
        all_targets = {e.target for e in edges}
        all_sources = {e.source for e in edges}
        entry_nodes = [n.node_id for n in nodes if n.node_id not in all_targets]
        terminal_nodes = [n.node_id for n in nodes if n.node_id not in all_sources]

        # Topological sort
        topo_order = self._topological_sort(nodes, edges)

        graph = ExecutionGraph(
            graph_id=f"graph-{plan_id}",
            nodes=nodes,
            edges=edges,
            entry_nodes=entry_nodes,
            terminal_nodes=terminal_nodes,
            topological_order=topo_order,
            provenance=[f"graph_compiler:{plan_id}"],
        )
        graph.compute_hash()
        return graph

    def _validate_graph(self, nodes: list[GraphNode], edges: list[GraphEdge]) -> None:
        """Validate graph: no cycles, no self-loops, no missing refs."""
        node_ids = {n.node_id for n in nodes}

        # Self-loops
        for e in edges:
            if e.source == e.target:
                raise ValueError(f"Self-loop detected: {e.source}")

        # Missing references
        for e in edges:
            if e.source not in node_ids:
                raise ValueError(f"Missing source node: {e.source}")
            if e.target not in node_ids:
                raise ValueError(f"Missing target node: {e.target}")

        # Cycle detection
        if self._has_cycle(nodes, edges):
            raise ValueError("Cycle detected in graph")

    def _has_cycle(self, nodes: list[GraphNode], edges: list[GraphEdge]) -> bool:
        """DFS-based cycle detection."""
        graph: dict[str, list[str]] = {n.node_id: [] for n in nodes}
        for e in edges:
            graph[e.source].append(e.target)

        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(node)
            return False

        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def _topological_sort(self, nodes: list[GraphNode], edges: list[GraphEdge]) -> list[str]:
        """Kahn's algorithm for topological sort."""
        in_degree: dict[str, int] = {n.node_id: 0 for n in nodes}
        adj: dict[str, list[str]] = {n.node_id: [] for n in nodes}

        for e in edges:
            adj[e.source].append(e.target)
            in_degree[e.target] = in_degree.get(e.target, 0) + 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        result: list[str] = []

        while queue:
            queue.sort()  # Deterministic
            node = queue.pop(0)
            result.append(node)
            for neighbor in adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result
