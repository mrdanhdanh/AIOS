"""Tests for execution graph compiler."""

from __future__ import annotations

import pytest

from aios.execution_graph.compiler import GraphCompiler
from aios.execution_graph.contracts import ExecutionGraph, NodeState


class TestGraphCompiler:
    def _make_plan(self, steps: list[dict] | None = None) -> dict:
        if steps is None:
            steps = [
                {"step_id": "s1", "name": "analyze"},
                {"step_id": "s2", "name": "implement", "dependencies": ["s1"]},
                {"step_id": "s3", "name": "test", "dependencies": ["s2"]},
            ]
        return {"plan_id": "test-plan", "steps": steps}

    def test_compile_basic(self) -> None:
        compiler = GraphCompiler()
        graph = compiler.compile(self._make_plan())
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2

    def test_entry_nodes(self) -> None:
        compiler = GraphCompiler()
        graph = compiler.compile(self._make_plan())
        assert "s1" in graph.entry_nodes

    def test_terminal_nodes(self) -> None:
        compiler = GraphCompiler()
        graph = compiler.compile(self._make_plan())
        assert "s3" in graph.terminal_nodes

    def test_topological_order(self) -> None:
        compiler = GraphCompiler()
        graph = compiler.compile(self._make_plan())
        assert graph.topological_order.index("s1") < graph.topological_order.index("s2")
        assert graph.topological_order.index("s2") < graph.topological_order.index("s3")

    def test_cycle_rejected(self) -> None:
        compiler = GraphCompiler()
        plan = self._make_plan(steps=[
            {"step_id": "a", "dependencies": ["b"]},
            {"step_id": "b", "dependencies": ["a"]},
        ])
        with pytest.raises(ValueError, match="Cycle"):
            compiler.compile(plan)

    def test_self_loop_rejected(self) -> None:
        compiler = GraphCompiler()
        plan = self._make_plan(steps=[
            {"step_id": "a", "dependencies": ["a"]},
        ])
        with pytest.raises(ValueError, match="Self-loop"):
            compiler.compile(plan)

    def test_missing_ref_rejected(self) -> None:
        compiler = GraphCompiler()
        plan = self._make_plan(steps=[
            {"step_id": "a", "dependencies": ["nonexistent"]},
        ])
        with pytest.raises(ValueError, match="Missing"):
            compiler.compile(plan)

    def test_deterministic(self) -> None:
        compiler = GraphCompiler()
        g1 = compiler.compile(self._make_plan())
        g2 = compiler.compile(self._make_plan())
        assert g1.topological_order == g2.topological_order
        assert g1.content_hash == g2.content_hash

    def test_compute_hash(self) -> None:
        compiler = GraphCompiler()
        graph = compiler.compile(self._make_plan())
        assert graph.content_hash
        assert len(graph.content_hash) == 16

    def test_get_node(self) -> None:
        compiler = GraphCompiler()
        graph = compiler.compile(self._make_plan())
        node = graph.get_node("s1")
        assert node is not None
        assert node.name == "analyze"

    def test_get_successors(self) -> None:
        compiler = GraphCompiler()
        graph = compiler.compile(self._make_plan())
        successors = graph.get_successors("s1")
        assert "s2" in successors

    def test_get_predecessors(self) -> None:
        compiler = GraphCompiler()
        graph = compiler.compile(self._make_plan())
        preds = graph.get_predecessors("s3")
        assert "s2" in preds

    def test_to_dict(self) -> None:
        compiler = GraphCompiler()
        graph = compiler.compile(self._make_plan())
        d = graph.to_dict()
        assert "node_count" in d
        assert "topological_order" in d

    def test_parallel_nodes(self) -> None:
        compiler = GraphCompiler()
        plan = self._make_plan(steps=[
            {"step_id": "a", "name": "a"},
            {"step_id": "b", "name": "b"},
            {"step_id": "c", "name": "c", "dependencies": ["a", "b"]},
        ])
        graph = compiler.compile(plan)
        assert "a" in graph.entry_nodes
        assert "b" in graph.entry_nodes
