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
    "KnowledgeChunk",
    "KnowledgeHit",
    "KnowledgeChunker",
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
class KnowledgeChunk:
    """A deterministic chunk derived from a document — spec section 2.6.

    Each chunk is content-addressed and carries full provenance back to
    ``source_id → document_id → chunk_id`` so a retriever can emit evidence
    as required by AC-007-05 / AC-007-10.
    """

    chunk_id: str
    source_id: str
    document_id: str
    source_type: KnowledgeSourceType
    content: str
    content_hash: str
    location: Dict[str, Any]  # e.g. {"chunk_index": 0, "char_start": 0, "char_end": 512}
    metadata: Dict[str, Any] = field(default_factory=dict)
    producer: str = ""
    task_id: str = ""
    run_id: str = ""
    created_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        content: str,
        source_id: str,
        document_id: str,
        source_type: KnowledgeSourceType | str,
        location: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        producer: str = "",
        task_id: str = "",
        run_id: str = "",
        chunk_id: Optional[str] = None,
    ) -> "KnowledgeChunk":
        if isinstance(source_type, str):
            source_type = KnowledgeSourceType(source_type)
        if not source_id or not str(source_id).strip():
            raise KnowledgeError("source_id is required for chunk")
        if not document_id or not str(document_id).strip():
            raise KnowledgeError("document_id is required for chunk")
        return cls(
            chunk_id=chunk_id or f"kchunk-{uuid.uuid4().hex[:12]}",
            source_id=str(source_id),
            document_id=str(document_id),
            source_type=source_type,  # type: ignore[arg-type]
            content=content,
            content_hash=_hash_content(content),
            location=dict(location or {}),
            metadata=dict(metadata or {}),
            producer=producer or "",
            task_id=task_id or "",
            run_id=run_id or "",
        )

    def verify(self) -> bool:
        return _hash_content(self.content) == self.content_hash


