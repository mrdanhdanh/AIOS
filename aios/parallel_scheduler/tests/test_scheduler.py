"""Tests for parallel scheduler."""

from __future__ import annotations

import pytest

from aios.parallel_scheduler.contracts import JoinPolicy, SchedulerState
from aios.parallel_scheduler.scheduler import ParallelScheduler


class TestParallelScheduler:
    def _make_dag(self) -> tuple[list[dict], list[dict]]:
        nodes = [
            {"node_id": "a"}, {"node_id": "b"}, {"node_id": "c"},
        ]
        edges = [
            {"source": "a", "target": "c"},
            {"source": "b", "target": "c"},
        ]
        return nodes, edges

    def test_load_graph(self) -> None:
        sched = ParallelScheduler()
        nodes, edges = self._make_dag()
        sched.load_graph(nodes, edges)
        assert sched.state == SchedulerState.IDLE

    def test_get_ready_nodes(self) -> None:
        sched = ParallelScheduler()
        nodes, edges = self._make_dag()
        sched.load_graph(nodes, edges)
        ready = sched.get_ready_nodes()
        assert "a" in ready
        assert "b" in ready
        assert "c" not in ready

    def test_dispatch(self) -> None:
        sched = ParallelScheduler()
        nodes, edges = self._make_dag()
        sched.load_graph(nodes, edges)
        assert sched.dispatch("a") is True

    def test_dispatch_requires_deps(self) -> None:
        sched = ParallelScheduler()
        nodes, edges = self._make_dag()
        sched.load_graph(nodes, edges)
        assert sched.dispatch("c") is False  # a, b not completed

    def test_dispatch_ready_parallel(self) -> None:
        sched = ParallelScheduler()
        nodes, edges = self._make_dag()
        sched.load_graph(nodes, edges)
        dispatched = sched.dispatch_ready()
        assert "a" in dispatched
        assert "b" in dispatched
        assert "c" not in dispatched

    def test_complete_and_dispatch_chain(self) -> None:
        sched = ParallelScheduler()
        nodes, edges = self._make_dag()
        sched.load_graph(nodes, edges)
        sched.dispatch_ready()
        sched.complete("a")
        sched.complete("b")
        ready = sched.get_ready_nodes()
        assert "c" in ready

    def test_full_execution(self) -> None:
        sched = ParallelScheduler()
        nodes, edges = self._make_dag()
        sched.load_graph(nodes, edges)
        # Round 1
        sched.dispatch_ready()
        sched.complete("a")
        sched.complete("b")
        # Round 2
        sched.dispatch_ready()
        sched.complete("c")
        assert sched.state == SchedulerState.COMPLETED

    def test_snapshot_and_restore(self) -> None:
        sched = ParallelScheduler()
        nodes, edges = self._make_dag()
        sched.load_graph(nodes, edges)
        sched.dispatch("a")
        snapshot = sched.save_snapshot()
        sched.restore_snapshot(snapshot)
        assert sched.state == SchedulerState.RUNNING

    def test_dispatch_log(self) -> None:
        sched = ParallelScheduler()
        nodes, edges = self._make_dag()
        sched.load_graph(nodes, edges)
        sched.dispatch("a")
        log = sched.get_dispatch_log()
        assert len(log) >= 1

    def test_nonexistent_node(self) -> None:
        sched = ParallelScheduler()
        assert sched.dispatch("nonexistent") is False
