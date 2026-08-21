"""Tests for orchestrator v2 components."""

from __future__ import annotations

import pytest

from aios.orchestrator.v2.advisor import ImprovementAdvisor, ProposalPriority
from aios.orchestrator.v2.evaluator import EvaluationCollector, EvaluationRecord
from aios.orchestrator.v2.reporter import GoalReporter, GoalStatus
from aios.orchestrator.v2.supervisor import ExecutionState, ExecutionSupervisor


class TestExecutionSupervisor:
    def test_start(self) -> None:
        sup = ExecutionSupervisor()
        record = sup.start("ex-1")
        assert record.execution_id == "ex-1"
        assert record.state == ExecutionState.RUNNING

    def test_complete(self) -> None:
        sup = ExecutionSupervisor()
        sup.start("ex-1")
        event = sup.complete("ex-1")
        assert event is not None
        assert event.state == ExecutionState.COMPLETED
        record = sup.get_record("ex-1")
        assert record.is_terminal

    def test_fail(self) -> None:
        sup = ExecutionSupervisor()
        sup.start("ex-1")
        event = sup.fail("ex-1", "error occurred")
        assert event is not None
        assert event.state == ExecutionState.FAILED
        assert event.detail == "error occurred"

    def test_timeout(self) -> None:
        sup = ExecutionSupervisor()
        sup.start("ex-1")
        event = sup.timeout("ex-1")
        assert event is not None
        assert event.state == ExecutionState.TIMEOUT

    def test_complete_terminal_no_double(self) -> None:
        sup = ExecutionSupervisor()
        sup.start("ex-1")
        sup.complete("ex-1")
        event = sup.complete("ex-1")
        assert event is None

    def test_duration(self) -> None:
        sup = ExecutionSupervisor()
        record = sup.start("ex-1")
        assert record.duration_ms >= 0

    def test_list_records(self) -> None:
        sup = ExecutionSupervisor()
        sup.start("ex-1")
        sup.start("ex-2")
        assert len(sup.list_records()) == 2

    def test_events_recorded(self) -> None:
        sup = ExecutionSupervisor()
        sup.start("ex-1")
        sup.complete("ex-1")
        record = sup.get_record("ex-1")
        assert len(record.events) == 2

    def test_to_dict(self) -> None:
        sup = ExecutionSupervisor()
        record = sup.start("ex-1")
        d = record.to_dict()
        assert "execution_id" in d
        assert "state" in d


class TestEvaluationCollector:
    def test_collect(self) -> None:
        ec = EvaluationCollector()
        record = ec.collect("ex-1", success=True, quality_score=0.9)
        assert record.execution_id == "ex-1"
        assert record.success is True

    def test_provenance(self) -> None:
        ec = EvaluationCollector()
        record = ec.collect("ex-1", provenance=["task-001", "exec-001"])
        assert record.provenance == ["task-001", "exec-001"]

    def test_get_record(self) -> None:
        ec = EvaluationCollector()
        ec.collect("ex-1")
        ec.collect("ex-2")
        record = ec.get_record("ex-1")
        assert record is not None

    def test_avg_quality(self) -> None:
        ec = EvaluationCollector()
        ec.collect("ex-1", quality_score=0.8)
        ec.collect("ex-2", quality_score=1.0)
        assert ec.avg_quality() == 0.9

    def test_total_cost(self) -> None:
        ec = EvaluationCollector()
        ec.collect("ex-1", cost=0.5)
        ec.collect("ex-2", cost=0.3)
        assert ec.total_cost() == 0.8

    def test_total_tokens(self) -> None:
        ec = EvaluationCollector()
        ec.collect("ex-1", tokens_used=100)
        ec.collect("ex-2", tokens_used=200)
        assert ec.total_tokens() == 300

    def test_to_dict(self) -> None:
        ec = EvaluationCollector()
        record = ec.collect("ex-1")
        d = record.to_dict()
        assert "execution_id" in d
        assert "provenance" in d


