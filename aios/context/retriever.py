"""Context Retriever (TASK-121, M18).

Queries the hybrid index (T120) and ranks relevant chunks. Fail-closed: an
unready index is rejected (T078). Secret isolation: secret chunks are never
returned (T040/T113). Deterministic. Provenance (T001 Rule 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from aios.governance.evidence.store import EvidenceStore

from .common import ContextError, SecretBoundary, emit_evidence, sha256
from .hybrid_index import HybridIndex, HybridIndexError, HybridQueryResult


__all__ = ["RetrievalError", "RetrievalHit", "RetrievalResult", "ContextRetriever"]


class RetrievalError(ContextError):
    """Raised when retrieval fails (fail-closed, T078)."""


@dataclass
class RetrievalHit:
    chunk: str
    source: str
    score: float
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk": self.chunk,
            "source": self.source,
            "score": self.score,
            "content_hash": self.content_hash,
        }


@dataclass
class RetrievalResult:
    query: str
    hits: list[RetrievalHit]
    retriever_id: str
    policy_ref: str
    evidence_ref: str
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "hits": [h.to_dict() for h in self.hits],
            "retriever_id": self.retriever_id,
            "policy_ref": self.policy_ref,
            "evidence_ref": self.evidence_ref,
            "content_hash": self.content_hash,
        }


class ContextRetriever:
    """Query hybrid index + relevance rank + policy boundary."""

    def __init__(
        self,
        *,
        evidence_store: Optional[EvidenceStore] = None,
        run_id: str = "run-context",
        task_id: str = "TASK-121",
        producer: str = "context.retriever",
    ) -> None:
        self._store = evidence_store or EvidenceStore()
        self._run_id = run_id
        self._task_id = task_id
        self._producer = producer

    def retrieve(
        self,
        index: HybridIndex,
        query: str,
        *,
        policy_ref: str = "pol-context-retrieve",
        top_k: int = 10,
    ) -> RetrievalResult:
        # Fail-closed: index must be built (T078).
        if getattr(index, "_index_id", None) is None:
            raise RetrievalError("hybrid index is not ready (fail-closed, T078)")
        try:
            qres: HybridQueryResult = index.query(query, top_k=top_k)
        except HybridIndexError as exc:
            raise RetrievalError(str(exc)) from exc
        hits: list[RetrievalHit] = []
        for h in qres.hits:
            # Secret isolation: never return a secret chunk (T040/T113).
            if SecretBoundary.is_secret_path(h.source):
                continue
            hits.append(
                RetrievalHit(
                    chunk=h.chunk, source=h.source, score=h.combined, content_hash=h.content_hash
                )
            )
        retriever_id = f"ret-{sha256(query + str(len(hits)))[:16]}"
        canonical = "\n".join(f"{h.chunk}:{h.score}" for h in hits)
        content_hash = sha256(canonical)
        evidence_ref = emit_evidence(
            self._store,
            task_id=self._task_id,
            run_id=self._run_id,
            producer=self._producer,
            type_="retrieval",
            source="retrieve",
            content=canonical,
        )
        return RetrievalResult(
            query=query,
            hits=hits,
            retriever_id=retriever_id,
            policy_ref=policy_ref,
            evidence_ref=evidence_ref,
            content_hash=content_hash,
        )
