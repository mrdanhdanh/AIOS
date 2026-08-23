"""Provider Registry + Lifecycle (TASK-110, M17).

Registers providers through the model contract (T109) and manages their
lifecycle (register/enable/disable/deprecate) without vendor lock-in.
``provider_id`` is immutable (T001 Rule 1). Unhealthy providers are never
selected (T025). Every lifecycle event carries provenance (T001 Rule 5).

Layering: ``unknown`` (infra) layer.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from .contracts import ModelContract, validate_contract


__all__ = [
    "ProviderRegistryError",
    "ProviderStatus",
    "HealthStatus",
    "ProviderRecord",
    "LifecycleEvent",
    "ProviderRegistry",
]


class ProviderRegistryError(Exception):
    """Raised on provider registry usage errors (fail-closed)."""


class ProviderStatus(str, Enum):
    REGISTERED = "registered"
    ENABLED = "enabled"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


@dataclass
class LifecycleEvent:
    """A single lifecycle transition with provenance (T001 Rule 5)."""

    event_id: str
    provider_id: str
    from_status: str
    to_status: str
    producer: str
    run_id: str
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "provider_id": self.provider_id,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "producer": self.producer,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
        }


@dataclass
class ProviderRecord:
    """A registered provider bound to a model contract (T109)."""

    provider_id: str
    model_contract_ref: str
    status: ProviderStatus = ProviderStatus.REGISTERED
    health: HealthStatus = HealthStatus.HEALTHY
    lifecycle_event_log: list[LifecycleEvent] = field(default_factory=list)
    policy_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "model_contract_ref": self.model_contract_ref,
            "status": self.status.value,
            "health": self.health.value,
            "lifecycle_event_log": [e.to_dict() for e in self.lifecycle_event_log],
            "policy_ref": self.policy_ref,
        }


class ProviderRegistry:
    """Registry of providers with immutable ids and lifecycle management."""

    def __init__(self, *, producer: str = "model_runtime.provider_registry") -> None:
        self._providers: dict[str, ProviderRecord] = {}
        self._lock = threading.RLock()
        self._producer = producer
        self._event_seq = 0

    # -- registration (immutable id, T001 Rule 1) -------------------------- #
    def register(
        self,
        provider_id: str,
        model_contract: ModelContract,
        *,
        policy_ref: str = "",
        run_id: str = "init",
    ) -> ProviderRecord:
        """Register a provider. Rejects duplicate ids (T001 Rule 1)."""
        validate_contract(model_contract)
        with self._lock:
            if provider_id in self._providers:
                raise ProviderRegistryError(
                    f"provider_id already registered: {provider_id!r} (immutable, T001)"
                )
            record = ProviderRecord(
                provider_id=provider_id,
                model_contract_ref=model_contract.model_id,
                status=ProviderStatus.REGISTERED,
                health=HealthStatus.HEALTHY,
                policy_ref=policy_ref or model_contract.policy_ref,
            )
            self._emit(record, ProviderStatus.REGISTERED, run_id)
            self._providers[provider_id] = record
            return record

    def _emit(self, record: ProviderRecord, to_status: ProviderStatus, run_id: str) -> None:
        self._event_seq += 1
        event = LifecycleEvent(
            event_id=f"evt-{self._event_seq}",
            provider_id=record.provider_id,
            from_status=record.status.value,
            to_status=to_status.value,
            producer=self._producer,
            run_id=run_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        record.lifecycle_event_log.append(event)
        record.status = to_status

    # -- lifecycle -------------------------------------------------------- #
    def enable(self, provider_id: str, *, run_id: str = "lifecycle") -> ProviderRecord:
        return self._transition(provider_id, ProviderStatus.ENABLED, run_id)

    def disable(self, provider_id: str, *, run_id: str = "lifecycle") -> ProviderRecord:
        return self._transition(provider_id, ProviderStatus.DISABLED, run_id)

    def deprecate(self, provider_id: str, *, run_id: str = "lifecycle") -> ProviderRecord:
        # Soft-delete: deprecated, id never reused (T001 Rule 1).
        return self._transition(provider_id, ProviderStatus.DEPRECATED, run_id)

    def _transition(self, provider_id: str, to: ProviderStatus, run_id: str) -> ProviderRecord:
        with self._lock:
            record = self._get(provider_id)
            if record.status == ProviderStatus.DEPRECATED:
                raise ProviderRegistryError(
                    f"provider {provider_id!r} is deprecated; id is immutable (T001)"
                )
            self._emit(record, to, run_id)
            return record

    # -- health (T025) ---------------------------------------------------- #
    def set_health(self, provider_id: str, healthy: bool) -> ProviderRecord:
        with self._lock:
            record = self._get(provider_id)
            record.health = HealthStatus.HEALTHY if healthy else HealthStatus.UNHEALTHY
            return record

    def is_healthy(self, provider_id: str) -> bool:
        with self._lock:
            return self._get(provider_id).health == HealthStatus.HEALTHY

    # -- selection (fail-closed, deterministic) ---------------------------- #
    def select(self, *, policy_ref: str = "") -> Optional[ProviderRecord]:
        """Select an enabled + healthy provider.

        Deterministic: same registry state -> same selection. Unhealthy or
        disabled providers are never selected (T025). Fail-closed: returns
        ``None`` when nothing is eligible.
        """
        with self._lock:
            eligible = [
                r
                for r in self._providers.values()
                if r.status == ProviderStatus.ENABLED
                and r.health == HealthStatus.HEALTHY
                and (not policy_ref or r.policy_ref == policy_ref)
            ]
            if not eligible:
                return None
            eligible.sort(key=lambda r: r.provider_id)
            return eligible[0]

    # -- queries ---------------------------------------------------------- #
    def get(self, provider_id: str) -> ProviderRecord:
        with self._lock:
            return self._get(provider_id)

    def list_providers(self) -> list[ProviderRecord]:
        with self._lock:
            return [r for r in self._providers.values()]

    def _get(self, provider_id: str) -> ProviderRecord:
        record = self._providers.get(provider_id)
        if record is None:
            raise ProviderRegistryError(f"unknown provider: {provider_id!r}")
        return record
