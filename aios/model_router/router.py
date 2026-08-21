"""Model Router — deterministic-first model selection.

AC-025-01: Model selected by policy+capability+cost+health.
AC-025-02: Deterministic routing.
AC-025-03: No LLM needed for normal routing.
AC-025-10: No eligible model → fail-closed.
AC-025-11: Selection has explanation and provenance.
"""

from __future__ import annotations

from typing import Any

from aios.model_router.contracts import (
    ModelCandidate,
    ModelHealth,
    ModelRequirement,
    ModelSelection,
    RoutingPolicy,
)
from aios.model_router.health import ModelHealthTracker


class ModelRouter:
    """Selects model by policy, capability, cost, and health.

    Deterministic-first — no LLM involvement for normal routing.
    """

    def __init__(self, health_tracker: ModelHealthTracker | None = None) -> None:
        self._candidates: list[ModelCandidate] = []
        self._health = health_tracker or ModelHealthTracker()
        self._selection_history: list[ModelSelection] = []

    def register_candidate(self, candidate: ModelCandidate) -> None:
        """Register a model candidate."""
        self._candidates.append(candidate)

    def select(self, requirement: ModelRequirement) -> ModelSelection:
        """Select the best model for the given requirement.

        AC-025-01: Policy + capability + cost + health.
        AC-025-10: Fail-closed if no eligible model.
        """
        rejected: list[str] = []
        eligible: list[ModelCandidate] = []

        for c in self._candidates:
            # Health check
            if not self._health.is_healthy(c.model_id):
                rejected.append(f"{c.model_id}: unhealthy")
                continue

            # Capability check
            if requirement.required_capabilities:
                missing = [cap for cap in requirement.required_capabilities if cap not in c.capabilities]
                if missing:
                    rejected.append(f"{c.model_id}: missing capabilities {missing}")
                    continue

            # Context window check
            if c.context_window < requirement.min_context_window:
                rejected.append(f"{c.model_id}: context_window {c.context_window} < {requirement.min_context_window}")
                continue

            # Cost check
            if c.cost_per_token > requirement.max_cost_per_token:
                rejected.append(f"{c.model_id}: cost {c.cost_per_token} > {requirement.max_cost_per_token}")
                continue

            # Latency check
            if c.latency_ms > requirement.max_latency_ms:
                rejected.append(f"{c.model_id}: latency {c.latency_ms}ms > {requirement.max_latency_ms}ms")
                continue

            eligible.append(c)

        if not eligible:
            selection = ModelSelection(
                model=None,
                selected=False,
                explanation="No eligible model found (fail-closed)",
                alternatives_rejected=rejected,
                provenance=["model_router:fail_closed"],
            )
            self._selection_history.append(selection)
            return selection

        # Score eligible candidates by policy
        scored = self._score_by_policy(eligible, requirement.policy)
        best = scored[0]

        selection = ModelSelection(
            model=best,
            selected=True,
            explanation=f"Selected {best.model_id} ({best.provider}) by {requirement.policy.value}",
            alternatives_rejected=rejected,
            provenance=[f"model_router:{requirement.policy.value}"],
        )
        self._selection_history.append(selection)
        return selection

    def _score_by_policy(
        self,
        candidates: list[ModelCandidate],
        policy: RoutingPolicy,
    ) -> list[ModelCandidate]:
        """Score and sort candidates by routing policy."""

        def score(c: ModelCandidate) -> float:
            if policy == RoutingPolicy.COST_OPTIMIZED:
                return -c.cost_per_token  # Lower cost = higher score
            elif policy == RoutingPolicy.LATENCY_OPTIMIZED:
                return -c.latency_ms  # Lower latency = higher score
            elif policy == RoutingPolicy.QUALITY_OPTIMIZED:
                return c.context_window  # Larger window = higher quality proxy
            else:  # BALANCED
                return -(c.cost_per_token * 1000 + c.latency_ms)

        return sorted(candidates, key=score, reverse=True)

    def get_history(self) -> list[ModelSelection]:
        return list(self._selection_history)

    def list_candidates(self) -> list[ModelCandidate]:
        return list(self._candidates)
