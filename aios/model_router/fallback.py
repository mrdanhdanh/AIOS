"""Fallback resolver — builds an ordered fallback chain for model selection.

Deterministic-first and FAIL-CLOSED: only healthy, available candidates that
meet the requirement are considered; the preferred provider/model is ordered
first when present. If `fallback_allowed` is False, the chain is limited to the
single preferred candidate.
"""

from __future__ import annotations

from typing import Any

from aios.model_router.contracts import (
    ModelCandidate,
    ModelRequirement,
    RoutingPolicy,
)


class FallbackResolver:
    """Resolves an ordered list of fallback candidates for a requirement."""

    def resolve(
        self,
        requirement: ModelRequirement,
        candidates: list[ModelCandidate],
    ) -> list[ModelCandidate]:
        """Return eligible candidates ordered by fallback preference.

        Fail-closed: excludes unhealthy / unavailable / under-quality candidates.
        """
        eligible: list[ModelCandidate] = []
        for c in candidates:
            if not c.is_healthy:
                continue
            if c.availability <= 0.0:
                continue
            if c.quality < requirement.minimum_quality:
                continue
            if requirement.tool_calling_required and "tool_calling" not in c.capabilities:
                continue
            if requirement.structured_output_required and "structured_output" not in c.capabilities:
                continue
            if requirement.locality and c.metadata.get("locality") != requirement.locality:
                continue
            eligible.append(c)

        # Order: preferred model/provider first, then by policy score.
        preferred = [
            c
            for c in eligible
            if (requirement.preferred_model and c.model_id == requirement.preferred_model)
            or (requirement.preferred_provider and c.provider == requirement.preferred_provider)
        ]
        rest = [c for c in eligible if c not in preferred]

        ordered = preferred + self._by_policy(rest, requirement.policy)

        if not requirement.fallback_allowed and preferred:
            return preferred
        return ordered

    @staticmethod
    def _by_policy(
        candidates: list[ModelCandidate],
        policy: RoutingPolicy,
    ) -> list[ModelCandidate]:
        def score(c: ModelCandidate) -> float:
            if policy == RoutingPolicy.COST_OPTIMIZED:
                return -c.cost_per_token
            elif policy == RoutingPolicy.LATENCY_OPTIMIZED:
                return -c.latency_ms
            elif policy == RoutingPolicy.QUALITY_OPTIMIZED:
                return c.quality
            return -(c.cost_per_token * 1000 + c.latency_ms)

        return sorted(candidates, key=score, reverse=True)
