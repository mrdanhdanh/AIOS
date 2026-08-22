"""Parallel Scheduler — runs DAG nodes in parallel within boundaries.

AC-028-01: Operates through contracts.
AC-028-02: Nodes not dispatched before dependency satisfied.
AC-028-03: Parallel nodes dispatched when independent.
AC-028-11: Deterministic scheduling without LLM.
"""

from __future__ import annotations

import time
from typing import Any

from aios.parallel_scheduler.contracts import (
    DispatchDecision,
    JoinPolicy,
    ScheduledNode,
    SchedulerState,
)


class ParallelScheduler:
    """Schedules and dispatches DAG nodes respecting dependencies."""

    def __init__(self, join_policy: JoinPolicy = JoinPolicy.ALL_SUCCESS) -> None:
        self._state = SchedulerState.IDLE
        self._nodes: dict[str, ScheduledNode] = {}
        self._join_policy = join_policy
        self._dispatch_log: list[dict[str, Any]] = []

    @property
    def state(self) -> SchedulerState:
        return self._state

    def load_graph(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> None:
        """Load a graph for scheduling."""
        self._state = SchedulerState.IDLE
        self._nodes.clear()

        for n in nodes:
            self._nodes[n["node_id"]] = ScheduledNode(
                node_id=n["node_id"],
                dependencies=[],
            )

        for e in edges:
            target = e["target"]
            source = e["source"]
            if target in self._nodes:
                self._nodes[target].dependencies.append(source)

    def _dependencies_satisfied(self, node: ScheduledNode) -> bool:
        """Evaluate dependency satisfaction per the active JoinPolicy."""
        if not node.dependencies:
            return True
        dep_states = [
            self._nodes.get(d, ScheduledNode(state="pending")).state
            for d in node.dependencies
        ]
        if self._join_policy == JoinPolicy.ALL_SUCCESS:
            return all(s == "completed" for s in dep_states)
        if self._join_policy == JoinPolicy.ANY_SUCCESS:
            return any(s == "completed" for s in dep_states)
        if self._join_policy == JoinPolicy.ALL_COMPLETED:
            # All dependencies must have finished (completed or failed), none pending/running.
            return all(s in ("completed", "failed") for s in dep_states)
        return False

    def decision_for(self, node_id: str) -> DispatchDecision:
        """Return the dispatch decision for a node (AC-028 JoinPolicy variants)."""
        node = self._nodes.get(node_id)
        if node is None:
            return DispatchDecision.REJECTED
        if node.state != "pending":
            return DispatchDecision.BLOCKED
        if self._dependencies_satisfied(node):
            return DispatchDecision.READY
        return DispatchDecision.WAITING_DEPENDENCY

    def get_ready_nodes(self) -> list[str]:
        """Get nodes whose dependencies are satisfied per the active JoinPolicy."""
        ready = []
        for nid, node in self._nodes.items():
            if node.state != "pending":
                continue
            if self._dependencies_satisfied(node):
                ready.append(nid)
        return sorted(ready)  # Deterministic

    def dispatch(self, node_id: str) -> bool:
        """Dispatch a single node."""
        if node_id not in self._nodes:
            return False
        node = self._nodes[node_id]
        if node.state != "pending":
            return False

        # Verify dependencies
        for dep in node.dependencies:
            dep_node = self._nodes.get(dep)
            if dep_node is None or dep_node.state != "completed":
                return False

        node.state = "running"
        node.dispatch_time = time.time()
        self._state = SchedulerState.RUNNING
        self._dispatch_log.append({"node_id": node_id, "action": "dispatch", "time": node.dispatch_time})
        return True

    def complete(self, node_id: str) -> bool:
        """Mark a node as completed."""
        if node_id not in self._nodes:
            return False
        node = self._nodes[node_id]
        if node.state != "running":
            return False
        node.state = "completed"
        node.completion_time = time.time()
        self._dispatch_log.append({"node_id": node_id, "action": "complete", "time": node.completion_time})

        # Check if all done
        if all(n.state == "completed" for n in self._nodes.values()):
            self._state = SchedulerState.COMPLETED
        return True

    def dispatch_ready(self) -> list[str]:
        """Dispatch all ready nodes in parallel."""
        ready = self.get_ready_nodes()
        dispatched = []
        for nid in ready:
            if self.dispatch(nid):
                dispatched.append(nid)
        return dispatched

    def save_snapshot(self) -> dict[str, Any]:
        """Save scheduler state for resume."""
        return {
            "state": self._state.value,
            "nodes": {nid: {"state": n.state} for nid, n in self._nodes.items()},
        }

    def restore_snapshot(self, snapshot: dict[str, Any]) -> None:
        """Restore scheduler state from snapshot."""
        self._state = SchedulerState(snapshot["state"])
        for nid, data in snapshot.get("nodes", {}).items():
            if nid in self._nodes:
                self._nodes[nid].state = data["state"]

    def get_dispatch_log(self) -> list[dict[str, Any]]:
        return list(self._dispatch_log)
