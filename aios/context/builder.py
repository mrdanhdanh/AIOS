"""Context Builder + Budget (TASK-122, M18).

Assembles retrieved context (T121) into a final context, enforces a token/size
budget (T024), and trims by priority when over budget (fail-closed). Deterministic.
Secret isolation. Provenance (T001 Rule 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from aios.context_optimizer.contracts import ContextPriority
from aios.governance.evidence.store import EvidenceStore

from .common import ContextError, SecretBoundary, emit_evidence, sha256
from .retriever import RetrievalResult


__all__ = ["BuildError", "BuiltChunk", "BuiltContext", "ContextBuilder"]


class BuildError(ContextError):
    """Raised when context building fails (fail-closed, T024/T078)."""


@dataclass
class BuiltChunk:
    chunk: str
    source: str
    priority: int
    token_count: int
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk": self.chunk,
            "source": self.source,
            "priority": self.priority,
            "token_count": self.token_count,
            "content_hash": self.content_hash,
        }


@dataclass
class BuiltContext:
    retrieval_ref: str
    assembled_chunks: list[BuiltChunk]
    budget_used: int
    budget_limit: int
    within_budget: bool
    evidence_ref: str
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "retrieval_ref": self.retrieval_ref,
            "assembled_chunks": [c.to_dict() for c in self.assembled_chunks],
            "budget_used": self.budget_used,
            "budget_limit": self.budget_limit,
            "within_budget": self.within_budget,
            "evidence_ref": self.evidence_ref,
            "content_hash": self.content_hash,
        }


def _priority_for_score(score: float) -> int:
    """Higher relevance score -> higher priority (lower number, T024)."""
    if score >= 0.8:
        return ContextPriority.P1_CRITICAL.value
    if score >= 0.5:
        return ContextPriority.P2_TASK.value
    if score >= 0.2:
        return ContextPriority.P3_MEMORY.value
    return ContextPriority.P6_LOW.value


class ContextBuilder:
    """Assembly + budget enforce + priority trim."""

    def __init__(
        self,
        *,
        evidence_store: Optional[EvidenceStore] = None,
        run_id: str = "run-context",
        task_id: str = "TASK-122",
        producer: str = "context.builder",
    ) -> None:
        self._store = evidence_store or EvidenceStore()
        self._run_id = run_id
        self._task_id = task_id
        self._producer = producer

    def build(
        self,
        retrieval: RetrievalResult,
        *,
        budget_limit: int = 1000,
        policy_ref: str = "pol-context-build",
    ) -> BuiltContext:
        if not retrieval.hits:
            raise BuildError("nothing retrieved to build context (fail-closed)")
        chunks: list[BuiltChunk] = []
        for h in retrieval.hits:
            if SecretBoundary.is_secret_path(h.source):
                raise BuildError("refusing to build context containing a secret chunk (T040)")
            token_count = max(1, len(h.chunk.split()))
            chunks.append(
                BuiltChunk(
                    chunk=h.chunk,
                    source=h.source,
                    priority=_priority_for_score(h.score),
                    token_count=token_count,
                    content_hash=h.content_hash,
                )
            )
        # Sort by priority (ascending = higher priority first).
        chunks.sort(key=lambda c: c.priority)
        # Enforce budget: keep highest priority first; if a never-drop (P0/P1)
        # chunk cannot fit, fail-closed (T024).
        kept: list[BuiltChunk] = []
        used = 0
        for c in chunks:
            if used + c.token_count <= budget_limit:
                kept.append(c)
                used += c.token_count
            elif c.priority <= ContextPriority.P1_CRITICAL.value:
                raise BuildError(
                    "cannot fit mandatory (P0/P1) chunk within budget (fail-closed, T024)"
                )
            else:
                # Priority trim: drop lowest-priority chunk.
                continue
        within = used <= budget_limit
        canonical = "\n".join(f"{c.chunk}:{c.priority}" for c in kept)
        content_hash = sha256(canonical)
        evidence_ref = emit_evidence(
            self._store,
            task_id=self._task_id,
            run_id=self._run_id,
            producer=self._producer,
            type_="build",
            source="build",
            content=canonical,
        )
        return BuiltContext(
            retrieval_ref=retrieval.retriever_id,
            assembled_chunks=kept,
            budget_used=used,
            budget_limit=budget_limit,
            within_budget=within,
            evidence_ref=evidence_ref,
            content_hash=content_hash,
        )
