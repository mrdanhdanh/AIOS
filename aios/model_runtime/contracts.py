"""Model Contracts (TASK-109, M17).

Standard, vendor-neutral model contract: request/response schemas, capability
declaration, usage schema, and a policy boundary. A model is usable in AIOS
only if it implements :class:`ModelContract`. The contract carries **no** vendor
logic — adapters (T110) implement it. Every call carries provenance (T001 Rule 5)
and validation is deterministic (same contract + same input -> same result).

Layering: ``model_runtime`` is an ``unknown`` (infra) layer — it may import
stdlib and other AIOS packages but never agent/orchestrator internals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


__all__ = [
    "ModelContractError",
    "ModelCapability",
    "UsageSchema",
    "CapabilityDeclaration",
    "ModelRequest",
    "ModelResponse",
    "ModelContract",
    "PolicyBoundary",
    "validate_contract",
]


class ModelContractError(Exception):
    """Raised when a model contract is invalid (fail-closed, T078)."""


class ModelCapability(str, Enum):
    """What a model can do (declared by the contract, not hard-coded vendor)."""

    CHAT = "chat"
    EMBED = "embed"
    VISION = "vision"
    CODE = "code"
    FUNCTION_CALLING = "function_calling"
    STRUCTURED_OUTPUT = "structured_output"
    REASONING = "reasoning"


@dataclass
class UsageSchema:
    """Normalized usage (token/cost/latency) — consumed by T115."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost": self.cost,
            "latency_ms": self.latency_ms,
        }


@dataclass
class CapabilityDeclaration:
    """A single declared capability of a model."""

    capability: str
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "enabled": self.enabled,
            "metadata": dict(self.metadata),
        }


@dataclass
class ModelRequest:
    """Standard request schema for every model."""

    prompt: str = ""
    capabilities: list[str] = field(default_factory=list)
    max_tokens: int = 0
    temperature: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "capabilities": list(self.capabilities),
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "metadata": dict(self.metadata),
        }


@dataclass
class ModelResponse:
    """Standard response schema for every model."""

    content: str = ""
    model_id: str = ""
    usage: UsageSchema = field(default_factory=UsageSchema)
    finish_reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "model_id": self.model_id,
            "usage": self.usage.to_dict(),
            "finish_reason": self.finish_reason,
            "metadata": dict(self.metadata),
        }


@dataclass
class ModelContract:
    """Vendor-neutral model contract.

    A model is usable in AIOS only if it implements this contract. The contract
    carries no vendor logic; adapters (T110) implement it.
    """

    model_id: str
    provider_ref: str
    capabilities: list[str] = field(default_factory=list)
    request_schema: str = "ModelRequest"
    response_schema: str = "ModelResponse"
    usage_schema: str = "UsageSchema"
    policy_ref: str = ""

    # -- validation (fail-closed, deterministic) --------------------------- #
    def validate_request(self, request: ModelRequest) -> None:
        """Validate a request against the contract. Raise on violation."""
        if not isinstance(request, ModelRequest):
            raise ModelContractError("request must be a ModelRequest")
        missing = [c for c in request.capabilities if c not in self.capabilities]
        if missing:
            raise ModelContractError(
                f"request requires capabilities not declared by contract: {missing}"
            )

    def validate_response(self, response: ModelResponse) -> None:
        """Validate a response against the contract. Raise on violation."""
        if not isinstance(response, ModelResponse):
            raise ModelContractError("response must be a ModelResponse")
        if response.model_id and response.model_id != self.model_id:
            raise ModelContractError(
                f"response model_id {response.model_id!r} != contract {self.model_id!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "provider_ref": self.provider_ref,
            "capabilities": list(self.capabilities),
            "request_schema": self.request_schema,
            "response_schema": self.response_schema,
            "usage_schema": self.usage_schema,
            "policy_ref": self.policy_ref,
        }


@dataclass
class PolicyBoundary:
    """Declares the policy a contract must respect (T113).

    A contract with an empty ``policy_ref`` is *open*; the security integration
    (T113) blocks any inference that bypasses the required policy.
    """

    policy_ref: str = ""

    def requires_policy(self) -> bool:
        return bool(self.policy_ref)

    def is_respected(self, applied_policy_ref: str) -> bool:
        """True iff the applied policy matches the required boundary."""
        if not self.policy_ref:
            return True
        return applied_policy_ref == self.policy_ref


def validate_contract(contract: ModelContract) -> None:
    """Fail-closed validation of a model contract (T078).

    Raises :class:`ModelContractError` when the contract is invalid. Deterministic:
    same contract -> same outcome.
    """
    if not isinstance(contract, ModelContract):
        raise ModelContractError("contract must be a ModelContract")
    if not contract.model_id:
        raise ModelContractError("model_id is required")
    if not contract.provider_ref:
        raise ModelContractError("provider_ref is required")
    if not contract.capabilities:
        raise ModelContractError("contract must declare at least one capability")
    for cap in contract.capabilities:
        if not isinstance(cap, str) or not cap:
            raise ModelContractError(f"invalid capability declaration: {cap!r}")
