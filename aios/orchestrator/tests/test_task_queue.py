"""Tests for TaskQueue — AC-012-03/04/09 (TASK-012)."""

import json
import tempfile
from pathlib import Path

import pytest

from aios.orchestrator.task_queue import Task, TaskPriority, TaskQueue, TaskQueueError, TaskStatus


class TestTask:
    def test_create_and_validate(self):
        t = Task(id="task-001", goal_id="goal-001")
        t.validate()
        assert t.id == "task-001"

    def test_self_dependency_reject(self):
        with pytest.raises(TaskQueueError):
            Task(id="a", dependencies=["a"]).validate()

    def test_transition_valid(self):
        t = Task(id="a")
        t.transition(TaskStatus.READY)
        assert t.status == TaskStatus.READY
        t.transition(TaskStatus.RUNNING)
        assert t.status == TaskStatus.RUNNING
        t.transition(TaskStatus.SUCCEEDED)
        assert t.status == TaskStatus.SUCCEEDED

    def test_transition_invalid(self):
        t = Task(id="a", status=TaskStatus.SUCCEEDED)
        with pytest.raises(TaskQueueError):
            t.transition(TaskStatus.READY)

    def test_to_dict_from_dict_roundtrip(self):
        t = Task(id="a", goal_id="g1", priority=TaskPriority.HIGH, dependencies=["dep1"])
        d = t.to_dict()
        t2 = Task.from_dict(d)
        assert t2.id == t.id
        assert t2.priority == t.priority
        assert t2.dependencies == t.dependencies


class TestTaskQueue:
    def test_enqueue_and_auto_ready(self):
        q = TaskQueue()
        t = Task(id="a")
        q.enqueue(t)
        assert q.get("a").status == TaskStatus.READY

    def test_dependency_blocked(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.enqueue(Task(id="b", dependencies=["a"]))
        assert q.get("b").status == TaskStatus.BLOCKED
        # Complete a -> b becomes READY
        q.dequeue()  # a -> RUNNING
        q.succeed("a")
        assert q.get("b").status == TaskStatus.READY

    def test_dependency_chain(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.enqueue(Task(id="b", dependencies=["a"]))
        q.enqueue(Task(id="c", dependencies=["b"]))
        assert q.get("b").status == TaskStatus.BLOCKED
        assert q.get("c").status == TaskStatus.BLOCKED
        # Fail a -> b,c remain BLOCKED
        q.dequeue()
        q.fail("a")
        assert q.get("b").status == TaskStatus.BLOCKED
        assert q.get("c").status == TaskStatus.BLOCKED

    def test_priority_does_not_override_dependency(self):
        q = TaskQueue()
        q.enqueue(Task(id="a", priority=TaskPriority.LOW))
        q.enqueue(Task(id="b", priority=TaskPriority.CRITICAL, dependencies=["a"]))
        # b is HIGH priority but BLOCKED by dependency
        assert q.get("b").status == TaskStatus.BLOCKED
        # peek should return a (READY), not b (BLOCKED)
        assert q.peek().id == "a"

    def test_peek_priority_order(self):
        q = TaskQueue()
        q.enqueue(Task(id="low", priority=TaskPriority.LOW))
        q.enqueue(Task(id="high", priority=TaskPriority.HIGH))
        q.enqueue(Task(id="critical", priority=TaskPriority.CRITICAL))
        assert q.peek().id == "critical"

    def test_dequeue_transitions_to_running(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        t = q.dequeue()
        assert t.status == TaskStatus.RUNNING

    def test_pause_resume(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.dequeue()
        q.pause("a")
        assert q.get("a").status == TaskStatus.PAUSED
        q.resume("a")
        assert q.get("a").status == TaskStatus.READY

    def test_cancel(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.cancel("a")
        assert q.get("a").status == TaskStatus.CANCELLED

    def test_block_unblock(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.block("a")
        assert q.get("a").status == TaskStatus.BLOCKED
        q.unblock("a")
        assert q.get("a").status == TaskStatus.READY

    def test_prioritize(self):
        q = TaskQueue()
        q.enqueue(Task(id="a", priority=TaskPriority.LOW))
        q.prioritize("a", "CRITICAL")
        assert q.get("a").priority == TaskPriority.CRITICAL

    def test_reorder(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.enqueue(Task(id="b"))
        q.reorder(["b", "a"])
        assert q._order == ["b", "a"]

    def test_reorder_invalid_reject(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        with pytest.raises(TaskQueueError):
            q.reorder(["a", "b"])

    def test_duplicate_enqueue_reject(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        with pytest.raises(TaskQueueError):
            q.enqueue(Task(id="a"))

    def test_persistence_roundtrip(self):
        q = TaskQueue()
        q.enqueue(Task(id="a", goal_id="g1"))
        q.enqueue(Task(id="b", dependencies=["a"]))
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "queue.json")
            q.save_to_file(path)
            q2 = TaskQueue()
            q2.load_from_file(path)
            assert q2.get("a").goal_id == "g1"
            assert q2.get("b").status == TaskStatus.BLOCKED

    def test_persistence_resume(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.enqueue(Task(id="b", dependencies=["a"]))
        q.dequeue()  # a -> RUNNING
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "queue.json")
            q.save_to_file(path)
            q2 = TaskQueue()
            q2.load_from_file(path)
            assert q2.get("a").status == TaskStatus.RUNNING
            assert q2.get("b").status == TaskStatus.BLOCKED
            q2.succeed("a")
            assert q2.get("b").status == TaskStatus.READY

    def test_no_cron_scheduling(self):
        # TaskQueue should not have cron/schedule methods
        q = TaskQueue()
        assert not hasattr(q, "schedule_cron")
        assert not hasattr(q, "schedule_at")
        assert not hasattr(q, "run_cron")

    def test_list_by_status(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.enqueue(Task(id="b", dependencies=["a"]))
        ready = q.list_by_status(TaskStatus.READY)
        blocked = q.list_by_status(TaskStatus.BLOCKED)
        assert len(ready) == 1
        assert len(blocked) == 1

    def test_list_by_goal(self):
        q = TaskQueue()
        q.enqueue(Task(id="a", goal_id="g1"))
        q.enqueue(Task(id="b", goal_id="g1"))
        q.enqueue(Task(id="c", goal_id="g2"))
        assert len(q.list_by_goal("g1")) == 2
        assert len(q.list_by_goal("g2")) == 1

    def test_increment_attempts(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.increment_attempts("a")
        assert q.get("a").attempts == 1

    def test_clear(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.clear()
        assert len(q) == 0
