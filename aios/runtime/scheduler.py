"""Runtime scheduler / technical execution queue (TASK-005, M1).

A lightweight, in-process, thread-safe queue for execution requests. It is the
*technical* scheduler (distinct from the logical task queue owned by the
orchestration layer in a later milestone): it orders pending executions by
priority and dispatches them one at a time. It does not itself run work — it
hands requests to a caller-provided ``dispatch`` function.

Guarantees per TASK-005 §2.5 / AC-005-09:
  - Scheduler does NOT own or allocate resources (ResourcePool is separate).
  - Scheduler does NOT implement workflow logic; it only decides *when*
    an execution is dispatched (one-shot / queued / scheduled / priority).
  - Supports pause/resume, scheduled future dispatch, cancellation, and
    priority ordering.

Layering: ``runtime`` layer — relative imports only; no agent/orchestrator deps.
"""

from __future__ import annotations

import heapq
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


__all__ = [
    "SchedulerError",
    "RequestStatus",
    "ScheduledRequest",
    "Scheduler",
    "SchedulerContract",
]


class SchedulerError(Exception):
    """Raised on scheduler usage errors."""


class RequestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    CANCELLED = "cancelled"


@dataclass(order=True)
class ScheduledRequest:
    """A request queued for technical dispatch."""

    priority: int
    seq: int  # insertion sequence (tie-breaker for stable FIFO)
    request_id: str = field(compare=False)
    payload: Any = field(compare=False, default=None)
    context_id: Optional[str] = field(compare=False, default=None)
    status: RequestStatus = field(compare=False, default=RequestStatus.PENDING)
    created_at: str = field(compare=False, default="")

    @classmethod
    def create(cls, payload, priority=0, context_id=None, request_id=None):
        from datetime import datetime, timezone

        return cls(
            priority=priority,
            seq=0,  # assigned by Scheduler
            request_id=request_id or f"req-{uuid.uuid4().hex[:12]}",
            payload=payload,
            context_id=context_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


class Scheduler:
    """Priority queue of execution requests with status tracking.

    Technical scheduler only — does NOT allocate resources or implement
    workflow logic (AC-005-09). Supports one-shot, queued, scheduled
    (future), priority, pause/resume, cancellation and dispatch.
    """

    def __init__(self) -> None:
        self._heap: List[ScheduledRequest] = []
        self._by_id: Dict[str, ScheduledRequest] = {}
        self._scheduled: List[tuple] = []  # (run_at_epoch, seq, request)
        self._seq = 0
        self._paused = False
        self._lock = threading.RLock()

    # -- enqueue -------------------------------------------------------- #
    def enqueue(self, payload: Any, *, priority: int = 0, context_id: Optional[str] = None,
                request_id: Optional[str] = None) -> ScheduledRequest:
        with self._lock:
            self._seq += 1
            req = ScheduledRequest.create(
                payload, priority=priority, context_id=context_id, request_id=request_id
            )
            req.seq = self._seq
            heapq.heappush(self._heap, req)
            self._by_id[req.request_id] = req
        return req

    def enqueue_request(self, req: ScheduledRequest, *, priority: int = 0) -> ScheduledRequest:
        """Enqueue an already-built request (priority can be overridden)."""
        with self._lock:
            self._seq += 1
            req.seq = self._seq
            req.priority = priority
            req.status = RequestStatus.PENDING
            heapq.heappush(self._heap, req)
            self._by_id[req.request_id] = req
        return req

    def schedule(self, payload: Any, *, run_at: Optional[str] = None,
                 run_at_epoch: Optional[float] = None,
                 priority: int = 0, context_id: Optional[str] = None,
                 request_id: Optional[str] = None) -> ScheduledRequest:
        """Schedule a request for future dispatch.

        ``run_at`` — ISO-8601 timestamp, or ``run_at_epoch`` seconds since epoch.
        If no time is given, behaves like :meth:`enqueue` (one-shot).
        """
        if run_at is None and run_at_epoch is None:
            return self.enqueue(payload, priority=priority, context_id=context_id, request_id=request_id)
        if run_at is not None and run_at_epoch is None:
            try:
                dt = datetime.fromisoformat(run_at.replace("Z", "+00:00"))
                run_at_epoch = dt.timestamp()
            except Exception:
                run_at_epoch = time.time()
        assert run_at_epoch is not None
        with self._lock:
            self._seq += 1
            req = ScheduledRequest.create(
                payload, priority=priority, context_id=context_id, request_id=request_id
            )
            req.seq = self._seq
            # Store in scheduled list; promoted to heap when due.
            heapq.heappush(self._scheduled, (run_at_epoch, req.seq, req))
            self._by_id[req.request_id] = req
        return req

    def _promote_due(self) -> None:
        now = time.time()
        while self._scheduled and self._scheduled[0][0] <= now:
            _, _, req = heapq.heappop(self._scheduled)
            if req.status != RequestStatus.CANCELLED:
                heapq.heappush(self._heap, req)

    # -- dispatch ------------------------------------------------------- #
    def dequeue(self) -> Optional[ScheduledRequest]:
        """Pop the highest-priority PENDING request (or None if empty/paused)."""
        with self._lock:
            if self._paused:
                return None
            self._promote_due()
            while self._heap:
                req = heapq.heappop(self._heap)
                if req.status == RequestStatus.CANCELLED:
                    self._by_id.pop(req.request_id, None)
                    continue
                req.status = RequestStatus.RUNNING
                return req
            return None

    def dispatch_next(self, dispatch_fn: Optional[Callable[[ScheduledRequest], Any]] = None) -> Optional[Any]:
        """Dispatch the next pending request via ``dispatch_fn``.

        Returns the dispatch result or the request itself when no function given.
        The scheduler does NOT implement execution — caller supplies the function
        (separation per AC-005-09).
        """
        req = self.dequeue()
        if req is None:
            return None
        if dispatch_fn is not None:
            try:
                result = dispatch_fn(req)
                self.mark_done(req.request_id)
                return result
            except Exception:
                # Leave as RUNNING so caller can decide retry/cancel
                raise
        return req

    # -- state ---------------------------------------------------------- #
    def peek(self) -> Optional[ScheduledRequest]:
        with self._lock:
            self._promote_due()
            for req in sorted(self._heap, key=lambda r: (r.priority, r.seq)):
                if req.status == RequestStatus.PENDING:
                    return req
            return None

    def mark_done(self, request_id: str) -> None:
        with self._lock:
            req = self._by_id.get(request_id)
            if req is not None:
                req.status = RequestStatus.DONE

    def cancel(self, request_id: str) -> bool:
        with self._lock:
            req = self._by_id.get(request_id)
            if req is None or req.status != RequestStatus.PENDING:
                return False
            req.status = RequestStatus.CANCELLED
            return True

    def pause(self) -> None:
        """Pause dispatch — queued requests remain pending (spec §2.5)."""
        with self._lock:
            self._paused = True

    def resume(self) -> None:
        """Resume dispatch after :meth:`pause`."""
        with self._lock:
            self._paused = False

    @property
    def is_paused(self) -> bool:
        with self._lock:
            return self._paused

    def get(self, request_id: str) -> Optional[ScheduledRequest]:
        with self._lock:
            return self._by_id.get(request_id)

    def pending(self) -> List[ScheduledRequest]:
        with self._lock:
            self._promote_due()
            return [r for r in self._heap if r.status == RequestStatus.PENDING]

    def scheduled_count(self) -> int:
        with self._lock:
            return len(self._scheduled)

    def __len__(self) -> int:
        with self._lock:
            return len(self._heap) + len(self._scheduled)


# Contract alias per spec
SchedulerContract = Scheduler
