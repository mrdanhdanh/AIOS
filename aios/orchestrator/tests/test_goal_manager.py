"""Tests for GoalManager — AC-012-01/02/09 (TASK-012)."""

import json
import tempfile
from pathlib import Path

import pytest

from aios.orchestrator.goal_manager import Goal, GoalError, GoalManager, GoalStatus


class TestGoal:
    def test_create_and_validate(self):
        g = Goal(id="goal-001", title="Build auth", description="desc")
        g.validate()
        assert g.id == "goal-001"
        assert g.status == GoalStatus.CREATED

    def test_invalid_id_reject(self):
        with pytest.raises(GoalError):
            Goal(id="", title="t").validate()

    def test_invalid_priority_reject(self):
        with pytest.raises(GoalError):
            Goal(id="g1", title="t", priority="invalid").validate()

    def test_transition_valid(self):
        g = Goal(id="g1", title="t")
        g.transition(GoalStatus.PLANNED)
        assert g.status == GoalStatus.PLANNED
        g.transition(GoalStatus.ACTIVE)
        assert g.status == GoalStatus.ACTIVE
        g.transition(GoalStatus.PAUSED)
        assert g.status == GoalStatus.PAUSED
        g.transition(GoalStatus.ACTIVE)
        assert g.status == GoalStatus.ACTIVE
        g.transition(GoalStatus.COMPLETED)
        assert g.status == GoalStatus.COMPLETED

    def test_transition_invalid(self):
        g = Goal(id="g1", title="t")
        with pytest.raises(GoalError):
            g.transition(GoalStatus.ACTIVE)  # CREATED -> ACTIVE invalid

    def test_to_dict_from_dict_roundtrip(self):
        g = Goal(id="g1", title="t", description="d", tasks=["task-001"], priority="high")
        d = g.to_dict()
        g2 = Goal.from_dict(d)
        assert g2.id == g.id
        assert g2.title == g.title
        assert g2.tasks == g.tasks
        assert g2.priority == g.priority

    def test_progress(self):
        g = Goal(id="g1", title="t", tasks=["a", "b", "c"])
        p = g.progress({"a": "SUCCEEDED", "b": "SUCCEEDED", "c": "PENDING"})
        assert p["completed"] == 2
        assert p["total"] == 3
        assert p["percent"] == pytest.approx(66.66, rel=0.01)


class TestGoalManager:
    def test_create_and_get(self):
        gm = GoalManager()
        g = gm.create_goal(title="Build auth", description="desc")
        assert gm.get(g.id).title == "Build auth"

    def test_duplicate_reject(self):
        gm = GoalManager()
        gm.create_goal(title="t", goal_id="g1")
        with pytest.raises(GoalError):
            gm.create_goal(title="t2", goal_id="g1")

    def test_list(self):
        gm = GoalManager()
        gm.create_goal(title="t1", goal_id="g1")
        gm.create_goal(title="t2", goal_id="g2")
        assert len(gm.list()) == 2

    def test_transition_pause_resume_cancel(self):
        gm = GoalManager()
        g = gm.create_goal(title="t", goal_id="g1")
        gm.transition("g1", GoalStatus.PLANNED)
        gm.transition("g1", GoalStatus.ACTIVE)
        gm.pause("g1")
        assert gm.get("g1").status == GoalStatus.PAUSED
        gm.resume("g1")
        assert gm.get("g1").status == GoalStatus.ACTIVE
        gm.cancel("g1")
        assert gm.get("g1").status == GoalStatus.CANCELLED

    def test_add_remove_task(self):
        gm = GoalManager()
        gm.create_goal(title="t", goal_id="g1")
        gm.add_task("g1", "task-001")
        assert "task-001" in gm.get("g1").tasks
        gm.remove_task("g1", "task-001")
        assert "task-001" not in gm.get("g1").tasks

    def test_add_duplicate_task_reject(self):
        gm = GoalManager()
        gm.create_goal(title="t", goal_id="g1", tasks=["task-001"])
        with pytest.raises(GoalError):
            gm.add_task("g1", "task-001")

    def test_progress(self):
        gm = GoalManager()
        gm.create_goal(title="t", goal_id="g1", tasks=["a", "b"])
        p = gm.progress("g1", {"a": "SUCCEEDED", "b": "PENDING"})
        assert p["completed"] == 1

    def test_persistence_roundtrip(self):
        gm = GoalManager()
        gm.create_goal(title="t1", goal_id="g1", tasks=["task-001"])
        gm.transition("g1", GoalStatus.PLANNED)
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "goals.json")
            gm.save_to_file(path)
            # Simulate restart: new manager loads from file
            gm2 = GoalManager()
            gm2.load_from_file(path)
            assert gm2.get("g1").title == "t1"
            assert gm2.get("g1").status == GoalStatus.PLANNED
            assert gm2.get("g1").tasks == ["task-001"]

    def test_persistence_resume(self):
        gm = GoalManager()
        g = gm.create_goal(title="t", goal_id="g1", tasks=["a", "b"])
        gm.transition("g1", GoalStatus.PLANNED)
        gm.transition("g1", GoalStatus.ACTIVE)
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "goals.json")
            gm.save_to_file(path)
            gm2 = GoalManager()
            gm2.load_from_file(path)
            # Resume should work
            gm2.pause("g1")
            assert gm2.get("g1").status == GoalStatus.PAUSED
            gm2.resume("g1")
            assert gm2.get("g1").status == GoalStatus.ACTIVE

    def test_clear(self):
        gm = GoalManager()
        gm.create_goal(title="t", goal_id="g1")
        gm.clear()
        assert len(gm) == 0

    def test_unknown_goal_reject(self):
        gm = GoalManager()
        with pytest.raises(GoalError):
            gm.get("unknown")

    def test_to_dict(self):
        gm = GoalManager()
        gm.create_goal(title="t", goal_id="g1")
        d = gm.to_dict()
        assert "g1" in d
