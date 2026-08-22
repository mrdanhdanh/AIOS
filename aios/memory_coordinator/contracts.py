"""Memory coordinator contracts — query, candidate, score, selection, context."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemoryType(str, Enum):
    """Types of memory."""
    CONVERSATION = "conversation"
    SESSION = "session"
    KNOWLEDGE = "knowledge"
    ARTIFACT = "artifact"


@dataclass
class MemoryQuery:
    """Unified memory query."""

    query_text: str = ""
    memory_types: list[MemoryType] = field(default_factory=lambda: list(MemoryType))
    execution_id: str = ""
    workflow_id: str = ""
    agent_id: str = ""
    scope: str = ""
    filters: dict[str, Any] = field(default_factory=dict)
    max_candidates: int = 50
    token_budget: int = 4000
    ranking_policy: str = "default"
    required_provenance: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_text": self.query_text,
            "memory_types": [t.value for t in self.memory_types],
            "execution_id": self.execution_id,
            "scope": self.scope,
            "filters": self.filters,
            "ranking_policy": self.ranking_policy,
            "token_budget": self.token_budget,
            "required_provenance": self.required_provenance,
        }


@dataclass
class MemoryCandidate:
    """A candidate memory entry."""

    memory_id: str
    memory_type: MemoryType
    content: str
    score: float = 0.0
    source: str = ""
    execution_id: str = ""
    timestamp: float = 0.0
    token_count: int = 0
    provenance: list[str] = field(default_factory=list)
    checksum: str = ""
    scope: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "score": self.score,
            "source": self.source,
            "token_count": self.token_count,
            "provenance": self.provenance,
            "checksum": self.checksum,
            "scope": self.scope,
        }


@dataclass
class MemoryScore:
    """Score for a memory candidate."""

    memory_id: str
    relevance: float = 0.0
    recency: float = 0.0
    importance: float = 0.0
    overall: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "relevance": self.relevance,
            "recency": self.recency,
            "importance": self.importance,
            "overall": self.overall,
        }


@dataclass
class MemorySelection:
    """Selected memory entries within budget."""

    selected: list[MemoryCandidate] = field(default_factory=list)
    total_tokens: int = 0
    budget: int = 0
    dropped_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_count": len(self.selected),
            "total_tokens": self.total_tokens,
            "budget": self.budget,
            "dropped_count": self.dropped_count,
        }


@dataclass
class MemoryContext:
    """Final memory context output for Context Service."""

    query: MemoryQuery | None = None
    selection: MemorySelection | None = None
    provenance: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query.to_dict() if self.query else None,
            "selection": self.selection.to_dict() if self.selection else None,
            "provenance": self.provenance,
            "metadata": self.metadata,
        }
