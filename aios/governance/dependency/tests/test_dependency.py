"""Automated tests for the Dependency Graph gate (Rule 2)."""

import pytest

from aios.governance.dependency import CycleError, DependencyGraph


def _status_table(passed):
    def fn(tid):
        return "PASS" if tid in passed else "BLOCKED"
    return fn


def test_closure_is_transitive():
    g = DependencyGraph()
    g.add_task("TASK-002", ["TASK-001"])
    g.add_task("TASK-003", ["TASK-002"])
    g.add_task("TASK-004", ["TASK-002", "TASK-001"])
    assert g.get_closure("TASK-003") == {"TASK-002", "TASK-001"}
    assert g.get_closure("TASK-004") == {"TASK-002", "TASK-001"}


def test_task_runs_when_dependency_not_passed_is_blocked():
    """Rule 2: a task whose dependency has not PASSED must be BLOCKED."""
    g = DependencyGraph()
    g.add_task("TASK-002", ["TASK-001"])
    # TASK-001 has not passed.
    ready, blocker = g.is_ready("TASK-002", _status_table(set()))
    assert ready is False
    assert blocker == "TASK-001"


def test_task_ready_when_closure_passes():
    g = DependencyGraph()
    g.add_task("TASK-002", ["TASK-001"])
    g.add_task("TASK-003", ["TASK-002"])
    passed = {"TASK-001", "TASK-002", "TASK-003"}
    ready, blocker = g.is_ready("TASK-003", _status_table(passed))
    assert ready is True
    assert blocker is None


def test_self_dependency_raises():
    g = DependencyGraph()
    with pytest.raises(CycleError):
        g.add_edge("TASK-001", "TASK-001")


def test_cyclic_dependency_is_detected_and_blocks():
    """Rule 2: a cyclic dependency must be detected (-> BLOCK)."""
    g = DependencyGraph()
    g.add_task("TASK-002", ["TASK-003"])
    g.add_task("TASK-003", ["TASK-002"])
    cycle = g.detect_cycle()
    assert cycle is not None
    # The cycle must involve both tasks.
    assert "TASK-002" in cycle and "TASK-003" in cycle