class KnowledgeChunker:
    """Deterministic fixed-window chunker with overlap.

    Pure-Python, no tokenizer dependency. Splits on character boundaries with
    configurable ``chunk_size`` and ``overlap`` so the output is fully
    deterministic. Callers may pass their own chunker; this one covers the
    minimal M1 requirement from section 2.6 without an external NLP dependency.
    """

    def __init__(self, chunk_size: int = 800, overlap: int = 100) -> None:
        if chunk_size <= 0:
            raise KnowledgeError("chunk_size must be > 0")
        if overlap < 0 or overlap >= chunk_size:
            raise KnowledgeError("overlap must satisfy 0 <= overlap < chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: KnowledgeDocument) -> List[KnowledgeChunk]:
        text = doc.content
        if not text:
            return []
        chunks: List[KnowledgeChunk] = []
        step = self.chunk_size - self.overlap
        for idx, start in enumerate(range(0, len(text), step)):
            end = min(start + self.chunk_size, len(text))
            piece = text[start:end]
            if not piece.strip():
                if end >= len(text):
                    break
                continue
            loc = {"chunk_index": idx, "char_start": start, "char_end": end}
            # Preserve document provenance into the chunk.
            ch = KnowledgeChunk.create(
                content=piece,
                source_id=doc.source_id,
                document_id=doc.doc_id,
                source_type=doc.source_type,
                location=loc,
                metadata=dict(doc.metadata),
                producer=doc.producer,
                task_id=doc.task_id,
                run_id=doc.run_id,
            )
            chunks.append(ch)
            if end >= len(text):
                break
        return chunks

    def chunk_text(
        self,
        text: str,
        source_id: str,
        document_id: str,
        source_type: KnowledgeSourceType | str = KnowledgeSourceType.INLINE,
        metadata: Optional[Dict[str, Any]] = None,
        producer: str = "",
        task_id: str = "",
        run_id: str = "",
    ) -> List[KnowledgeChunk]:
        # Delegate to chunk_document via a synthetic document so provenance and
        # chunk hashing are consistent.
        doc = KnowledgeDocument.create(
            content=text,
            source_id=source_id,
            source_type=source_type,
            producer=producer,
            task_id=task_id,
            run_id=run_id,
            metadata=metadata,
        )
        # Use the synthetic document's id as document_id for traceability while
        # preserving caller-supplied document_id when provided.
        if document_id != doc.doc_id:
            # Rebind document_id so the caller's id is authoritative.
            doc.doc_id = document_id
        chunks: List[KnowledgeChunk] = []
        step = self.chunk_size - self.overlap
        for idx, start in enumerate(range(0, len(text), step)):
            end = min(start + self.chunk_size, len(text))
            piece = text[start:end]
            if not piece.strip():
                if end >= len(text):
                    break
                continue
            loc = {"chunk_index": idx, "char_start": start, "char_end": end}
            ch = KnowledgeChunk.create(
                content=piece,
                source_id=source_id,
                document_id=document_id,
                source_type=KnowledgeSourceType(source_type) if isinstance(source_type, str) else source_type,  # type: ignore[arg-type]
                location=loc,
                metadata=dict(metadata or {}),
                producer=producer,
                task_id=task_id,
                run_id=run_id,
            )
            chunks.append(ch)
            if end >= len(text):
                break
        return chunks


@dataclass
class KnowledgeHit:
    """A retrieval hit carrying provenance for evidence construction.

    When the hit originates from a chunk, ``chunk_id``/``document_id``/``location``
    are populated; for document-level hits they reflect the document itself.
    """

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
    # Chunk-level provenance (section 2.6 / 2.9) — present when retrieval is chunk-aware.
    chunk_id: Optional[str] = None
    document_id: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

    def evidence(self) -> Dict[str, Any]:
        """Return the minimal evidence dict required by AC-007-05/10."""
        return {
            "source_id": self.source_id,
            "document_id": self.document_id or self.doc_id,
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "location": self.location,
            "content_hash": self.content_hash,
            "created_at": self.created_at,
            "producer": self.producer,
            "task_id": self.task_id,
            "run_id": self.run_id,
        }


class KnowledgeIndex:
    """Thread-safe in-memory inverted index with deterministic TF ranking.

    Supports both document-level and chunk-level indexing. Chunk indexing is
    opt-in via ``ingest_chunks`` so existing document-only callers are
    unaffected.
    """

    def __init__(self) -> None:
        self._sources: Dict[str, KnowledgeSource] = {}
        self._docs: Dict[str, KnowledgeDocument] = {}
        self._by_source: Dict[str, List[str]] = defaultdict(list)
        # token -> doc_id -> tf
        self._inverted: Dict[str, Dict[str, int]] = defaultdict(dict)
        # Chunk substrate (section 2.6): separate inverted index per chunk.
        self._chunks: Dict[str, KnowledgeChunk] = {}
        self._by_document: Dict[str, List[str]] = defaultdict(list)
        self._chunk_inverted: Dict[str, Dict[str, int]] = defaultdict(dict)
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

    # -- chunks --

    def ingest_chunks(self, chunks: List[KnowledgeChunk]) -> List[KnowledgeChunk]:
        """Index a batch of chunks (e.g. from :class:`KnowledgeChunker`).

        Chunks must reference a registered ``source_id``. Duplicate
        ``chunk_id`` is rejected. Indexing is additive — chunk TF is kept in
        a separate inverted index so chunk search does not perturb
        document-level ``search()`` ranking.
        """
        if not chunks:
            return []
        # Validate all chunk source_ids up front under the lock's view.
        with self._lock:
            for ch in chunks:
                if ch.source_id not in self._sources:
                    raise KnowledgeError(f"source not found for chunk: {ch.source_id!r}")
                if ch.chunk_id in self._chunks:
                    raise KnowledgeError(f"chunk_id already exists: {ch.chunk_id!r}")
        # Build TF outside the write lock for the batch, then commit.
        batch_tf: List[tuple[KnowledgeChunk, Counter]] = []
        for ch in chunks:
            if not ch.verify():
                raise KnowledgeError(f"content_hash mismatch for chunk {ch.chunk_id!r}")
            batch_tf.append((ch, Counter(_tokenize(ch.content))))
        with self._lock:
            for ch, tf in batch_tf:
                if ch.chunk_id in self._chunks:
                    raise KnowledgeError(f"chunk_id already exists: {ch.chunk_id!r}")
                self._chunks[ch.chunk_id] = ch
                self._by_document[ch.document_id].append(ch.chunk_id)
                for tok, cnt in tf.items():
                    self._chunk_inverted[tok][ch.chunk_id] = cnt
        return chunks

    def get_chunk(self, chunk_id: str) -> KnowledgeChunk:
        with self._lock:
            c = self._chunks.get(chunk_id)
        if c is None:
            raise KnowledgeError(f"chunk not found: {chunk_id!r}")
        return c

    def list_chunks(self, document_id: str) -> List[KnowledgeChunk]:
        with self._lock:
            ids = list(self._by_document.get(str(document_id), []))
            return [self._chunks[i] for i in ids]

    @property
    def chunk_count(self) -> int:
        with self._lock:
            return len(self._chunks)

    def verify_chunks(self) -> bool:
        with self._lock:
            return all(c.verify() for c in self._chunks.values())

    def search_chunks(
        self,
        query: str,
        limit: Optional[int] = None,
        source_type: Optional[KnowledgeSourceType | str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[KnowledgeHit]:
        """Deterministic chunk-level keyword search with optional metadata filter.

        Same ranking contract as document search (TF → source-type priority →
        chunk_id) plus chunk provenance ``chunk_id``/``document_id``/``location``
        on each hit. ``metadata_filter`` requires an exact match on each
        supplied key against the candidate chunk's ``metadata``.
        """
        if not query or not query.strip():
            return []
        qtokens = _tokenize(query)
        if not qtokens:
            return []
        if isinstance(source_type, str) and source_type is not None:
            source_type = KnowledgeSourceType(source_type)
        with self._lock:
            scores: Dict[str, int] = defaultdict(int)
            for tok in qtokens:
                posting = self._chunk_inverted.get(tok)
                if not posting:
                    continue
                for cid, cnt in posting.items():
                    scores[cid] += cnt
            if not scores:
                return []
            # Optional filters before ranking.
            if source_type is not None or metadata_filter is not None:
                filtered: Dict[str, int] = {}
                for cid, sc in scores.items():
                    ch = self._chunks[cid]
                    if source_type is not None and ch.source_type != source_type:
                        continue
                    if metadata_filter is not None:
                        if not all(ch.metadata.get(k) == v for k, v in metadata_filter.items()):
                            continue
                    filtered[cid] = sc
                scores = filtered
                if not scores:
                    return []
            ranked: List[tuple[int, int, str, KnowledgeChunk]] = []
            for cid, sc in scores.items():
                ch = self._chunks[cid]
                pri = _SOURCE_PRIORITY.get(ch.source_type.value, 99)
                ranked.append((-sc, pri, ch.chunk_id, ch))
            ranked.sort(key=lambda x: (x[0], x[1], x[2]))
            hits: List[KnowledgeHit] = []
            for neg_sc, _pri, _cid, ch in ranked:
                hits.append(
                    KnowledgeHit(
                        doc_id=ch.chunk_id,
                        source_id=ch.source_id,
                        source_type=ch.source_type,
                        content=ch.content,
                        content_hash=ch.content_hash,
                        score=-neg_sc,
                        metadata=dict(ch.metadata),
                        producer=ch.producer,
                        task_id=ch.task_id,
                        run_id=ch.run_id,
                        chunk_id=ch.chunk_id,
                        document_id=ch.document_id,
                        location=dict(ch.location) if ch.location else None,
                        created_at=ch.created_at,
                    )
                )
            if limit is not None:
                hits = hits[: max(0, int(limit))]
            return hits

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
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[KnowledgeHit]:
        """Deterministic keyword search.

        - Tokenizes ``query`` with the same ``_TOKEN_RE`` as indexing
          (case-insensitive).
        - Scores each document by sum of TF for the query tokens (pure TF,
          no IDF — deterministic and offline).
        - Optional ``source_type`` filter, and optional ``metadata_filter``
          (exact key=value match against candidate metadata).
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
            # Filters before ranking (source_type + optional metadata exact-match).
            if source_type is not None or metadata_filter is not None:
                filtered: Dict[str, int] = {}
                for did, sc in scores.items():
                    doc = self._docs[did]
                    if source_type is not None and doc.source_type != source_type:
                        continue
                    if metadata_filter is not None:
                        if not all(doc.metadata.get(k) == v for k, v in metadata_filter.items()):
                            continue
                    filtered[did] = sc
                scores = filtered
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
                        document_id=doc.doc_id,
                        created_at=doc.created_at,
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
