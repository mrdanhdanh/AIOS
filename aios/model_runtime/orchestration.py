"""Inference Runtime Orchestration (TASK-112, M17).

Orchestrates inference through a provider (T110) + model (T111) deterministically
— builds an execution plan, selects the model via the deterministic resolver,
and dispatches only to registered + enabled providers. Every inference carries
provenance (T001 Rule 5) and is policy-gated (T113). The orchestrator is **not**
a control-plane LLM: planning is rule-based (T001 Rule 4).

Layering: ``unknown`` (infra) layer.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

from .contracts import ModelContract, ModelRequest, ModelResponse, validate_contract
from .model_registry import ModelRegistry, ResolveStatus
from .provider_registry import (
    HealthStatus,
    ProviderRegistry,
    ProviderStatus,
    ProviderRegistryError,
)


__all__ = [
    "OrchestrationError",
    "ExecutionStatus",
    "InferencePlan",
    "InferenceOrchestrator",
]


class OrchestrationError(Exception):
    """Raised when orchestration cannot proceed (fail-closed, T078)."""


class ExecutionStatus(str, Enum):
    PLANNED = "planned"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    REJECTED = "rejected"


@dataclass
class InferencePlan:
    """A deterministic inference execution plan."""

    plan_id: str
    provider_ref: str
    model_ref: str
    request: ModelRequest
    policy_ref: str = ""
    execution_status: ExecutionStatus = ExecutionStatus.PLANNED
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "provider_ref": self.provider_ref,
            "model_ref": self.model_ref,
            "request": self.request.to_dict(),
            "policy_ref": self.policy_ref,
            "execution_status": self.execution_status.value,
            "evidence_ref": self.evidence_ref,
        }


# A backend performs the actual provider call. Signature: (provider_id, request) -> ModelResponse
DispatchFn = Callable[[str, ModelRequest], ModelResponse]


class InferenceOrchestrator:
    """Plans + dispatches inference through registered providers."""

    def __init__(
        self,
        *,
        provider_registry: Optional[ProviderRegistry] = None,
        model_registry: Optional[ModelRegistry] = None,
        dispatch_fn: Optional[DispatchFn] = None,
        producer: str = "model_runtime.orchestration",
    ) -> None:
        self._providers = provider_registry or ProviderRegistry()
        self._models = model_registry or ModelRegistry()
        self._dispatch = dispatch_fn
        self._producer = producer
        self._lock = threading.RLock()
        self._seq = 0

    # -- planning (deterministic, rule-based) ------------------------------ #
    def plan(
        self,
        request: ModelRequest,
        *,
        plan_id: Optional[str] = None,
        policy_ref: str = "",
        run_id: str = "plan",
    ) -> InferencePlan:
        with self._lock:
            self._seq += 1
            pid = plan_id or f"plan-{self._seq}"
        # Select model deterministically (T111).
        resolver = self._models.resolve(
            pid,
            capability_req=list(request.capabilities),
            policy_ref=policy_ref,
            run_id=run_id,
        )
        if resolver.status != ResolveStatus.RESOLVED or not resolver.selected_model:
            raise OrchestrationError("no model resolved for request (fail-closed)")
        contract = self._models.get(resolver.selected_model)
        # Provider must be registered + enabled (T110).
        provider_id = contract.provider_ref
        try:
            provider = self._providers.get(provider_id)
        except ProviderRegistryError:
            raise OrchestrationError(f"provider not registered: {provider_id!r}")
        if provider.status != ProviderStatus.ENABLED:
            raise OrchestrationError(f"provider not enabled: {provider_id!r} (T110)")
        if provider.health != HealthStatus.HEALTHY:
            raise OrchestrationError(f"provider unhealthy: {provider_id!r} (T025)")
        # Policy boundary: contract must respect the requested policy (T113).
        if policy_ref and contract.policy_ref and contract.policy_ref != policy_ref:
            raise OrchestrationError(
                f"contract policy_ref {contract.policy_ref!r} != required {policy_ref!r}"
            )
        validate_contract(contract)
        contract.validate_request(request)
        return InferencePlan(
            plan_id=pid,
            provider_ref=provider_id,
            model_ref=contract.model_id,
            request=request,
            policy_ref=policy_ref,
            execution_status=ExecutionStatus.PLANNED,
        )

    # -- dispatch (fail-closed) ------------------------------------------- #
    def dispatch(self, plan: InferencePlan, *, run_id: str = "dispatch") -> ModelResponse:
        if plan.execution_status == ExecutionStatus.REJECTED:
            raise OrchestrationError("plan was rejected; cannot dispatch")
        provider = self._providers.get(plan.provider_ref)
        if provider.status != ProviderStatus.ENABLED:
            raise OrchestrationError(f"provider disabled at dispatch: {plan.provider_ref!r}")
        if self._dispatch is None:
            raise OrchestrationError("no dispatch backend configured")
        response = self._dispatch(plan.provider_ref, plan.request)
        if not isinstance(response, ModelResponse):
            raise OrchestrationError("dispatch backend returned non-ModelResponse")
        contract = self._models.get(plan.model_ref)
        contract.validate_response(response)
        plan.execution_status = ExecutionStatus.COMPLETED
        plan.evidence_ref = f"evt-inference-{plan.plan_id}:{run_id}:{datetime.now(timezone.utc).isoformat()}"
        return response
