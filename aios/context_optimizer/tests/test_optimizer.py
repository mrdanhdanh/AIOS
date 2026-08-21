"""Tests for context optimizer components."""

from __future__ import annotations

import pytest

from aios.context_optimizer.compressor import DeterministicCompressor
from aios.context_optimizer.contracts import ContextItem, ContextPriority, OptimizedContext
from aios.context_optimizer.optimizer import ContextOptimizer


class TestContextPriority:
    def test_p0_never_drop(self) -> None:
        assert ContextPriority.P0_SYSTEM.never_drop is True

    def test_p1_never_drop(self) -> None:
        assert ContextPriority.P1_CRITICAL.never_drop is True

    def test_p2_not_never_drop(self) -> None:
        assert ContextPriority.P2_TASK.never_drop is False

    def test_ordering(self) -> None:
        assert ContextPriority.P0_SYSTEM < ContextPriority.P6_LOW


class TestContextItem:
    def test_default_token_count(self) -> None:
        item = ContextItem(item_id="c-1", priority=ContextPriority.P2_TASK, content="hello world")
        assert item.token_count == 2

    def test_is_valid(self) -> None:
        item = ContextItem(item_id="c-1", priority=ContextPriority.P2_TASK, content="hello")
        assert item.is_valid is True

    def test_expired_not_valid(self) -> None:
        item = ContextItem(item_id="c-1", priority=ContextPriority.P2_TASK, content="hello", expired=True)
        assert item.is_valid is False

    def test_superseded_not_valid(self) -> None:
        item = ContextItem(item_id="c-1", priority=ContextPriority.P2_TASK, content="hello", superseded=True)
        assert item.is_valid is False


class TestDeterministicCompressor:
    def test_truncate_no_op(self) -> None:
        comp = DeterministicCompressor()
        item = ContextItem(item_id="c-1", priority=ContextPriority.P2_TASK, content="a b c")
        result = comp.truncate(item, 10)
        assert result.content == "a b c"

    def test_truncate_reduces(self) -> None:
        comp = DeterministicCompressor()
        item = ContextItem(item_id="c-1", priority=ContextPriority.P2_TASK, content="a b c d e f g h")
        result = comp.truncate(item, 3)
        assert result.token_count == 3
        assert "[...]" in result.content

    def test_truncate_preserves_provenance(self) -> None:
        comp = DeterministicCompressor()
        item = ContextItem(item_id="c-1", priority=ContextPriority.P2_TASK, content="a b c d e", provenance=["p1"])
        result = comp.truncate(item, 2)
        assert result.provenance == ["p1"]

    def test_extract_key_sentences(self) -> None:
        comp = DeterministicCompressor()
        item = ContextItem(
            item_id="c-1",
            priority=ContextPriority.P2_TASK,
            content="First sentence. Second sentence. Third sentence. Fourth sentence.",
        )
        result = comp.extract_key_sentences(item, max_sentences=2)
        assert "First sentence" in result.content
        assert "Fourth sentence" not in result.content

    def test_compress_to_fit_within_budget(self) -> None:
        comp = DeterministicCompressor()
        items = [
            ContextItem("c-1", ContextPriority.P2_TASK, "hello", token_count=5),
        ]
        result, count = comp.compress_to_fit(items, budget=100)
        assert len(result) == 1
        assert count == 0

    def test_compress_to_fit_never_drops_p0(self) -> None:
        comp = DeterministicCompressor()
        items = [
            ContextItem("c-1", ContextPriority.P0_SYSTEM, "system instruction", token_count=50),
            ContextItem("c-2", ContextPriority.P2_TASK, "task context", token_count=30),
            ContextItem("c-3", ContextPriority.P6_LOW, "low priority", token_count=20),
        ]
        result, count = comp.compress_to_fit(items, budget=55)
        p0_items = [i for i in result if i.priority == ContextPriority.P0_SYSTEM]
        assert len(p0_items) == 1


class TestContextOptimizer:
    def test_optimize_basic(self) -> None:
        opt = ContextOptimizer()
        items = [
            ContextItem("c-1", ContextPriority.P2_TASK, "task content", token_count=10),
            ContextItem("c-2", ContextPriority.P4_HISTORY, "history", token_count=10),
        ]
        result = opt.optimize(items, budget=100)
        assert result.total_tokens <= 100
        assert len(result.items) == 2

    def test_optimize_dedup(self) -> None:
        opt = ContextOptimizer()
        items = [
            ContextItem("c-1", ContextPriority.P2_TASK, "same content", token_count=5),
            ContextItem("c-2", ContextPriority.P3_MEMORY, "same content", token_count=5),
        ]
        result = opt.optimize(items, budget=100)
        assert len(result.items) == 1

    def test_optimize_filters_expired(self) -> None:
        opt = ContextOptimizer()
        items = [
            ContextItem("c-1", ContextPriority.P2_TASK, "valid", token_count=5),
            ContextItem("c-2", ContextPriority.P2_TASK, "expired", token_count=5, expired=True),
        ]
        result = opt.optimize(items, budget=100)
        assert len(result.items) == 1

    def test_optimize_budget_enforcement(self) -> None:
        opt = ContextOptimizer()
        items = [
            ContextItem("c-1", ContextPriority.P0_SYSTEM, "system", token_count=5),
            ContextItem("c-2", ContextPriority.P2_TASK, "task", token_count=5),
            ContextItem("c-3", ContextPriority.P6_LOW, "low", token_count=5),
        ]
        result = opt.optimize(items, budget=10)
        # P0 kept (5), P2 kept (5), P6 dropped by compressor
        assert result.total_tokens <= 10
        # Only 2 items remain (P6 was dropped by compressor)
        assert len(result.items) == 2

    def test_optimize_p0_p1_never_dropped(self) -> None:
        opt = ContextOptimizer()
        items = [
            ContextItem("c-1", ContextPriority.P0_SYSTEM, "sys", token_count=50),
            ContextItem("c-2", ContextPriority.P1_CRITICAL, "crit", token_count=50),
        ]
        result = opt.optimize(items, budget=60)
        assert len(result.items) == 2
        assert result.dropped_count == 0

    def test_optimize_provenance(self) -> None:
        opt = ContextOptimizer()
        items = [
            ContextItem("c-1", ContextPriority.P2_TASK, "content", token_count=5, provenance=["p1"]),
        ]
        result = opt.optimize(items, budget=100)
        assert "p1" in result.provenance

    def test_to_dict(self) -> None:
        opt = ContextOptimizer()
        items = [ContextItem("c-1", ContextPriority.P2_TASK, "hello", token_count=5)]
        result = opt.optimize(items, budget=100)
        d = result.to_dict()
        assert "item_count" in d
        assert "budget" in d
