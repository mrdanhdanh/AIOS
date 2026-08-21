"""Execution Supervisor — monitors execution lifecycle.

AC-022-01: Supervisor monitors execution lifecycle.
AC-022-02: Failure/timeout detected.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExecutionState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class SupervisionEvent:
    """Event recorded by the supervisor."""

    execution_id: str
    event_type: str
    state: ExecutionState
    timestamp: float = field(default_factory=time.time)
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "event_type": self.event_type,
            "state": self.state.value,
            "timestamp": self.timestamp,
            "detail": self.detail,
        }


@dataclass
class ExecutionRecord:
    """Record of a supervised execution."""

    execution_id: str
    state: ExecutionState = ExecutionState.CREATED
    start_time: float = 0.0
    end_time: float = 0.0
    timeout_seconds: float = 300.0
    events: list[SupervisionEvent] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        if self.start_time == 0:
            return 0.0
        end = self.end_time if self.end_time > 0 else time.time()
        return (end - self.start_time) * 1000

    @property
    def is_terminal(self) -> bool:
        return self.state in (
            ExecutionState.COMPLETED,
            ExecutionState.FAILED,
            ExecutionState.TIMEOUT,
            ExecutionState.CANCELLED,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "state": self.state.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "timeout_seconds": self.timeout_seconds,
            "event_count": len(self.events),
        }


class ExecutionSupervisor:
    """Monitors execution lifecycle and detects failures/timeouts.

    AC-022-01: Monitors lifecycle.
    AC-022-02: Detects failure/timeout.
    """

    def __init__(self, default_timeout: float = 300.0) -> None:
        self._records: dict[str, ExecutionRecord] = {}
        self._default_timeout = default_timeout

    def start(self, execution_id: str, timeout: float | None = None) -> ExecutionRecord:
        """Start supervising an execution."""
        record = ExecutionRecord(
            execution_id=execution_id,
            state=ExecutionState.RUNNING,
            start_time=time.time(),
            timeout_seconds=timeout or self._default_timeout,
        )
        event = SupervisionEvent(
            execution_id=execution_id,
            event_type="started",
            state=ExecutionState.RUNNING,
        )
        record.events.append(event)
        self._records[execution_id] = record
        return record

    def complete(self, execution_id: str) -> SupervisionEvent | None:
        """Mark execution as completed."""
        record = self._records.get(execution_id)
        if record is None or record.is_terminal:
            return None
        record.state = ExecutionState.COMPLETED
        record.end_time = time.time()
        event = SupervisionEvent(
            execution_id=execution_id,
            event_type="completed",
            state=ExecutionState.COMPLETED,
        )
        record.events.append(event)
        return event

    def fail(self, execution_id: str, reason: str = "") -> SupervisionEvent | None:
        """Mark execution as failed.

        AC-022-02: Failure detected.
        """
        record = self._records.get(execution_id)
        if record is None or record.is_terminal:
            return None
        record.state = ExecutionState.FAILED
        record.end_time = time.time()
        event = SupervisionEvent(
            execution_id=execution_id,
            event_type="failed",
            state=ExecutionState.FAILED,
            detail=reason,
        )
        record.events.append(event)
        return event

    def timeout(self, execution_id: str) -> SupervisionEvent | None:
        """Mark execution as timed out.

        AC-022-02: Timeout detected.
        """
        record = self._records.get(execution_id)
        if record is None or record.is_terminal:
            return None
        record.state = ExecutionState.TIMEOUT
        record.end_time = time.time()
        event = SupervisionEvent(
            execution_id=execution_id,
            event_type="timeout",
            state=ExecutionState.TIMEOUT,
            detail=f"Exceeded {record.timeout_seconds}s timeout",
        )
        record.events.append(event)
        return event

    def check_timeouts(self) -> list[SupervisionEvent]:
        """Check all running executions for timeout."""
        events = []
        for eid, record in self._records.items():
            if record.state == ExecutionState.RUNNING:
                if record.duration_ms / 1000 > record.timeout_seconds:
                    event = self.timeout(eid)
                    if event:
                        events.append(event)
        return events

    def get_record(self, execution_id: str) -> ExecutionRecord | None:
        return self._records.get(execution_id)

    def list_records(self) -> list[ExecutionRecord]:
        return list(self._records.values())
