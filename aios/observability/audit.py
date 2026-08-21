"""Audit service with provenance tracking.

AC-021-02: Audit has provenance.
"""

from __future__ import annotations

import hashlib
import threading
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuditEntry:
    """Immutable audit entry with provenance."""

    entry_id: str
    timestamp: float
    who: str
    what: str
    execution_id: str = ""
    workflow_id: str = ""
    agent_id: str = ""
    capability_id: str = ""
    tool_id: str = ""
    policy_decision: str = ""
    result: str = ""
    provenance_chain: list[str] = field(default_factory=list)

    def compute_hash(self) -> str:
        content = f"{self.entry_id}:{self.who}:{self.what}:{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "who": self.who,
            "what": self.what,
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "agent_id": self.agent_id,
            "capability_id": self.capability_id,
            "tool_id": self.tool_id,
            "policy_decision": self.policy_decision,
            "result": self.result,
            "provenance_chain": self.provenance_chain,
            "content_hash": self.compute_hash(),
        }


class AuditService:
    """Immutable audit trail with provenance.

    AC-021-02: Audit has provenance.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: list[AuditEntry] = []
        self._counter: int = 0

    def record(
        self,
        who: str,
        what: str,
        execution_id: str = "",
        workflow_id: str = "",
        agent_id: str = "",
        capability_id: str = "",
        tool_id: str = "",
        policy_decision: str = "",
        result: str = "",
        provenance: list[str] | None = None,
    ) -> AuditEntry:
        """Record an audit entry."""
        with self._lock:
            self._counter += 1
            entry = AuditEntry(
                entry_id=f"audit-{self._counter:06d}",
                timestamp=time.time(),
                who=who,
                what=what,
                execution_id=execution_id,
                workflow_id=workflow_id,
                agent_id=agent_id,
                capability_id=capability_id,
                tool_id=tool_id,
                policy_decision=policy_decision,
                result=result,
                provenance_chain=provenance or [],
            )
            self._entries.append(entry)
            return entry

    def query(
        self,
        who: str | None = None,
        execution_id: str | None = None,
        agent_id: str | None = None,
        limit: int | None = None,
    ) -> list[AuditEntry]:
        """Query audit entries with filters."""
        with self._lock:
            entries = list(self._entries)

        if who:
            entries = [e for e in entries if e.who == who]
        if execution_id:
            entries = [e for e in entries if e.execution_id == execution_id]
        if agent_id:
            entries = [e for e in entries if e.agent_id == agent_id]
        if limit:
            entries = entries[-limit:]
        return entries

    def count(self) -> int:
        with self._lock:
            return len(self._entries)

    def get_entry(self, entry_id: str) -> AuditEntry | None:
        with self._lock:
            for e in self._entries:
                if e.entry_id == entry_id:
                    return e
        return None
