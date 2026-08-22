"""Tests for TASK-025 FallbackResolver and requirement/candidate fields."""

from __future__ import annotations

from aios.model_router.contracts import (
    ModelCandidate,
    ModelRequirement,
    RoutingPolicy,
)
from aios.model_router.fallback import FallbackResolver


def _candidates() -> list[ModelCandidate]:
    return [
        ModelCandidate("gpt-4", "openai", quality=0.9, capabilities=["tool_calling"]),
        ModelCandidate("opus", "anthropic", quality=0.95, capabilities=["tool_calling", "structured_output"]),
        ModelCandidate("local", "ollama", quality=0.6, is_healthy=False),
    ]


def test_requirement_and_candidate_new_fields() -> None:
    req = ModelRequirement(minimum_quality=0.5, preferred_provider="openai",
                           tool_calling_required=True, fallback_allowed=False)
    assert req.minimum_quality == 0.5
    assert req.tool_calling_required is True
    c = ModelCandidate("x", "y", quality=0.8, availability=0.5)
    assert c.quality == 0.8 and c.availability == 0.5


def test_fallback_excludes_unhealthy_and_under_quality() -> None:
    req = ModelRequirement(minimum_quality=0.7)
    chain = FallbackResolver().resolve(req, _candidates())
    ids = [c.model_id for c in chain]
    assert "local" not in ids
    assert all(c.quality >= 0.7 for c in chain)


def test_fallback_prefers_provider() -> None:
    req = ModelRequirement(preferred_provider="openai")
    chain = FallbackResolver().resolve(req, _candidates())
    assert chain[0].provider == "openai"


def test_fallback_disallowed_limits_to_preferred() -> None:
    req = ModelRequirement(preferred_provider="openai", fallback_allowed=False)
    chain = FallbackResolver().resolve(req, _candidates())
    assert len(chain) == 1
    assert chain[0].provider == "openai"


def test_fallback_tool_calling_required() -> None:
    req = ModelRequirement(tool_calling_required=True)
    chain = FallbackResolver().resolve(req, _candidates())
    assert all("tool_calling" in c.capabilities for c in chain)
