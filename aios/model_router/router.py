"""Model Router — deterministic-first model selection.

AC-025-01: Model selected by policy+capability+cost+health.
AC-025-02: Deterministic routing.
AC-025-03: No LLM needed for normal routing.
AC-025-10: No eligible model → fail-closed.
AC-025-11: Selection has explanation and provenance.
"""

from __future__ import annotations

from typing import Any

from aios.autonomous_recovery import (
    FailureClassifier,
    RecoveryController,
    RecoveryStrategy,
)
from aios.model_router.contracts import (
    ModelCandidate,
    ModelHealth,
    ModelRequirement,
    ModelRoute,
    ModelSelection,
    RoutingPolicy,
)
from aios.model_router.fallback import FallbackResolver
from aios.model_router.health import ModelHealthTracker


class ModelRouter:
    """Selects model by policy, capability, cost, and health.

    Deterministic-first — no LLM involvement for normal routing.
    """

    def __init__(self, health_tracker: ModelHealthTracker | None = None) -> None:
        self._candidates: list[ModelCandidate] = []
        self._health = health_tracker or ModelHealthTracker()
        self._fallback = FallbackResolver()
        self._selection_history: list[ModelSelection] = []

    def register_candidate(self, candidate: ModelCandidate) -> None:
        """Register a model candidate."""
        self._candidates.append(candidate)

    def _eligible_chain(
        self, requirement: ModelRequirement
    ) -> tuple[list[str], list[ModelCandidate], list[ModelCandidate]]:
        """Return (rejected, eligible, fallback-ordered chain) for a requirement.

        Single source of truth for eligibility used by both :meth:`select` and
        :meth:`route`. Deterministic and fail-closed.
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

        chain = self._fallback.resolve(requirement, eligible)
        return rejected, eligible, chain

    def select(self, requirement: ModelRequirement) -> ModelSelection:
        """Select the best model for the given requirement.

        AC-025-01: Policy + capability + cost + health.
        AC-025-10: Fail-closed if no eligible model.
        """
        rejected, eligible, chain = self._eligible_chain(requirement)

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

        if not chain:
            selection = ModelSelection(
                model=None,
                selected=False,
                explanation="No eligible model after fallback resolution (fail-closed)",
                alternatives_rejected=rejected,
                provenance=["model_router:fail_closed"],
            )
            self._selection_history.append(selection)
            return selection

        best = chain[0]
        selection = ModelSelection(
            model=best,
            selected=True,
            explanation=f"Selected {best.model_id} ({best.provider}) by {requirement.policy.value}",
            alternatives_rejected=rejected,
            provenance=[f"model_router:{requirement.policy.value}"],
        )
        self._selection_history.append(selection)
        return selection

    def route(
        self,
        intent: str,
        policy: RoutingPolicy = RoutingPolicy.BALANCED,
        *,
        cost_estimate: float | None = None,
        latency_budget: float | None = None,
        evidence_ref: str = "",
        **requirement_kwargs: object,
    ) -> ModelRoute:
        """Build a policy-driven :class:`ModelRoute` for an intent (TASK-075).

        Selection is policy-driven (no hardcoded provider). The returned route
        carries the fallback provider chain, a cost estimate, a latency budget,
        and an ``evidence_ref`` for provenance.
        """
        requirement = ModelRequirement(task_type=intent, policy=policy, **requirement_kwargs)
        _rejected, _eligible, chain = self._eligible_chain(requirement)

        if not chain:
            return ModelRoute(
                intent=intent,
                selected_provider="",
                fallback_providers=[],
                cost_estimate=0.0,
                latency_budget=0.0,
                evidence_ref=evidence_ref or "model_router:fail_closed",
                policy=policy,
                selected_model=None,
                provenance=["model_router:fail_closed"],
            )

        selected = chain[0]
        fallback_providers = [c.provider for c in chain[1:]]
        return ModelRoute(
            intent=intent,
            selected_provider=selected.provider,
            fallback_providers=fallback_providers,
            cost_estimate=cost_estimate if cost_estimate is not None else selected.cost_per_token,
            latency_budget=latency_budget if latency_budget is not None else selected.latency_ms,
            evidence_ref=evidence_ref or f"model_router:{policy.value}",
            policy=policy,
            selected_model=selected.model_id,
            provenance=[f"model_router:{policy.value}"],
        )

    def attempt_fallback(
        self,
        route: ModelRoute,
        failed_provider: str,
        failure_reason: str = "provider unavailable",
    ) -> ModelRoute | None:
        """Route to the next fallback provider when one fails (T055).

        Uses the autonomous-recovery controller to decide the strategy. A
        provider/dependency failure maps to ``FALLBACK`` and yields the next
        provider in the chain. Any other strategy (e.g. ``SAFE_STOP`` for an
        unknown failure) returns ``None`` — fail-closed.
        """
        classifier = FailureClassifier()
        controller = RecoveryController()
        failure_class = classifier.classify(failure_reason)
        strategy = controller.decide_strategy(failure_class, 0)
        if strategy is not RecoveryStrategy.FALLBACK:
            return None

        ordered = [route.selected_provider] + list(route.fallback_providers)
        remaining = [p for p in ordered if p != failed_provider]
        if not remaining:
            return None

        return ModelRoute(
            intent=route.intent,
            selected_provider=remaining[0],
            fallback_providers=remaining[1:],
            cost_estimate=route.cost_estimate,
            latency_budget=route.latency_budget,
            evidence_ref=route.evidence_ref,
            policy=route.policy,
            selected_model=None,
            provenance=list(route.provenance) + [f"model_router:fallback_from:{failed_provider}"],
        )

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
