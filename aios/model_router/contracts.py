"""Model router contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RoutingPolicy(str, Enum):
    COST_OPTIMIZED = "cost_optimized"
    LATENCY_OPTIMIZED = "latency_optimized"
    QUALITY_OPTIMIZED = "quality_optimized"
    BALANCED = "balanced"


@dataclass
class ModelRequirement:
    """Requirements for model selection."""

    task_type: str = ""
    min_context_window: int = 0
    max_cost_per_token: float = float("inf")
    max_latency_ms: float = float("inf")
    required_capabilities: list[str] = field(default_factory=list)
    policy: RoutingPolicy = RoutingPolicy.BALANCED
    prefer_offline: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_type": self.task_type,
            "min_context_window": self.min_context_window,
            "max_cost_per_token": self.max_cost_per_token,
            "policy": self.policy.value,
            "prefer_offline": self.prefer_offline,
        }


@dataclass
class ModelCandidate:
    """A candidate model for routing."""

    model_id: str
    provider: str
    context_window: int = 4096
    cost_per_token: float = 0.0
    latency_ms: float = 100.0
    capabilities: list[str] = field(default_factory=list)
    is_healthy: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "provider": self.provider,
            "context_window": self.context_window,
            "cost_per_token": self.cost_per_token,
            "latency_ms": self.latency_ms,
            "is_healthy": self.is_healthy,
        }


@dataclass
class ModelSelection:
    """Selected model with explanation."""

    model: ModelCandidate | None = None
    selected: bool = False
    explanation: str = ""
    alternatives_rejected: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model.to_dict() if self.model else None,
            "selected": self.selected,
            "explanation": self.explanation,
            "alternatives_rejected": self.alternatives_rejected,
            "provenance": self.provenance,
        }


@dataclass
class ModelHealth:
    """Health status for a model."""

    model_id: str
    healthy: bool = True
    failure_count: int = 0
    last_failure_time: float = 0.0
    avg_latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "healthy": self.healthy,
            "failure_count": self.failure_count,
        }
