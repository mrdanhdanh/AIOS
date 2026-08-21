"""Integration tests for Operational Orchestration — AC-012-01..10 (TASK-012)."""

import tempfile
from pathlib import Path

import pytest

from aios.orchestrator.failure_recovery import FailureRecovery, RecoveryStrategy, RetryPolicy
from aios.orchestrator.goal_manager import GoalManager, GoalStatus
from aios.orchestrator.permission_broker import OrchestratorPermissionBroker, OrchestratorPermissionDecision
from aios.orchestrator.task_queue import Task, TaskQueue, TaskStatus
from aios.runtime.permission import Permission, PermissionBroker, PermissionScope
from aios.runtime.policy import PolicyDecision, PolicyEngine, PolicyRule


class TestGoalResume:
    def test_goal_resume_after_restart(self):
        gm = GoalManager()
        g = gm.create_goal(title="Build auth", goal_id="goal-001", tasks=["task-001", "task-002"])
        gm.transition("goal-001", GoalStatus.PLANNED)
        gm.transition("goal-001", GoalStatus.ACTIVE)
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "goals.json")
            gm.save_to_file(path)
            # Simulate restart
            gm2 = GoalManager()
            gm2.load_from_file(path)
            assert gm2.get("goal-001").status == GoalStatus.ACTIVE
            assert gm2.get("goal-001").tasks == ["task-001", "task-002"]
            # Resume
            gm2.pause("goal-001")
            gm2.resume("goal-001")
            assert gm2.get("goal-001").status == GoalStatus.ACTIVE


class TestTaskDependency:
    def test_dependency_blocked(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.enqueue(Task(id="b", dependencies=["a"]))
        assert q.get("b").status == TaskStatus.BLOCKED
        q.dequeue()
        q.succeed("a")
        assert q.get("b").status == TaskStatus.READY

    def test_chain_blocked_on_failure(self):
        q = TaskQueue()
        q.enqueue(Task(id="a"))
        q.enqueue(Task(id="b", dependencies=["a"]))
        q.enqueue(Task(id="c", dependencies=["b"]))
        q.dequeue()
        q.fail("a")
        assert q.get("b").status == TaskStatus.BLOCKED
        assert q.get("c").status == TaskStatus.BLOCKED


class TestPermissionDeny:
    def test_deny_blocks_task(self):
        broker = PermissionBroker()
        engine = PolicyEngine(broker=broker)
        ob = OrchestratorPermissionBroker(permission_broker=broker, policy_engine=engine)
        q = TaskQueue()
        q.enqueue(Task(id="task-001"))
        # Check permission -> DENY
        decision = ob.check("agent:alice", ["filesystem.write"], resource="filesystem.write")
        assert decision == OrchestratorPermissionDecision.DENY
        # Task should be blocked, not running — simulate orchestration blocking on DENY
        if decision == OrchestratorPermissionDecision.DENY:
            q.block("task-001")
        assert q.get("task-001").status == TaskStatus.BLOCKED
        # BLOCKED tasks are not dequeueable via peek (only READY)
        assert q.peek() is None


class TestRetryBounded:
    def test_retry_exhausted(self):
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=3))
        for i in range(3):
            r = fr.handle_failure("task-001", "timeout")
            assert r.strategy == RecoveryStrategy.RETRY_SAME
        r = fr.handle_failure("task-001", "timeout")
        assert r.strategy != RecoveryStrategy.RETRY_SAME
        assert r.attempt == 4

    def test_retry_success(self):
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=3))
        r1 = fr.handle_failure("task-001", "timeout")
        assert r1.attempt == 1
        r2 = fr.handle_failure("task-001", "timeout")
        assert r2.attempt == 2
        # Simulate success on 3rd attempt (no failure)
        assert fr.attempts("task-001") == 2


class TestRecoveryPolicy:
    def test_fallback_only_when_allowed(self):
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=1), policy_checker=lambda tid, strat: strat == RecoveryStrategy.FALLBACK_AGENT)
        fr.handle_failure("task-001", "timeout")
        r = fr.handle_failure("task-001", "timeout")
        assert r.strategy == RecoveryStrategy.FALLBACK_AGENT

    def test_fallback_denied(self):
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=1), policy_checker=lambda tid, strat: False)
        fr.handle_failure("task-001", "timeout")
        r = fr.handle_failure("task-001", "timeout")
        assert r.strategy == RecoveryStrategy.FAIL


class TestStateAuthority:
    def test_orchestration_state_references_execution(self):
        q = TaskQueue()
        t = Task(id="task-001", execution_id="exec-123")
        q.enqueue(t)
        assert q.get("task-001").execution_id == "exec-123"
        # Orchestration state does not own execution state — only references it
        assert hasattr(q.get("task-001"), "execution_id")
        # Runtime StateStore is separate authority
        from aios.runtime.state import StateStore

        store = StateStore()
        assert store is not None

    def test_goal_references_tasks_not_execution(self):
        gm = GoalManager()
        g = gm.create_goal(title="t", goal_id="g1", tasks=["task-001"])
        assert "task-001" in g.tasks
        assert not hasattr(g, "execution_state")


class TestQueueSeparation:
    def test_no_cron(self):
        q = TaskQueue()
        assert not hasattr(q, "schedule_cron")
        assert not hasattr(q, "schedule_at")
        assert not hasattr(q, "run_cron")
        assert not hasattr(q, "cron")

    def test_logical_queue_only(self):
        q = TaskQueue()
        # Only logical ops
        assert hasattr(q, "enqueue")
        assert hasattr(q, "dequeue")
        assert hasattr(q, "peek")
        assert hasattr(q, "pause")
        assert hasattr(q, "resume")
        assert hasattr(q, "cancel")
        assert hasattr(q, "block")
        assert hasattr(q, "unblock")


class TestFullOrchestrationFlow:
    def test_request_to_goal_to_queue_to_recovery(self):
        # Simulate: Request -> Decision -> Goal -> Queue -> Permission -> Recovery
        from aios.orchestrator.decision_pipeline import DecisionPipeline

        pipe = DecisionPipeline()
        result = pipe.execute({"text": "run tests"})
        assert result.source == "deterministic"

        gm = GoalManager()
        g = gm.create_goal(title="Run tests", goal_id="goal-001", tasks=["task-001"])
        gm.transition("goal-001", GoalStatus.PLANNED)
        gm.transition("goal-001", GoalStatus.ACTIVE)

        q = TaskQueue()
        q.enqueue(Task(id="task-001", goal_id="goal-001", workflow_id="test-workflow"))
        assert q.get("task-001").status == TaskStatus.READY

        # Permission check
        broker = PermissionBroker()
        broker.grant("agent:test", Permission(PermissionScope.EXECUTE, "test.run"))
        engine = PolicyEngine(broker=broker)
        engine.add_rule(PolicyRule("allow-test", applies=lambda r: r.resource == "test.run", decision=PolicyDecision.ALLOW, reason="allow"))
        ob = OrchestratorPermissionBroker(permission_broker=broker, policy_engine=engine)
        decision = ob.check("agent:test", ["test.run"], resource="test.run")
        assert decision == OrchestratorPermissionDecision.ALLOW

        # Execute and handle failure
        q.dequeue()
        assert q.get("task-001").status == TaskStatus.RUNNING
        fr = FailureRecovery(retry_policy=RetryPolicy(max_attempts=3))
        # Simulate transient failure
        r = fr.handle_failure("task-001", "timeout")
        assert r.strategy == RecoveryStrategy.RETRY_SAME
