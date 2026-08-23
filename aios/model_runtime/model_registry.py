"""Model Registry + Deterministic Resolver (TASK-111, M17).

Registers models through the T109 contract and resolves the best model by
policy/capability/cost/health using a **rule engine (no LLM)**. Resolution is
deterministic: same request + same registry/policy -> same ``selected_model``.
``model_id`` is immutable (T001 Rule 1). Every resolve carries provenance
(T001 Rule 5).

Layering: ``unknown`` (infra) layer.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from .contracts import ModelContract, validate_contract
from .provider_registry import HealthStatus, ProviderRegistry, ProviderStatus


__all__ = [
    "ModelRegistryError",
    "ResolveStatus",
    "ModelResolver",
    "ModelRegistry",
]


class ModelRegistryError(Exception):
    """Raised on model registry usage errors (fail-closed)."""


class ResolveStatus(str, Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"


@dataclass
class ModelResolver:
    """A deterministic resolution request + result (no LLM)."""

    model_id: str  # immutable request id (T001 Rule 1)
    capability_req: list[str] = field(default_factory=list)
    policy_ref: str = ""
    cost_budget: float = float("inf")
    health_filter: bool = True
    selected_model: Optional[str] = None
    resolver_deterministic: bool = True
    llm_call_count: int = 0  # always 0 — deterministic-first (T001 Rule 4)
    provenance: list[str] = field(default_factory=list)
    status: ResolveStatus = ResolveStatus.UNRESOLVED

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "capability_req": list(self.capability_req),
            "policy_ref": self.policy_ref,
            "cost_budget": self.cost_budget,
            "health_filter": self.health_filter,
            "selected_model": self.selected_model,
            "resolver_deterministic": self.resolver_deterministic,
            "llm_call_count": self.llm_call_count,
            "provenance": list(self.provenance),
            "status": self.status.value,
        }


class ModelRegistry:
    """Registry of models + deterministic resolver."""

    def __init__(
        self,
        *,
        provider_registry: Optional[ProviderRegistry] = None,
        producer: str = "model_runtime.model_registry",
    ) -> None:
        self._models: dict[str, ModelContract] = {}
        self._lock = threading.RLock()
        self._providers = provider_registry
        self._producer = producer
        self._seq = 0

    # -- registration (immutable id, T001 Rule 1) -------------------------- #
    def register(self, contract: ModelContract) -> ModelContract:
        validate_contract(contract)
        with self._lock:
            if contract.model_id in self._models:
                raise ModelRegistryError(
                    f"model_id already registered: {contract.model_id!r} (immutable, T001)"
                )
            self._models[contract.model_id] = contract
            return contract

    def get(self, model_id: str) -> ModelContract:
        with self._lock:
            c = self._models.get(model_id)
            if c is None:
                raise ModelRegistryError(f"unknown model: {model_id!r}")
            return c

    def list_models(self) -> list[ModelContract]:
        with self._lock:
            return list(self._models.values())

    # -- deterministic resolver (rule engine, no LLM) --------------------- #
    def resolve(
        self,
        request_id: str,
        *,
        capability_req: Optional[list[str]] = None,
        policy_ref: str = "",
        cost_budget: float = float("inf"),
        health_filter: bool = True,
        run_id: str = "resolve",
    ) -> ModelResolver:
        """Resolve the best model by rule. Deterministic, LLM-call-count == 0."""
        capability_req = capability_req or []
        with self._lock:
            candidates = [
                c
                for c in self._models.values()
                if all(cap in c.capabilities for cap in capability_req)
                and (not policy_ref or c.policy_ref == policy_ref)
            ]
            if self._providers is not None and health_filter:
                healthy_providers = {
                    r.provider_id
                    for r in self._providers.list_providers()
                    if r.status == ProviderStatus.ENABLED
                    and r.health == HealthStatus.HEALTHY
                }
                candidates = [
                    c for c in candidates if c.provider_ref in healthy_providers
                ]
            # Cost filter (deterministic): keep models within budget.
            candidates = [c for c in candidates if self._est_cost(c) <= cost_budget]
            if not candidates:
                result = ModelResolver(
                    model_id=request_id,
                    capability_req=capability_req,
                    policy_ref=policy_ref,
                    cost_budget=cost_budget,
                    health_filter=health_filter,
                    status=ResolveStatus.UNRESOLVED,
                )
                result.provenance.append(
                    f"{self._producer}:no-eligible-model:{datetime.now(timezone.utc).isoformat()}"
                )
                return result
            # Deterministic ranking: lower cost, then model_id tie-break.
            candidates.sort(key=lambda c: (round(self._est_cost(c), 6), c.model_id))
            chosen = candidates[0]
            result = ModelResolver(
                model_id=request_id,
                capability_req=capability_req,
                policy_ref=policy_ref,
                cost_budget=cost_budget,
                health_filter=health_filter,
                selected_model=chosen.model_id,
                status=ResolveStatus.RESOLVED,
            )
            result.provenance.append(
                f"{self._producer}:resolved:{chosen.model_id}:{run_id}"
            )
            return result

    @staticmethod
    def _est_cost(contract: ModelContract) -> float:
        # Cost proxy derived from the contract's declared capabilities count is
        # intentionally stable; real cost is computed in T115. Here we use a
        # deterministic proxy so resolution stays reproducible.
        return float(len(contract.capabilities))
