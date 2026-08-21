"""Tests for model router components."""

from __future__ import annotations

import pytest

from aios.model_router.contracts import ModelCandidate, ModelRequirement, RoutingPolicy
from aios.model_router.health import ModelHealthTracker
from aios.model_router.router import ModelRouter


class TestModelRouter:
    def _setup_router(self) -> ModelRouter:
        router = ModelRouter()
        router.register_candidate(ModelCandidate("gpt-4", "openai", context_window=8192, cost_per_token=0.00003, latency_ms=200, capabilities=["chat", "code"]))
        router.register_candidate(ModelCandidate("gpt-3.5", "openai", context_window=4096, cost_per_token=0.000002, latency_ms=100, capabilities=["chat"]))
        router.register_candidate(ModelCandidate("mock", "mock", context_window=2048, cost_per_token=0.0, latency_ms=10, capabilities=["chat", "code"], metadata={"offline": True}))
        return router

    def test_select_basic(self) -> None:
        router = self._setup_router()
        req = ModelRequirement(task_type="chat")
        sel = router.select(req)
        assert sel.selected is True
        assert sel.model is not None

    def test_select_cost_optimized(self) -> None:
        router = self._setup_router()
        req = ModelRequirement(policy=RoutingPolicy.COST_OPTIMIZED)
        sel = router.select(req)
        assert sel.selected is True
        assert sel.model.model_id == "mock"  # cost=0

    def test_select_capability_filter(self) -> None:
        router = self._setup_router()
        req = ModelRequirement(required_capabilities=["code"])
        sel = router.select(req)
        assert sel.selected is True
        # gpt-3.5 doesn't have code, so rejected
        assert "gpt-3.5" in sel.alternatives_rejected or sel.model.model_id != "gpt-3.5"

    def test_select_no_eligible_fail_closed(self) -> None:
        router = self._setup_router()
        req = ModelRequirement(
            required_capabilities=["nonexistent"],
        )
        sel = router.select(req)
        assert sel.selected is False
        assert sel.model is None

    def test_select_context_window(self) -> None:
        router = self._setup_router()
        req = ModelRequirement(min_context_window=10000)
        sel = router.select(req)
        assert sel.selected is False  # No model has 10000+ window

    def test_select_cost_limit(self) -> None:
        router = self._setup_router()
        req = ModelRequirement(max_cost_per_token=0.000001)
        sel = router.select(req)
        assert sel.selected is True
        assert sel.model.cost_per_token <= 0.000001

    def test_health_tracker(self) -> None:
        tracker = ModelHealthTracker()
        assert tracker.is_healthy("gpt-4") is True
        tracker.record_failure("gpt-4")
        tracker.record_failure("gpt-4")
        tracker.record_failure("gpt-4")
        assert tracker.is_healthy("gpt-4") is False

    def test_unhealthy_model_rejected(self) -> None:
        tracker = ModelHealthTracker()
        tracker.record_failure("gpt-4")
        tracker.record_failure("gpt-4")
        tracker.record_failure("gpt-4")
        router = ModelRouter(health_tracker=tracker)
        router.register_candidate(ModelCandidate("gpt-4", "openai"))
        router.register_candidate(ModelCandidate("mock", "mock", cost_per_token=0.0))
        req = ModelRequirement(policy=RoutingPolicy.COST_OPTIMIZED)
        sel = router.select(req)
        assert sel.model.model_id == "mock"

    def test_history(self) -> None:
        router = self._setup_router()
        router.select(ModelRequirement())
        router.select(ModelRequirement())
        assert len(router.get_history()) == 2

    def test_provenance(self) -> None:
        router = self._setup_router()
        sel = router.select(ModelRequirement(policy=RoutingPolicy.BALANCED))
        assert len(sel.provenance) > 0

    def test_to_dict(self) -> None:
        router = self._setup_router()
        sel = router.select(ModelRequirement())
        d = sel.to_dict()
        assert "selected" in d
        assert "explanation" in d
