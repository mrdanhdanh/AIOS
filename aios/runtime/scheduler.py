"""Runtime scheduler / technical execution queue (TASK-005, M1).

A lightweight, in-process, thread-safe queue for execution requests. It is the
*technical* scheduler (distinct from the logical task queue owned by the
orchestration layer in a later milestone): it orders pending executions by
priority and dispatches them one at a time. It does not itself run work — it
hands requests to a caller-provided ``dispatch`` function.

Layering: ``runtime`` layer — relative imports only; no agent/orchestrator deps.
"""

from __future__ import annotations

import heapq
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


__all__ = ["SchedulerError", "RequestStatus", "ScheduledRequest", "Scheduler"]


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
    """Priority queue of execution requests with status tracking."""

    def __init__(self) -> None:
        self._heap: List[ScheduledRequest] = []
        self._by_id: Dict[str, ScheduledRequest] = {}
        self._seq = 0
        self._lock = threading.RLock()

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

    def dequeue(self) -> Optional[ScheduledRequest]:
        """Pop the highest-priority PENDING request (or None if empty)."""
        with self._lock:
            while self._heap:
                req = heapq.heappop(self._heap)
                if req.status == RequestStatus.CANCELLED:
                    self._by_id.pop(req.request_id, None)
                    continue
                req.status = RequestStatus.RUNNING
                return req
            return None

    def peek(self) -> Optional[ScheduledRequest]:
        with self._lock:
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

    def get(self, request_id: str) -> Optional[ScheduledRequest]:
        with self._lock:
            return self._by_id.get(request_id)

    def pending(self) -> List[ScheduledRequest]:
        with self._lock:
            return [r for r in self._heap if r.status == RequestStatus.PENDING]

    def __len__(self) -> int:
        with self._lock:
            return len(self._heap)
