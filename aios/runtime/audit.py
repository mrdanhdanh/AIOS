"""Append-only, hash-chained audit trail (TASK-004, M1).

Every security- and governance-relevant action in the runtime is recorded as an
:class:`AuditEvent`. Events form a tamper-evident chain: each event carries the
``hash`` of the previous event (``prev_hash``). :meth:`AuditTrail.verify_integrity`
recomputes the chain and returns ``False`` if any event was altered or if the
chain was reordered.

The audit service is deterministic and offline-first: it depends only on the
standard library and the kernel ``Event``/``EventBus`` primitives from
``aios.core`` (for optional asynchronous fan-out), never on agent/orchestrator
layers.
"""

from __future__ import annotations

import hashlib
import threading
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


__all__ = ["AuditError", "AuditStatus", "AuditEvent", "AuditTrail"]


class AuditError(Exception):
    """Raised on integrity or usage errors in the audit trail."""


class AuditStatus(Enum):
    """Outcome of an audited action."""

    OK = "ok"
    DENIED = "denied"
    ERROR = "error"
    ESCALATED = "escalated"


def _stable(payload: Any) -> str:
    """Render a JSON-ish stable string for hashing."""
    if isinstance(payload, dict):
        return "{" + ",".join(f"{k!r}:{_stable(v)}" for k, v in sorted(payload.items())) + "}"
    if isinstance(payload, (list, tuple)):
        return "[" + ",".join(_stable(v) for v in payload) + "]"
    return repr(payload)


@dataclass
class AuditEvent:
    """A single, hash-chained audit record."""

    event_id: str
    timestamp: str
    actor: str
    action: str
    target: str
    context_id: Optional[str]
    status: AuditStatus
    metadata: Dict[str, Any] = field(default_factory=dict)
    prev_hash: Optional[str] = None
    hash: Optional[str] = None

    def compute_hash(self) -> str:
        payload = "|".join(
            [
                self.event_id,
                self.timestamp,
                self.actor,
                self.action,
                self.target,
                str(self.context_id),
                self.status.value,
                self.prev_hash or "",
                _stable(self.metadata),
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def seal(self, prev_hash: Optional[str]) -> str:
        """Set ``prev_hash`` and compute + store ``hash``; return the hash."""
        self.prev_hash = prev_hash
        self.hash = self.compute_hash()
        return self.hash


class AuditTrail:
    """Thread-safe, append-only audit log with chain verification."""

    def __init__(self) -> None:
        self._events: List[AuditEvent] = []
        self._index: Dict[str, int] = {}
        self._by_context: Dict[str, List[int]] = defaultdict(list)
        self._by_actor: Dict[str, List[int]] = defaultdict(list)
        self._prev_hash: Optional[str] = None
        self._lock = threading.RLock()

    def record(
        self,
        actor: str,
        action: str,
        target: str,
        context_id: Optional[str] = None,
        status: AuditStatus = AuditStatus.OK,
        metadata: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> AuditEvent:
        """Append a new event, chaining it to the previous one."""
        with self._lock:
            ev = AuditEvent(
                event_id=event_id or f"aud-{uuid.uuid4().hex[:12]}",
                timestamp=timestamp or datetime.now(timezone.utc).isoformat(),
                actor=actor,
                action=action,
                target=target,
                context_id=context_id,
                status=status,
                metadata=dict(metadata or {}),
            )
            h = ev.seal(self._prev_hash)
            idx = len(self._events)
            self._events.append(ev)
            self._index[ev.event_id] = idx
            if context_id is not None:
                self._by_context[context_id].append(idx)
            self._by_actor[actor].append(idx)
            self._prev_hash = h
        return ev

    def get(self, event_id: str) -> Optional[AuditEvent]:
        with self._lock:
            idx = self._index.get(event_id)
            return self._events[idx] if idx is not None else None

    def query(
        self,
        *,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        context_id: Optional[str] = None,
        status: Optional[AuditStatus] = None,
    ) -> List[AuditEvent]:
        """Return events filtered by any combination of fields."""
        with self._lock:
            if context_id is not None:
                candidates = [self._events[i] for i in self._by_context.get(context_id, [])]
            elif actor is not None:
                candidates = [self._events[i] for i in self._by_actor.get(actor, [])]
            else:
                candidates = list(self._events)
        result = []
        for ev in candidates:
            if actor is not None and ev.actor != actor:
                continue
            if action is not None and ev.action != action:
                continue
            if context_id is not None and ev.context_id != context_id:
                continue
            if status is not None and ev.status != status:
                continue
            result.append(ev)
        return result

    def verify_integrity(self) -> bool:
        """Recompute the chain; return True iff unbroken and self-consistent."""
        with self._lock:
            prev: Optional[str] = None
            for ev in self._events:
                if ev.hash != ev.compute_hash():
                    return False
                if ev.prev_hash != prev:
                    return False
                prev = ev.hash
        return True

    def __len__(self) -> int:
        with self._lock:
            return len(self._events)

    @property
    def root_hash(self) -> Optional[str]:
        with self._lock:
            return self._prev_hash
