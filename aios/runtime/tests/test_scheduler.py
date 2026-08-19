"""Automated tests for the runtime scheduler (TASK-005)."""

import pytest

from aios.runtime.scheduler import (
    RequestStatus,
    ScheduledRequest,
    Scheduler,
    SchedulerError,
)


def test_enqueue_and_dequeue_fifo():
    s = Scheduler()
    a = s.enqueue("pa", priority=0)
    b = s.enqueue("pb", priority=0)
    assert s.dequeue().request_id == a.request_id
    assert s.dequeue().request_id == b.request_id


def test_priority_ordering():
    s = Scheduler()
    low = s.enqueue("low", priority=5)
    high = s.enqueue("high", priority=1)
    med = s.enqueue("med", priority=3)
    order = [s.dequeue().request_id for _ in range(3)]
    assert order == [high.request_id, med.request_id, low.request_id]


def test_dequeue_marks_running():
    s = Scheduler()
    r = s.enqueue("p")
    s.dequeue()
    assert s.get(r.request_id).status == RequestStatus.RUNNING


def test_mark_done_and_cancel():
    s = Scheduler()
    r = s.enqueue("p")
    s.dequeue()
    s.mark_done(r.request_id)
    assert s.get(r.request_id).status == RequestStatus.DONE
    r2 = s.enqueue("p2")
    assert s.cancel(r2.request_id) is True
    assert s.cancel(r2.request_id) is False  # already cancelled


def test_cancel_skipped_on_dequeue():
    s = Scheduler()
    r = s.enqueue("p")
    s.cancel(r.request_id)
    assert s.dequeue() is None


def test_peek_returns_highest_priority_pending():
    s = Scheduler()
    s.enqueue("low", priority=5)
    top = s.enqueue("top", priority=1)
    assert s.peek().request_id == top.request_id


def test_pending_count():
    s = Scheduler()
    s.enqueue("a")
    s.enqueue("b")
    s.enqueue("c")
    assert len(s.pending()) == 3
