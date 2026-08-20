"""Knowledge index — local sources + deterministic TF retrieval (TASK-007, M1).

``KnowledgeIndex`` ingests pre-extracted text documents from four source types
(``LOCAL_DOC``/``LOCAL_PDF``/``LOCAL_CODE``/``INLINE``) and serves
deterministic keyword retrieval. Ranking is pure TF-score → source-type
priority → ``doc_id`` tiebreak — no embeddings, no LLM, no network. Every
:class:`KnowledgeDocument` is content-addressed (SHA-256 ``content_hash``) and
carries provenance so callers can build an :class:`Evidence` chain.

PDF/code docs are ingested as pre-extracted text — callers extract before
``ingest`` so M1 needs no PDF parser dependency.

Offline-first, thread-safe via :class:`threading.RLock`.

Layering: ``runtime`` layer — relative imports only / ``aios.core`` + stdlib.
"""

from __future__ import annotations

import hashlib
import re
import threading
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

__all__ = [
    "KnowledgeError",
    "KnowledgeSourceType",
    "KnowledgeSource",
    "KnowledgeDocument",
    "KnowledgeHit",
    "KnowledgeIndex",
]

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")

# Deterministic source-type priority for tiebreak (lower wins).
_SOURCE_PRIORITY: Dict[str, int] = {
    "local_doc": 0,
    "local_code": 1,
    "local_pdf": 2,
    "inline": 3,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


class KnowledgeError(Exception):
    """Raised on knowledge validation or index errors."""


class KnowledgeSourceType(str, Enum):
    """The four M1 knowledge source types."""

    LOCAL_DOC = "local_doc"
    LOCAL_PDF = "local_pdf"
    LOCAL_CODE = "local_code"
    INLINE = "inline"

    @classmethod
    def all(cls) -> List["KnowledgeSourceType"]:
        return list(cls)


@dataclass
class KnowledgeSource:
    """A registered source (usually a file/uri) that documents are ingested from."""

    source_id: str
    source_type: KnowledgeSourceType
    uri: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        source_type: KnowledgeSourceType | str,
        source_id: Optional[str] = None,
        uri: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeSource":
        if isinstance(source_type, str):
            try:
                source_type = KnowledgeSourceType(source_type)
            except ValueError as exc:
                raise KnowledgeError(f"Unknown source type {source_type!r}") from exc
        if not isinstance(source_type, KnowledgeSourceType):
            raise KnowledgeError(f"source_type must be KnowledgeSourceType, got {type(source_type).__name__}")
        return cls(
            source_id=source_id or f"ksrc-{uuid.uuid4().hex[:12]}",
            source_type=source_type,
            uri=uri or "",
            metadata=dict(metadata or {}),
        )


@dataclass
class KnowledgeDocument:
    """A single ingested document with content-hash and provenance."""

    doc_id: str
    source_id: str
    source_type: KnowledgeSourceType
    content: str
    content_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    producer: str = ""
    task_id: str = ""
    run_id: str = ""
    created_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        content: str | bytes,
        source_id: str,
        source_type: KnowledgeSourceType | str,
        producer: str = "",
        task_id: str = "",
        run_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> "KnowledgeDocument":
        if isinstance(source_type, str):
            source_type = KnowledgeSourceType(source_type)
        if isinstance(content, bytes):
            try:
                text = content.decode("utf-8")
            except Exception as exc:
                raise KnowledgeError(f"bytes content must be utf-8: {exc}") from exc
        elif isinstance(content, str):
            text = content
        else:
            raise KnowledgeError(f"content must be str or bytes, got {type(content).__name__}")
        if not source_id or not str(source_id).strip():
            raise KnowledgeError("source_id is required")
        ch = _hash_content(text)
        return cls(
            doc_id=doc_id or f"kdoc-{uuid.uuid4().hex[:12]}",
            source_id=str(source_id),
            source_type=source_type,  # type: ignore[arg-type]
            content=text,
            content_hash=ch,
            metadata=dict(metadata or {}),
            producer=producer or "",
            task_id=task_id or "",
            run_id=run_id or "",
        )

    def verify(self) -> bool:
        return _hash_content(self.content) == self.content_hash


@dataclass
class KnowledgeHit:
    """A retrieval hit carrying provenance for evidence construction."""

    doc_id: str
    source_id: str
    source_type: KnowledgeSourceType
    content: str
    content_hash: str
    score: int
    metadata: Dict[str, Any]
    producer: str = ""
    task_id: str = ""
    run_id: str = ""


class KnowledgeIndex:
    """Thread-safe in-memory inverted index with deterministic TF ranking."""

    def __init__(self) -> None:
        self._sources: Dict[str, KnowledgeSource] = {}
        self._docs: Dict[str, KnowledgeDocument] = {}
        self._by_source: Dict[str, List[str]] = defaultdict(list)
        # token -> doc_id -> tf
        self._inverted: Dict[str, Dict[str, int]] = defaultdict(dict)
        self._lock = threading.RLock()

    # -- sources --

    def add_source(self, source: KnowledgeSource) -> KnowledgeSource:
        if not isinstance(source, KnowledgeSource):
            raise KnowledgeError("KnowledgeIndex only holds KnowledgeSource")
        with self._lock:
            if source.source_id in self._sources:
                raise KnowledgeError(f"source_id already exists: {source.source_id!r}")
            self._sources[source.source_id] = source
        return source

    def get_source(self, source_id: str) -> KnowledgeSource:
        with self._lock:
            s = self._sources.get(source_id)
        if s is None:
            raise KnowledgeError(f"source not found: {source_id!r}")
        return s

    def list_sources(self) -> List[KnowledgeSource]:
        with self._lock:
            return list(self._sources.values())

    # -- ingest --

    def ingest(
        self,
        content: str | bytes,
        source_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        producer: str = "",
        task_id: str = "",
        run_id: str = "",
        doc_id: Optional[str] = None,
    ) -> KnowledgeDocument:
        """Ingest a document under ``source_id`` (must be registered)."""
        with self._lock:
            src = self._sources.get(str(source_id))
            if src is None:
                raise KnowledgeError(f"source not found: {source_id!r}")
            stype = src.source_type
        doc = KnowledgeDocument.create(
            content=content,
            source_id=str(source_id),
            source_type=stype,
            producer=producer,
            task_id=task_id,
            run_id=run_id,
            metadata=metadata,
            doc_id=doc_id,
        )
        if not doc.verify():
            raise KnowledgeError("content_hash mismatch after create")
        tokens = _tokenize(doc.content)
        tf = Counter(tokens)
        with self._lock:
            if doc.doc_id in self._docs:
                raise KnowledgeError(f"doc_id already exists: {doc.doc_id!r}")
            self._docs[doc.doc_id] = doc
            self._by_source[doc.source_id].append(doc.doc_id)
            for tok, cnt in tf.items():
                self._inverted[tok][doc.doc_id] = cnt
        return doc

    # -- read --

    def get(self, doc_id: str) -> KnowledgeDocument:
        with self._lock:
            d = self._docs.get(doc_id)
        if d is None:
            raise KnowledgeError(f"document not found: {doc_id!r}")
        return d

    def list_by_source(self, source_id: str) -> List[KnowledgeDocument]:
        with self._lock:
            ids = list(self._by_source.get(str(source_id), []))
            return [self._docs[i] for i in ids]

    def search(
        self,
        query: str,
        limit: Optional[int] = None,
        source_type: Optional[KnowledgeSourceType | str] = None,
    ) -> List[KnowledgeHit]:
        """Deterministic keyword search.

        - Tokenizes ``query`` with the same ``_TOKEN_RE`` as indexing
          (case-insensitive).
        - Scores each document by sum of TF for the query tokens (pure TF,
          no IDF — deterministic and offline).
        - Optional ``source_type`` filter.
        - Ranking: score (desc) → source-type priority (asc) → doc_id (asc).
        - ``limit`` caps results when supplied.
        """
        if not query or not query.strip():
            return []
        qtokens = _tokenize(query)
        if not qtokens:
            return []
        if isinstance(source_type, str) and source_type is not None:
            source_type = KnowledgeSourceType(source_type)
        with self._lock:
            # Aggregate TF per doc across query tokens.
            scores: Dict[str, int] = defaultdict(int)
            for tok in qtokens:
                posting = self._inverted.get(tok)
                if not posting:
                    continue
                for doc_id, cnt in posting.items():
                    scores[doc_id] += cnt
            if not scores:
                return []
            # Filter by source_type when requested.
            if source_type is not None:
                scores = {
                    did: sc
                    for did, sc in scores.items()
                    if self._docs[did].source_type == source_type
                }
                if not scores:
                    return []
            ranked: List[tuple[int, int, str, KnowledgeDocument]] = []
            for doc_id, sc in scores.items():
                doc = self._docs[doc_id]
                pri = _SOURCE_PRIORITY.get(doc.source_type.value, 99)
                ranked.append((-sc, pri, doc.doc_id, doc))
            ranked.sort(key=lambda x: (x[0], x[1], x[2]))
            hits: List[KnowledgeHit] = []
            for neg_sc, _pri, _did, doc in ranked:
                hits.append(
                    KnowledgeHit(
                        doc_id=doc.doc_id,
                        source_id=doc.source_id,
                        source_type=doc.source_type,
                        content=doc.content,
                        content_hash=doc.content_hash,
                        score=-neg_sc,
                        metadata=dict(doc.metadata),
                        producer=doc.producer,
                        task_id=doc.task_id,
                        run_id=doc.run_id,
                    )
                )
            if limit is not None:
                hits = hits[: max(0, int(limit))]
            return hits

    def verify(self, doc_id: str) -> bool:
        return self.get(doc_id).verify()

    def verify_all(self) -> bool:
        with self._lock:
            return all(d.verify() for d in self._docs.values())

    def __len__(self) -> int:
        with self._lock:
            return len(self._docs)

    def __contains__(self, doc_id: object) -> bool:
        if not isinstance(doc_id, str):
            return False
        with self._lock:
            return doc_id in self._docs

    @property
    def source_count(self) -> int:
        with self._lock:
            return len(self._sources)
