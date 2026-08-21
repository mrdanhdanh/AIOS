"""Circular dependency detection tests (TASK-016 16.11)."""

import pytest

from aios.governance.architecture.graph import DependencyGraph
from aios.governance.architecture.rules import evaluate_graph


def _build(edges):
    g = DependencyGraph()
    for src, dst in edges:
        g.add_edge(src, dst)
    return g


class TestCycleDetection:
    def test_no_cycle(self):
        g = _build([
            ("a", "b"),
            ("b", "c"),
            ("a", "c"),
        ])
        assert g.detect_cycle() is None
        assert not g.has_cycle()

    def test_simple_cycle(self):
        g = _build([
            ("a", "b"),
            ("b", "c"),
            ("c", "a"),
        ])
        cycle = g.detect_cycle()
        assert cycle is not None
        # Cycle must be closed
        assert cycle[0] == cycle[-1]

    def test_self_loop(self):
        g = DependencyGraph()
        g.add_edge("a", "a")
        assert g.detect_cycle() is not None

    def test_two_cycles(self):
        g = _build([
            ("a", "b"), ("b", "a"),
            ("x", "y"), ("y", "x"),
        ])
        cycles = g.find_all_cycles()
        assert len(cycles) >= 2

    def test_topological_sort_raises_on_cycle(self):
        g = _build([("a", "b"), ("b", "a")])
        with pytest.raises(Exception):
            g.topological_sort()


class TestCycleInGraphEval:
    def test_cycle_produces_violation(self):
        g = _build([
            ("aios/agents/a.py", "aios/orchestrator/b.py"),
            ("aios/orchestrator/b.py", "aios/agents/a.py"),
        ])
        vs = evaluate_graph(g)
        assert any(v.rule_id == "ARCH-D-001" for v in vs)


class TestPackageLevelCycle:
    def test_package_cycle(self):
        g = DependencyGraph()
        g.add_edge("aios/foo/__init__.py", "aios/bar/__init__.py")
        g.add_edge("aios/bar/__init__.py", "aios/foo/__init__.py")
        assert g.detect_cycle() is not None
