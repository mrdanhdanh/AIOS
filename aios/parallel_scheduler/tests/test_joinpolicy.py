"""Tests for TASK-028 JoinPolicy variants and DispatchDecision."""

from __future__ import annotations

from aios.parallel_scheduler.contracts import DispatchDecision, JoinPolicy
from aios.parallel_scheduler.scheduler import ParallelScheduler


def _graph(scheduler: ParallelScheduler) -> None:
    scheduler.load_graph(
        [{"node_id": "a"}, {"node_id": "b"}, {"node_id": "c"}],
        [{"source": "a", "target": "b"}, {"source": "a", "target": "c"}],
    )


def test_all_success_default() -> None:
    s = ParallelScheduler(JoinPolicy.ALL_SUCCESS)
    _graph(s)
    assert s.decision_for("b") == DispatchDecision.WAITING_DEPENDENCY
    s.dispatch("a")
    s.complete("a")
    assert s.decision_for("b") == DispatchDecision.READY


def test_any_success() -> None:
    s = ParallelScheduler(JoinPolicy.ANY_SUCCESS)
    _graph(s)
    # No dep completed yet -> waiting
    assert s.decision_for("b") == DispatchDecision.WAITING_DEPENDENCY
    s.dispatch("a")
    s.complete("a")
    assert s.decision_for("b") == DispatchDecision.READY


def test_all_completed_accepts_failed_dep() -> None:
    s = ParallelScheduler(JoinPolicy.ALL_COMPLETED)
    _graph(s)
    s._nodes["a"].state = "failed"
    assert s.decision_for("b") == DispatchDecision.READY


def test_blocked_when_not_pending() -> None:
    s = ParallelScheduler()
    _graph(s)
    s.dispatch("a")
    assert s.decision_for("a") == DispatchDecision.BLOCKED


def test_rejected_unknown_node() -> None:
    s = ParallelScheduler()
    assert s.decision_for("zzz") == DispatchDecision.REJECTED
