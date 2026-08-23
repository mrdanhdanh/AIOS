"""Semantic + Hybrid Index (TASK-120, M18).

Combines the symbol index (T118) + dependency graph (T119) with deterministic
semantic embeddings into a hybrid index, and answers hybrid queries that blend
symbolic and semantic scores. Deterministic ranking. Fail-closed on embedding
failure. Secret isolation. Provenance (T001 Rule 5).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Tuple, Union

from aios.governance.evidence.store import EvidenceStore

from .common import ContextError, SecretBoundary, emit_evidence, sha256
from .dependency_graph import DependencyGraphResult
from .symbol_index import Symbol, SymbolIndexResult


__all__ = [
    "HybridIndexError",
    "Embedding",
    "HybridHit",
    "HybridIndexResult",
    "HybridQueryResult",
    "HybridIndex",
]


class HybridIndexError(ContextError):
    """Raised when hybrid indexing/query fails (fail-closed, T078)."""


@dataclass
class Embedding:
    chunk: str
    source: str
    vector: list[float]
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {"chunk": self.chunk, "source": self.source, "content_hash": self.content_hash}


@dataclass
class HybridHit:
    chunk: str
    source: str
    symbolic_score: float
    semantic_score: float
    combined: float
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk": self.chunk,
            "source": self.source,
            "symbolic_score": self.symbolic_score,
            "semantic_score": self.semantic_score,
            "combined": self.combined,
            "content_hash": self.content_hash,
        }


@dataclass
class HybridIndexResult:
    repo_ref: str
    symbol_ref: str
    dependency_ref: str
    embeddings: list[Embedding]
    index_id: str
    evidence_ref: str
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_ref": self.repo_ref,
            "symbol_ref": self.symbol_ref,
            "dependency_ref": self.dependency_ref,
            "embeddings": [e.to_dict() for e in self.embeddings],
            "index_id": self.index_id,
            "evidence_ref": self.evidence_ref,
            "content_hash": self.content_hash,
        }


@dataclass
class HybridQueryResult:
    repo_ref: str
    query: str
    hits: list[HybridHit]
    index_id: str
    evidence_ref: str
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_ref": self.repo_ref,
            "query": self.query,
            "hits": [h.to_dict() for h in self.hits],
            "index_id": self.index_id,
            "evidence_ref": self.evidence_ref,
            "content_hash": self.content_hash,
        }


# Deterministic embedding dimension (no LLM; hash-based bag-of-tokens).
EMBED_DIM = 64


def _default_embed(text: str) -> list[float]:
    vec = [0.0] * EMBED_DIM
    tokens = re.findall(r"[a-z0-9_]+", text.lower())
    if not tokens:
        return vec
    for tok in tokens:
        idx = int(sha256(tok)[:8], 16) % EMBED_DIM
        vec[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


ChunkInput = Union[str, Tuple[str, str]]


class HybridIndex:
    """Symbol backbone + dependency context + semantic embedding + hybrid query."""

    def __init__(
        self,
        *,
        evidence_store: Optional[EvidenceStore] = None,
        run_id: str = "run-context",
        task_id: str = "TASK-120",
        producer: str = "context.hybrid_index",
        embed_fn: Optional[Callable[[str], list[float]]] = None,
    ) -> None:
        self._store = evidence_store or EvidenceStore()
        self._run_id = run_id
        self._task_id = task_id
        self._producer = producer
        self._embed = embed_fn or _default_embed
        self._symbols: list[Symbol] = []
        self._deps: Optional[DependencyGraphResult] = None
        self._chunks: list[Embedding] = []
        self._index_id: Optional[str] = None
        self._evidence_ref: str = ""
        self._content_hash: str = ""

    def build(
        self,
        symbol_index: SymbolIndexResult,
        dependency: DependencyGraphResult,
        chunks: list[ChunkInput],
        *,
        policy_ref: str = "pol-context-hybrid",
    ) -> HybridIndexResult:
        if dependency.has_cycle:
            raise HybridIndexError("refusing to build hybrid index over a cyclic dependency graph")
        self._symbols = list(symbol_index.symbols)
        self._deps = dependency
        embeddings: list[Embedding] = []
        for item in chunks:
            if isinstance(item, tuple):
                text, source = item
            else:
                text, source = item, ""
            if SecretBoundary.is_secret_path(source):
                raise HybridIndexError("refusing to embed secret chunk")
            try:
                vec = self._embed(text)
            except Exception as exc:
                raise HybridIndexError(f"embedding failed: {exc}") from exc
            embeddings.append(
                Embedding(chunk=text, source=source, vector=vec, content_hash=sha256(text))
            )
        self._chunks = embeddings
        self._index_id = f"hyb-{sha256(str(len(self._symbols)) + str(len(embeddings)))[:16]}"
        canonical = "\n".join(e.content_hash for e in embeddings)
        self._content_hash = sha256(canonical)
        self._evidence_ref = emit_evidence(
            self._store,
            task_id=self._task_id,
            run_id=self._run_id,
            producer=self._producer,
            type_="hybrid_index",
            source="hybrid",
            content=canonical,
        )
        return HybridIndexResult(
            repo_ref="hybrid",
            symbol_ref=symbol_index.index_id,
            dependency_ref=dependency.graph_id,
            embeddings=embeddings,
            index_id=self._index_id,
            evidence_ref=self._evidence_ref,
            content_hash=self._content_hash,
        )

    def query(self, query: str, *, top_k: int = 10) -> HybridQueryResult:
        if self._index_id is None:
            raise HybridIndexError("hybrid index is not built (fail-closed)")
        q_vec = self._embed(query)
        q_tokens = set(re.findall(r"[a-z0-9_]+", query.lower()))
        hits: list[HybridHit] = []
        for emb in self._chunks:
            semantic = _cosine(q_vec, emb.vector)
            chunk_tokens = set(re.findall(r"[a-z0-9_]+", emb.chunk.lower()))
            sym = len(q_tokens & chunk_tokens) / max(1, len(q_tokens))
            combined = round(0.5 * sym + 0.5 * semantic, 6)
            hits.append(
                HybridHit(
                    chunk=emb.chunk,
                    source=emb.source,
                    symbolic_score=round(sym, 6),
                    semantic_score=round(semantic, 6),
                    combined=combined,
                    content_hash=emb.content_hash,
                )
            )
        hits.sort(key=lambda h: (-h.combined, h.chunk))
        hits = hits[:top_k]
        canonical = "\n".join(f"{h.chunk}:{h.combined}" for h in hits)
        content_hash = sha256(canonical)
        evidence_ref = emit_evidence(
            self._store,
            task_id=self._task_id,
            run_id=self._run_id,
            producer=self._producer,
            type_="hybrid_query",
            source="query",
            content=canonical,
        )
        return HybridQueryResult(
            repo_ref="hybrid",
            query=query,
            hits=hits,
            index_id=self._index_id,
            evidence_ref=evidence_ref,
            content_hash=content_hash,
        )
