"""Tests for TASK-023 MemoryFilter and provenance/observability (AC-023-08)."""

from __future__ import annotations

from aios.memory_coordinator.contracts import (
    MemoryCandidate,
    MemoryContext,
    MemoryQuery,
    MemoryType,
)
from aios.memory_coordinator.coordinator import MemoryCoordinator
from aios.memory_coordinator.filter import MemoryFilter


def _candidate(memory_id: str, provenance: list[str] | None = None, scope: str = "") -> MemoryCandidate:
    return MemoryCandidate(
        memory_id=memory_id,
        memory_type=MemoryType.CONVERSATION,
        content="x",
        provenance=provenance or [],
        scope=scope,
    )


def test_filter_excludes_missing_provenance_when_required() -> None:
    q = MemoryQuery(query_text="q", required_provenance=True)
    cands = [_candidate("a", provenance=["s1"]), _candidate("b", provenance=[])]
    out = MemoryFilter().apply(q, cands)
    assert [c.memory_id for c in out] == ["a"]


def test_filter_allows_missing_provenance_when_not_required() -> None:
    q = MemoryQuery(query_text="q", required_provenance=False)
    cands = [_candidate("a", provenance=[]), _candidate("b", provenance=["s"])]
    out = MemoryFilter().apply(q, cands)
    assert len(out) == 2


def test_filter_scope_isolation() -> None:
    q = MemoryQuery(query_text="q", scope="tenant-A")
    cands = [_candidate("a", provenance=["s"], scope="tenant-A"),
             _candidate("b", provenance=["s"], scope="tenant-B")]
    out = MemoryFilter().apply(q, cands)
    assert [c.memory_id for c in out] == ["a"]


def test_filter_metadata_filters() -> None:
    q = MemoryQuery(query_text="q", required_provenance=False,
                    filters={"tag": "oracle"})
    cands = [
        _candidate("a", provenance=["s"]),
        _candidate("b", provenance=["s"]),
    ]
    cands[1].metadata["tag"] = "oracle"
    out = MemoryFilter().apply(q, cands)
    assert [c.memory_id for c in out] == ["b"]


def test_coordinator_tracks_retrieval_stats() -> None:
    coord = MemoryCoordinator()
    q = MemoryQuery(query_text="q", memory_types=[MemoryType.CONVERSATION])
    ctx: MemoryContext = coord.coordinate(q)
    assert ctx.metadata["retrieval_stats"]["retrieve_calls"] == 1
    assert coord.retrieval_stats()["retrieve_calls"] == 1
