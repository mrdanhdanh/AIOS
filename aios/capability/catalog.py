"""System Catalog — indexed search over registry metadata (TASK-009, M1).

The catalog is a *consumer* of metadata — it never owns objects. Registries
push :class:`CatalogEntry` records into it; the catalog indexes and serves
``search`` / ``find_by_*`` queries deterministically (lower-cased substring
over ``id / type / tags / description`` — no embeddings, no LLM).

Offline-first, deterministic, thread-safe via :class:`threading.RLock`.

Layering: ``capability`` layer — stdlib + ``aios.core`` only.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

__all__ = ["CatalogError", "CatalogEntry", "SystemCatalog"]


class CatalogError(Exception):
    """Raised on catalog validation or lookup errors."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CatalogEntry:
    """A single indexed metadata record."""

    # stable id for the catalog row (not the original object id)
    entry_id: str = ""
    # logical type: capability | prompt | tool | agent | workflow | skill | model | artifact
    catalog_type: str = ""
    # original object id (capability_id / prompt_id / tool_id / ...)
    original_id: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # provenance — which registry/source produced this entry
    source: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        catalog_type: str,
        original_id: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "",
        provenance: Optional[Dict[str, Any]] = None,
        entry_id: Optional[str] = None,
    ) -> "CatalogEntry":
        obj = cls(
            entry_id=entry_id or f"cat-{uuid.uuid4().hex[:12]}",
            catalog_type=catalog_type,
            original_id=original_id,
            description=description or "",
            tags=list(tags or []),
            metadata=dict(metadata or {}),
            source=source or "",
            provenance=dict(provenance or {}),
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if not isinstance(self.entry_id, str) or not self.entry_id.strip():
            raise CatalogError("entry_id must be a non-empty string")
        if not isinstance(self.catalog_type, str) or not self.catalog_type.strip():
            raise CatalogError("catalog_type must be a non-empty string")
        if not isinstance(self.original_id, str) or not self.original_id.strip():
            raise CatalogError("original_id must be a non-empty string")
        if not isinstance(self.tags, list):
            raise CatalogError("tags must be a list")
        for t in self.tags:
            if not isinstance(t, str) or not t.strip():
                raise CatalogError(f"tag {t!r} must be a non-empty string")
        if not isinstance(self.metadata, dict):
            raise CatalogError("metadata must be a mapping")
        # provenance/source: at least one should be present so callers can chain evidence
        # but we allow empty for flexibility; the registry helpers set source.
        if not isinstance(self.source, str):
            raise CatalogError("source must be a string")
        if not isinstance(self.provenance, dict):
            raise CatalogError("provenance must be a mapping")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "catalog_type": self.catalog_type,
            "original_id": self.original_id,
            "description": self.description,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
            "source": self.source,
            "provenance": dict(self.provenance),
            "created_at": self.created_at,
        }


class SystemCatalog:
    """In-memory metadata index with deterministic search."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        # entry_id -> CatalogEntry
        self._entries: Dict[str, CatalogEntry] = {}
        # (catalog_type, original_id) -> entry_id for duplicate detection
        self._by_type_id: Dict[tuple, str] = {}

    # -- mutations ---------------------------------------------------------
    def index(self, entry: CatalogEntry) -> None:
        """Index a single entry. Duplicate (catalog_type, original_id) is rejected."""
        if not isinstance(entry, CatalogEntry):
            raise CatalogError("entry must be CatalogEntry")
        entry.validate()
        key = (entry.catalog_type, entry.original_id)
        with self._lock:
            if key in self._by_type_id:
                raise CatalogError(
                    f"entry already indexed for {key[0]!r}:{key[1]!r}"
                )
            if entry.entry_id in self._entries:
                raise CatalogError(f"entry_id already exists: {entry.entry_id!r}")
            self._entries[entry.entry_id] = entry
            self._by_type_id[key] = entry.entry_id

    def upsert(self, entry: CatalogEntry) -> None:
        """Insert or replace entry for (catalog_type, original_id)."""
        if not isinstance(entry, CatalogEntry):
            raise CatalogError("entry must be CatalogEntry")
        entry.validate()
        key = (entry.catalog_type, entry.original_id)
        with self._lock:
            old_id = self._by_type_id.get(key)
            if old_id is not None and old_id != entry.entry_id:
                # replace: remove old
                self._entries.pop(old_id, None)
            self._entries[entry.entry_id] = entry
            self._by_type_id[key] = entry.entry_id

    def remove(self, entry_id: Optional[str] = None, *, catalog_type: str = "", original_id: str = "") -> None:
        with self._lock:
            if entry_id is not None:
                e = self._entries.pop(entry_id, None)
                if e is None:
                    raise CatalogError(f"unknown entry_id: {entry_id!r}")
                self._by_type_id.pop((e.catalog_type, e.original_id), None)
                return
            key = (catalog_type, original_id)
            eid = self._by_type_id.get(key)
            if eid is None:
                raise CatalogError(f"unknown entry for {key!r}")
            self._entries.pop(eid, None)
            del self._by_type_id[key]

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self._by_type_id.clear()

    # -- queries -----------------------------------------------------------
    def get(self, entry_id: str) -> CatalogEntry:
        with self._lock:
            e = self._entries.get(entry_id)
        if e is None:
            raise CatalogError(f"unknown entry_id: {entry_id!r}")
        return e

    def find_by_id(self, original_id: str) -> List[CatalogEntry]:
        oid = original_id.lower()
        with self._lock:
            return sorted(
                [e for e in self._entries.values() if e.original_id.lower() == oid],
                key=lambda e: (e.catalog_type, e.original_id),
            )

    def find_by_type(self, catalog_type: str) -> List[CatalogEntry]:
        ct = catalog_type.lower()
        with self._lock:
            return sorted(
                [e for e in self._entries.values() if e.catalog_type.lower() == ct],
                key=lambda e: e.original_id,
            )

    def find_by_tag(self, tag: str) -> List[CatalogEntry]:
        t = tag.lower()
        with self._lock:
            out: List[CatalogEntry] = []
            for e in self._entries.values():
                if any(x.lower() == t for x in e.tags):
                    out.append(e)
            return sorted(out, key=lambda e: (e.catalog_type, e.original_id))

    def search(self, query: str) -> List[CatalogEntry]:
        """Deterministic substring search (lowercased) over id/type/tags/description."""
        if not isinstance(query, str) or not query.strip():
            raise CatalogError("query must be a non-empty string")
        q = query.lower()
        with self._lock:
            out: List[CatalogEntry] = []
            for e in self._entries.values():
                hay = " ".join(
                    [e.original_id, e.catalog_type, e.description, " ".join(e.tags)]
                ).lower()
                # also include metadata string values
                for v in e.metadata.values():
                    if isinstance(v, str):
                        hay += " " + v.lower()
                if q in hay:
                    out.append(e)
            return sorted(out, key=lambda e: (e.catalog_type, e.original_id))

    def list(self) -> List[CatalogEntry]:
        with self._lock:
            return sorted(self._entries.values(), key=lambda e: (e.catalog_type, e.original_id))

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)

    def __contains__(self, entry_id: str) -> bool:
        with self._lock:
            return entry_id in self._entries