class TestImprovementAdvisor:
    def test_analyze_high_latency(self) -> None:
        advisor = ImprovementAdvisor()
        record = EvaluationRecord(execution_id="ex-1", latency_ms=6000)
        proposal = advisor.analyze(record)
        assert proposal is not None
        assert proposal.priority == ProposalPriority.MEDIUM

    def test_analyze_policy_violation(self) -> None:
        advisor = ImprovementAdvisor()
        record = EvaluationRecord(execution_id="ex-1", policy_violations=2)
        proposal = advisor.analyze(record)
        assert proposal is not None
        assert proposal.priority == ProposalPriority.HIGH

    def test_analyze_high_cost(self) -> None:
        advisor = ImprovementAdvisor()
        record = EvaluationRecord(execution_id="ex-1", cost=2.0)
        proposal = advisor.analyze(record)
        assert proposal is not None
        assert proposal.priority == ProposalPriority.LOW

    def test_analyze_no_issue(self) -> None:
        advisor = ImprovementAdvisor()
        record = EvaluationRecord(execution_id="ex-1", latency_ms=100, cost=0.01)
        proposal = advisor.analyze(record)
        assert proposal is None

    def test_analyze_batch(self) -> None:
        advisor = ImprovementAdvisor()
        records = [
            EvaluationRecord(execution_id="ex-1", latency_ms=6000),
            EvaluationRecord(execution_id="ex-2", cost=0.01),
        ]
        proposals = advisor.analyze_batch(records)
        assert len(proposals) == 1  # Only high latency triggers

    def test_proposal_requires_policy(self) -> None:
        advisor = ImprovementAdvisor()
        record = EvaluationRecord(execution_id="ex-1", latency_ms=6000)
        proposal = advisor.analyze(record)
        assert proposal.requires_policy_approval is True

    def test_to_dict(self) -> None:
        advisor = ImprovementAdvisor()
        record = EvaluationRecord(execution_id="ex-1", latency_ms=6000)
        proposal = advisor.analyze(record)
        d = proposal.to_dict()
        assert "proposal_id" in d
        assert "evidence" in d


class TestGoalReporter:
    def test_register_goal(self) -> None:
        reporter = GoalReporter()
        report = reporter.register_goal("g-1", "Build feature", tasks_total=5)
        assert report.goal_id == "g-1"
        assert report.status == GoalStatus.ACTIVE

    def test_update_progress(self) -> None:
        reporter = GoalReporter()
        reporter.register_goal("g-1", "Build", tasks_total=5)
        report = reporter.update_progress("g-1", tasks_completed=3, execution_id="ex-1")
        assert report.tasks_completed == 3
        assert report.progress == 0.6

    def test_goal_completed(self) -> None:
        reporter = GoalReporter()
        reporter.register_goal("g-1", "Build", tasks_total=5)
        report = reporter.update_progress("g-1", tasks_completed=5)
        assert report.status == GoalStatus.COMPLETED
        assert report.progress == 1.0

    def test_fail_goal(self) -> None:
        reporter = GoalReporter()
        reporter.register_goal("g-1", "Build")
        report = reporter.fail_goal("g-1")
        assert report.status == GoalStatus.FAILED

    def test_list_goals(self) -> None:
        reporter = GoalReporter()
        reporter.register_goal("g-1", "A")
        reporter.register_goal("g-2", "B")
        assert len(reporter.list_goals()) == 2

    def test_active_goals(self) -> None:
        reporter = GoalReporter()
        reporter.register_goal("g-1", "A")
        reporter.register_goal("g-2", "B")
        reporter.fail_goal("g-2")
        active = reporter.active_goals()
        assert len(active) == 1
        assert active[0].goal_id == "g-1"

    def test_to_dict(self) -> None:
        reporter = GoalReporter()
        report = reporter.register_goal("g-1", "Build")
        d = report.to_dict()
        assert "goal_id" in d
        assert "status" in d
