"""Event Service — wraps EventBus for API/WebSocket boundary (TASK-017).

Layering: ``api`` layer.
"""
from __future__ import annotations

import threading
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set

from aios.core.events import Event, EventBus

ALLOWED_EVENTS: Set[str] = {
    "execution.created", "execution.started", "execution.node.started",
    "execution.node.completed", "execution.failed", "execution.completed",
    "task.created", "task.updated", "task.completed",
    "agent.started", "agent.completed",
    "artifact.created", "skill.changed", "health.changed", "policy.decision",
}


class EventServiceError(Exception):
    pass


@dataclass
class EventEnvelope:
    event_id: str
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = "1.0.0"
    source: str = "runtime"
    sequence: int = 0

    @classmethod
    def create(cls, event_type: str, payload: Optional[Dict[str, Any]] = None,
               source: str = "runtime", sequence: int = 0, event_id: Optional[str] = None) -> "EventEnvelope":
        if event_type not in ALLOWED_EVENTS:
            raise EventServiceError(f"Event type {event_type!r} not in whitelist")
        return cls(event_id=event_id or f"evt-{uuid.uuid4().hex[:12]}", event_type=event_type,
                   payload=dict(payload or {}), source=source, sequence=sequence)

    def to_dict(self) -> Dict[str, Any]:
        return {"event_id": self.event_id, "event_type": self.event_type, "payload": dict(self.payload),
                "timestamp": self.timestamp, "version": self.version, "source": self.source, "sequence": self.sequence}


class EventService:
    def __init__(self, bus: Optional[EventBus] = None, max_history: int = 1000) -> None:
        self._bus = bus or EventBus()
        self._max_history = max_history
        self._history: deque[EventEnvelope] = deque(maxlen=max_history)
        self._subscribers: List[Callable[[EventEnvelope], None]] = []
        self._sequence: int = 0
        self._lock = threading.RLock()

    def publish(self, event_type: str, payload: Optional[Dict[str, Any]] = None, source: str = "runtime") -> EventEnvelope:
        if event_type not in ALLOWED_EVENTS:
            raise EventServiceError(f"Event type {event_type!r} not in whitelist")
        with self._lock:
            self._sequence += 1
            envelope = EventEnvelope.create(event_type=event_type, payload=payload, source=source, sequence=self._sequence)
            self._history.append(envelope)
            subs = list(self._subscribers)
        for cb in subs:
            try:
                cb(envelope)
            except Exception:
                pass
        return envelope

    def subscribe(self, callback: Callable[[EventEnvelope], None]) -> None:
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[EventEnvelope], None]) -> None:
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    def history(self, event_type: Optional[str] = None, since_sequence: int = 0, limit: int = 100) -> List[EventEnvelope]:
        with self._lock:
            items = list(self._history)
        if event_type is not None:
            items = [e for e in items if e.event_type == event_type]
        if since_sequence > 0:
            items = [e for e in items if e.sequence > since_sequence]
        if limit and len(items) > limit:
            items = items[-limit:]
        return items

    def replay_since(self, last_event_id: Optional[str] = None) -> List[EventEnvelope]:
        if not last_event_id:
            with self._lock:
                return list(self._history)
        with self._lock:
            items = list(self._history)
        for idx, env in enumerate(items):
            if env.event_id == last_event_id:
                return items[idx + 1:]
        return items

    def clear(self) -> None:
        with self._lock:
            self._history.clear()
            self._sequence = 0

    @property
    def sequence(self) -> int:
        with self._lock:
            return self._sequence
