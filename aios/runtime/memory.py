"""Memory substrate — 4 types with scoped isolation + provenance (TASK-007, M1).

``MemoryStore`` is the M1 substrate for conversation / session / knowledge /
artifact memories. Every :class:`MemoryEntry` is content-addressed (SHA-256
``content_hash``) and carries provenance fields (``producer``/``source``/
``task_id``/``run_id``) so a caller can build an :class:`Evidence` chain
without importing governance. Isolation is enforced by ``scope_id``: a query
scoped to one scope never returns entries from another scope unless the caller
explicitly asks for an unscoped listing.

Offline-first: pure Python + stdlib + ``aios.core`` only. No embeddings, no
LLM, no network. Thread-safe via :class:`threading.RLock`.

Layering: ``runtime`` layer — relative imports only.
"""

from __future__ import annotations

import hashlib
import re
import threading
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

__all__ = ["MemoryError", "MemoryType", "MemoryEntry", "MemoryStore"]


class MemoryError(Exception):
    """Raised on memory validation or store errors."""


class MemoryType(str, Enum):
    """The four M1 memory types."""

    CONVERSATION = "conversation"
    SESSION = "session"
    KNOWLEDGE = "knowledge"
    ARTIFACT = "artifact"

    @classmethod
    def all(cls) -> List["MemoryType"]:
        return list(cls)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_content(content: str | bytes) -> str:
    if isinstance(content, str):
        data = content.encode("utf-8")
    else:
        data = bytes(content)
    return hashlib.sha256(data).hexdigest()


@dataclass
class MemoryEntry:
    """A single memory entry with content-hash integrity and provenance."""

    entry_id: str
    memory_type: MemoryType
    scope_id: str
    content: str
    content_hash: str
    producer: str = ""
    source: str = ""
    task_id: str = ""
    run_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    version: str = "0.1.0"

    @classmethod
    def create(
        cls,
        memory_type: MemoryType | str,
        scope_id: str,
        content: str | bytes,
        producer: str = "",
        source: str = "",
        task_id: str = "",
        run_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        entry_id: Optional[str] = None,
        version: str = "0.1.0",
    ) -> "MemoryEntry":
        """Build an entry, computing ``content_hash`` deterministically."""
        if isinstance(memory_type, str):
            try:
                memory_type = MemoryType(memory_type)
            except ValueError as exc:
                raise MemoryError(f"Unknown memory type {memory_type!r}") from exc
        if not isinstance(memory_type, MemoryType):
            raise MemoryError(f"memory_type must be MemoryType, got {type(memory_type).__name__}")
        if not scope_id or not str(scope_id).strip():
            raise MemoryError("scope_id is required (isolation key)")
        if isinstance(content, bytes):
            try:
                text = content.decode("utf-8")
            except Exception as exc:
                raise MemoryError(f"bytes content must be utf-8: {exc}") from exc
        elif isinstance(content, str):
            text = content
        else:
            raise MemoryError(f"content must be str or bytes, got {type(content).__name__}")
        ch = _hash_content(text)
        return cls(
            entry_id=entry_id or f"mem-{uuid.uuid4().hex[:12]}",
            memory_type=memory_type,
            scope_id=str(scope_id),
            content=text,
            content_hash=ch,
            producer=producer or "",
            source=source or "",
            task_id=task_id or "",
            run_id=run_id or "",
            metadata=dict(metadata or {}),
            version=version,
        )

    def verify(self) -> bool:
        """Return True iff stored ``content_hash`` matches current ``content``."""
        return _hash_content(self.content) == self.content_hash


