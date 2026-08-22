"""Tests for memory coordinator components."""

from __future__ import annotations

import time

import pytest

from aios.memory_coordinator.contracts import (
    MemoryCandidate,
    MemoryContext,
    MemoryQuery,
    MemoryType,
)
from aios.memory_coordinator.coordinator import MemoryCoordinator
from aios.memory_coordinator.dedup import Deduplicator
from aios.memory_coordinator.ranker import Ranker


class TestMemoryContracts:
    def test_memory_query_to_dict(self) -> None:
        q = MemoryQuery(query_text="test", token_budget=2000)
        d = q.to_dict()
        assert d["query_text"] == "test"
        assert d["token_budget"] == 2000

    def test_memory_candidate_to_dict(self) -> None:
        c = MemoryCandidate(
            memory_id="m-1",
            memory_type=MemoryType.CONVERSATION,
            content="hello",
        )
        d = c.to_dict()
        assert d["memory_id"] == "m-1"
        assert d["memory_type"] == "conversation"

    def test_memory_context_to_dict(self) -> None:
        ctx = MemoryContext(provenance=["m-1", "m-2"])
        d = ctx.to_dict()
        assert d["provenance"] == ["m-1", "m-2"]


class TestRanker:
    def test_score_relevance(self) -> None:
        ranker = Ranker()
        c = MemoryCandidate(
            memory_id="m-1",
            memory_type=MemoryType.KNOWLEDGE,
            content="Python is a programming language",
            timestamp=time.time(),
        )
        score = ranker.score(c, query_text="Python programming")
        assert score.relevance > 0
        assert score.overall > 0

    def test_rank_sorted(self) -> None:
        ranker = Ranker()
        candidates = [
            MemoryCandidate("m-1", MemoryType.CONVERSATION, "low relevance", timestamp=time.time() - 86400),
            MemoryCandidate("m-2", MemoryType.CONVERSATION, "high relevance", timestamp=time.time()),
        ]
        ranked = ranker.rank(candidates, query_text="high relevance")
        assert ranked[0][0].memory_id == "m-2"

    def test_deterministic(self) -> None:
        """AC-023-04: Deterministic ranking."""
        ranker = Ranker()
        c = MemoryCandidate("m-1", MemoryType.KNOWLEDGE, "test content", timestamp=1000.0)
        s1 = ranker.score(c, query_text="test", reference_time=2000.0)
        s2 = ranker.score(c, query_text="test", reference_time=2000.0)
        assert s1.overall == s2.overall

    def test_empty_query(self) -> None:
        ranker = Ranker()
        c = MemoryCandidate("m-1", MemoryType.KNOWLEDGE, "content")
        score = ranker.score(c, query_text="")
        assert score.overall >= 0


class TestDeduplicator:
    def test_exact_dedup(self) -> None:
        dedup = Deduplicator()
        candidates = [
            MemoryCandidate("m-1", MemoryType.CONVERSATION, "hello world", score=0.5),
            MemoryCandidate("m-2", MemoryType.CONVERSATION, "hello world", score=0.8),
            MemoryCandidate("m-3", MemoryType.CONVERSATION, "different text", score=0.6),
        ]
        result = dedup.deduplicate(candidates)
        assert len(result) == 2

    def test_keeps_highest_score(self) -> None:
        dedup = Deduplicator()
        candidates = [
            MemoryCandidate("m-1", MemoryType.CONVERSATION, "same", score=0.3),
            MemoryCandidate("m-2", MemoryType.CONVERSATION, "same", score=0.9),
        ]
        result = dedup.deduplicate(candidates)
        assert len(result) == 1
        assert result[0].memory_id == "m-2"

    def test_similarity(self) -> None:
        dedup = Deduplicator()
        sim = dedup.compute_similarity("hello world", "hello world")
        assert sim == 1.0

    def test_similarity_different(self) -> None:
        dedup = Deduplicator()
        sim = dedup.compute_similarity("hello", "completely different")
        assert sim == 0.0

    def test_empty_candidates(self) -> None:
        dedup = Deduplicator()
        assert dedup.deduplicate([]) == []


class TestMemoryCoordinator:
    def _make_store(self, candidates: list[MemoryCandidate]) -> object:
        """Create a mock memory store."""
        class MockStore:
            def __init__(self, cands: list[MemoryCandidate]) -> None:
                self._candidates = cands
            def search(self, query: str, limit: int = 10) -> list[MemoryCandidate]:
                return self._candidates[:limit]
        return MockStore(candidates)

    def test_register_and_retrieve(self) -> None:
        coord = MemoryCoordinator()
        store = self._make_store([
            MemoryCandidate("m-1", MemoryType.CONVERSATION, "hello"),
        ])
        coord.register_store(MemoryType.CONVERSATION, store)
        query = MemoryQuery(query_text="hello", memory_types=[MemoryType.CONVERSATION])
        candidates = coord.retrieve(query)
        assert len(candidates) == 1

    def test_retrieve_all_types(self) -> None:
        """AC-023-02: Accesses all 4 memory types."""
        coord = MemoryCoordinator()
        for mt in MemoryType:
            store = self._make_store([
                MemoryCandidate(f"m-{mt.value}", mt, f"content for {mt.value}"),
            ])
            coord.register_store(mt, store)
        query = MemoryQuery(memory_types=list(MemoryType))
        candidates = coord.retrieve(query)
        assert len(candidates) == 4

    def test_rank_and_dedup(self) -> None:
        coord = MemoryCoordinator()
        candidates = [
            MemoryCandidate("m-1", MemoryType.CONVERSATION, "hello", score=0.5),
            MemoryCandidate("m-2", MemoryType.CONVERSATION, "hello", score=0.8),
            MemoryCandidate("m-3", MemoryType.CONVERSATION, "world", score=0.6),
        ]
        result = coord.rank_and_dedup(candidates, "hello")
        assert len(result) == 2

    def test_select_within_budget(self) -> None:
        coord = MemoryCoordinator()
        candidates = [
            MemoryCandidate("m-1", MemoryType.CONVERSATION, "a b c", token_count=10),
            MemoryCandidate("m-2", MemoryType.CONVERSATION, "d e f", token_count=10),
            MemoryCandidate("m-3", MemoryType.CONVERSATION, "g h i", token_count=10),
        ]
        selection = coord.select_within_budget(candidates, budget=25)
        assert len(selection.selected) == 2
        assert selection.total_tokens == 20
        assert selection.dropped_count == 1

    def test_coordinate_full_pipeline(self) -> None:
        coord = MemoryCoordinator()
        for mt in MemoryType:
            store = self._make_store([
                MemoryCandidate(
                    f"m-{mt.value}",
                    mt,
                    f"content for {mt}",
                    timestamp=time.time(),
                    provenance=[f"src-{mt.value}"],
                ),
            ])
            coord.register_store(mt, store)
        query = MemoryQuery(
            query_text="content",
            memory_types=list(MemoryType),
            token_budget=100,
        )
        context = coord.coordinate(query)
        assert context.selection is not None
        assert len(context.provenance) > 0

    def test_coordinate_empty(self) -> None:
        coord = MemoryCoordinator()
        query = MemoryQuery()
        context = coord.coordinate(query)
        assert context.selection is not None
        assert len(context.selection.selected) == 0

    def test_to_dict(self) -> None:
        ctx = MemoryContext(provenance=["m-1"])
        d = ctx.to_dict()
        assert "provenance" in d
        assert "metadata" in d
