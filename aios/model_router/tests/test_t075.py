"""Tests for TASK-075 — Performance & Cost + Model Independence.

Covers every Acceptance Criterion and Test Matrix row:
- intent -> policy route (not hardcoded)
- provider down -> fallback route (T055)
- deterministic SUFFICIENT -> LLM call count 0 (Rule 4)
- deterministic INSUFFICIENT -> LLM fallback + validator
- same intent + policy -> same route (deterministic)
- provenance evidence on routes
- integration with Model Router + Deterministic + Recovery
"""

from __future__ import annotations

import pytest

from aios.governance.deterministic import ValidationError
from aios.model_router import (
    DeterministicRouter,
    ModelCandidate,
    ModelRoute,
    ModelRouter,
    RoutingPolicy,
)


def _router() -> ModelRouter:
    router = ModelRouter()
    # Cost and latency are anti-correlated so policy choice is observable.
    router.register_candidate(
        ModelCandidate("fast-model", "provider-fast", cost_per_token=0.0001, latency_ms=10, capabilities=["chat"])
    )
    router.register_candidate(
        ModelCandidate("cheap-model", "provider-cheap", cost_per_token=0.000001, latency_ms=500, capabilities=["chat"])
    )
    return router


class TestPolicyDrivenRouting:
    def test_route_not_hardcoded_policy_drives_selection(self) -> None:
        # AC1: selection via model router (policy-driven), not hardcoded.
        router = _router()
        cost_route = router.route("chat", RoutingPolicy.COST_OPTIMIZED)
        latency_route = router.route("chat", RoutingPolicy.LATENCY_OPTIMIZED)
        # Different policies -> different selected providers.
        assert cost_route.selected_provider == "provider-cheap"
        assert latency_route.selected_provider == "provider-fast"
        assert cost_route.selected_provider != latency_route.selected_provider

    def test_route_fail_closed_no_eligible(self) -> None:
        router = _router()
        route = router.route("chat", RoutingPolicy.BALANCED, required_capabilities=["nonexistent"])
        assert route.selected_provider == ""
        assert route.selected_model is None

    def test_route_has_provenance_evidence(self) -> None:
        # AC6: every route has provenance evidence.
        router = _router()
        route = router.route("chat", RoutingPolicy.COST_OPTIMIZED)
        assert isinstance(route, ModelRoute)
        assert route.evidence_ref
        assert route.provenance
        assert route.fallback_providers  # fallback chain present


class TestFallbackRouting:
    def test_provider_down_fallback_route(self) -> None:
        # AC4 / T055: provider down -> fallback route.
        router = _router()
        route = router.route("chat", RoutingPolicy.COST_OPTIMIZED)
        assert route.selected_provider == "provider-cheap"
        assert "provider-fast" in route.fallback_providers

        fb = router.attempt_fallback(route, "provider-cheap", "provider provider-cheap unavailable")
        assert fb is not None
        assert fb.selected_provider == "provider-fast"
        assert fb.fallback_providers == []
        assert any("fallback_from:provider-cheap" in p for p in fb.provenance)

    def test_unknown_failure_safe_stops(self) -> None:
        # Fail-closed: unknown failure -> no fallback route (SAFE_STOP).
        router = _router()
        route = router.route("chat", RoutingPolicy.COST_OPTIMIZED)
        fb = router.attempt_fallback(route, "provider-cheap", "mysterious unknown failure")
        assert fb is None


class TestDeterministicFirst:
    def test_sufficient_intent_llm_call_count_zero(self) -> None:
        # AC5 / Rule 4: deterministic SUFFICIENT -> LLM call count 0.
        router = _router()
        dr = DeterministicRouter(router)
        _route, llm_calls = dr.route("status", RoutingPolicy.BALANCED)
        assert llm_calls == 0

    def test_insufficient_intent_llm_fallback_validator(self) -> None:
        # AC5 / Rule 4: deterministic INSUFFICIENT -> LLM fallback + validator.
        router = _router()
        validator_calls: list[str] = []
        dr = DeterministicRouter(
            router,
            llm_fallback=lambda nr: f"plan for {nr.intent}",
            validator=lambda raw: (validator_calls.append(raw) or True),
        )
        _route, llm_calls = dr.route("translate this document", RoutingPolicy.BALANCED)
        assert llm_calls == 1
        assert validator_calls  # validator was invoked on the LLM output

    def test_insufficient_validator_failure_raises(self) -> None:
        router = _router()
        dr = DeterministicRouter(
            router,
            llm_fallback=lambda nr: "bad output",
            validator=lambda raw: False,
        )
        with pytest.raises(ValidationError):
            dr.route("translate this document", RoutingPolicy.BALANCED)


class TestDeterministicRouteStability:
    def test_same_intent_policy_same_route(self) -> None:
        # AC7: same intent + policy -> same route (deterministic).
        router = _router()
        r1 = router.route("chat", RoutingPolicy.COST_OPTIMIZED)
        r2 = router.route("chat", RoutingPolicy.COST_OPTIMIZED)
        assert r1.selected_provider == r2.selected_provider
        assert r1.selected_model == r2.selected_model
        assert r1.fallback_providers == r2.fallback_providers


class TestIntegration:
    def test_full_flow_model_router_deterministic_recovery(self) -> None:
        # AC8: integrates Model Router + Deterministic + Recovery.
        router = _router()
        dr = DeterministicRouter(router)
        route, llm_calls = dr.route("status", RoutingPolicy.COST_OPTIMIZED)
        assert llm_calls == 0
        assert route.selected_provider == "provider-cheap"
        # Provider fails -> recovery-driven fallback.
        fb = router.attempt_fallback(route, "provider-cheap", "provider provider-cheap down")
        assert fb is not None
        assert fb.selected_provider == "provider-fast"