class MemoryStore:
    """Thread-safe in-memory store with scoped isolation."""

    def __init__(self) -> None:
        self._entries: Dict[str, MemoryEntry] = {}
        self._by_type: Dict[MemoryType, List[str]] = defaultdict(list)
        self._by_scope: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.RLock()

    # -- write --

    def put(self, entry: MemoryEntry) -> MemoryEntry:
        """Store an entry, verifying integrity and isolation invariants."""
        if not isinstance(entry, MemoryEntry):
            raise MemoryError("MemoryStore only holds MemoryEntry")
        if not entry.verify():
            raise MemoryError(f"content_hash mismatch for {entry.entry_id!r}")
        with self._lock:
            if entry.entry_id in self._entries:
                raise MemoryError(f"entry_id already exists: {entry.entry_id!r}")
            self._entries[entry.entry_id] = entry
            if entry.entry_id not in self._by_type[entry.memory_type]:
                self._by_type[entry.memory_type].append(entry.entry_id)
            if entry.entry_id not in self._by_scope[entry.scope_id]:
                self._by_scope[entry.scope_id].append(entry.entry_id)
        return entry

    def delete(self, entry_id: str) -> None:
        with self._lock:
            entry = self._entries.pop(entry_id, None)
            if entry is None:
                raise MemoryError(f"entry not found: {entry_id!r}")
            lst = self._by_type.get(entry.memory_type)
            if lst is not None:
                try:
                    lst.remove(entry_id)
                except ValueError:
                    pass
            sl = self._by_scope.get(entry.scope_id)
            if sl is not None:
                try:
                    sl.remove(entry_id)
                except ValueError:
                    pass

    # -- read --

    def get(self, entry_id: str) -> MemoryEntry:
        with self._lock:
            e = self._entries.get(entry_id)
        if e is None:
            raise MemoryError(f"entry not found: {entry_id!r}")
        return e

    def list_all(self) -> List[MemoryEntry]:
        with self._lock:
            return list(self._entries.values())

    def list_by_type(self, memory_type: MemoryType | str) -> List[MemoryEntry]:
        if isinstance(memory_type, str):
            memory_type = MemoryType(memory_type)
        with self._lock:
            ids = list(self._by_type.get(memory_type, []))
            return [self._entries[i] for i in ids]

    def list_by_scope(self, scope_id: str) -> List[MemoryEntry]:
        with self._lock:
            ids = list(self._by_scope.get(str(scope_id), []))
            return [self._entries[i] for i in ids]

    def search(
        self,
        query: str,
        scope_id: Optional[str] = None,
        memory_type: Optional[MemoryType | str] = None,
    ) -> List[MemoryEntry]:
        """Deterministic substring search.

        - Case-insensitive ``query in content`` filtering.
        - Optional ``scope_id`` isolation: when supplied, only that scope is
          searched; when ``None``, all scopes are searched (caller must opt-in).
        - Optional ``memory_type`` filter.
        - Ranking: occurrence count (desc) → entry_id (asc) for determinism.
        """
        if not query or not query.strip():
            return []
        q = query.lower()
        if isinstance(memory_type, str) and memory_type is not None:
            memory_type = MemoryType(memory_type)
        with self._lock:
            candidates: List[MemoryEntry]
            if scope_id is not None:
                candidates = [self._entries[i] for i in list(self._by_scope.get(str(scope_id), []))]
            else:
                candidates = list(self._entries.values())
            if memory_type is not None:
                candidates = [e for e in candidates if e.memory_type == memory_type]
            scored: List[tuple[int, str, MemoryEntry]] = []
            for e in candidates:
                low = e.content.lower()
                if q not in low:
                    continue
                cnt = low.count(q)
                scored.append((-cnt, e.entry_id, e))
            scored.sort(key=lambda x: (x[0], x[1]))
            return [e for _, _, e in scored]

    def verify(self, entry_id: str) -> bool:
        return self.get(entry_id).verify()

    def verify_all(self) -> bool:
        with self._lock:
            return all(e.verify() for e in self._entries.values())

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)

    def __contains__(self, entry_id: object) -> bool:
        if not isinstance(entry_id, str):
            return False
        with self._lock:
            return entry_id in self._entries
