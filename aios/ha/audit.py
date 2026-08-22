"""Enterprise audit store — hash-chained entries for integrity."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuditEntry:
    entry_id: str
    actor: str
    action: str
    target: str
    timestamp: float = field(default_factory=time.time)
    checksum: str = ""
    previous_checksum: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "actor": self.actor,
            "action": self.action,
            "target": self.target,
            "timestamp": self.timestamp,
            "checksum": self.checksum,
            "previous_checksum": self.previous_checksum,
        }


class AuditStore:
    """Append-only audit log with SHA-256 integrity chaining."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []
        self._prev = "0" * 64

    def append(self, actor: str, action: str, target: str) -> AuditEntry:
        entry_id = f"aud-{len(self._entries) + 1}"
        payload = f"{entry_id}|{actor}|{action}|{target}|{self._prev}"
        checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        entry = AuditEntry(
            entry_id=entry_id,
            actor=actor,
            action=action,
            target=target,
            checksum=checksum,
            previous_checksum=self._prev,
        )
        self._entries.append(entry)
        self._prev = checksum
        return entry

    def entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def verify_integrity(self) -> bool:
        prev = "0" * 64
        for e in self._entries:
            payload = f"{e.entry_id}|{e.actor}|{e.action}|{e.target}|{prev}"
            expected = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            if expected != e.checksum:
                return False
            prev = e.checksum
        return True
