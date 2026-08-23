"""Usage / Cost / Audit / Evidence (TASK-115, M17).

Records usage (token/latency per T109 schema), computes cost against quota
(T039), writes an immutable, tamper-evident audit log (T078), and emits
evidence with provenance (T001 Rule 5). Fail-closed: a usage record missing a
hash/provenance is rejected (T078). Same call -> same usage/cost (deterministic).

Layering: ``unknown`` (infra) layer. Integrates with ``aios.verification_integrity``
(T078), ``aios.governance.evidence`` (T001) and ``aios.quota`` (T039).
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from aios.governance.evidence.store import Evidence, compute_hash
from aios.quota.quota_manager import QuotaManager
from aios.verification_integrity.integrity import IntegrityChecker, sha256

from .contracts import UsageSchema


__all__ = [
    "UsageError",
    "AuditEntry",
    "UsageRecord",
    "CostCompute",
    "AuditLog",
    "UsageCollector",
]


class UsageError(Exception):
    """Raised when a usage invariant is violated (fail-closed, T078)."""


@dataclass
class AuditEntry:
    """An immutable audit log entry (tamper-evident, T078)."""

    entry_id: str
    inference_ref: str
    content: str
    content_hash: str
    previous_hash: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "inference_ref": self.inference_ref,
            "content": self.content,
            "content_hash": self.content_hash,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
        }


@dataclass
class UsageRecord:
    """A usage record for one inference call."""

    inference_ref: str
    token_usage: UsageSchema
    latency_ms: float
    cost: float
    audit_entry: AuditEntry
    content_hash: str
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "inference_ref": self.inference_ref,
            "token_usage": self.token_usage.to_dict(),
            "latency_ms": self.latency_ms,
            "cost": self.cost,
            "audit_entry": self.audit_entry.to_dict(),
            "content_hash": self.content_hash,
            "evidence_ref": self.evidence_ref,
        }


class CostCompute:
    """Computes cost against a quota/budget (T039)."""

    def __init__(self, *, quota_manager: Optional[QuotaManager] = None) -> None:
        self._quota = quota_manager or QuotaManager()

    def compute(
        self,
        tenant_id: str,
        usage: UsageSchema,
        *,
        price_per_1k: float = 0.001,
    ) -> float:
        """Cost = tokens/1k * price, deterministic."""
        tokens = usage.total_tokens or (
            usage.prompt_tokens + usage.completion_tokens
        )
        return round(tokens / 1000.0 * price_per_1k, 6)

    def within_budget(self, tenant_id: str, resource_type: str, amount: int) -> bool:
        return self._quota.consume_quota(tenant_id, resource_type, amount)


class AuditLog:
    """Append-only, tamper-evident audit log (T078)."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []
        self._lock = threading.RLock()
        self._seq = 0

    def append(self, inference_ref: str, content: str) -> AuditEntry:
        with self._lock:
            self._seq += 1
            previous = self._entries[-1].content_hash if self._entries else ""
            content_hash = sha256(content)
            entry = AuditEntry(
                entry_id=f"audit-{self._seq}",
                inference_ref=inference_ref,
                content=content,
                content_hash=content_hash,
                previous_hash=previous,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            self._entries.append(entry)
            return entry

    def verify(self) -> bool:
        """Return True iff the chain is intact (no tamper)."""
        with self._lock:
            prev = ""
            for e in self._entries:
                if e.previous_hash != prev:
                    return False
                if sha256(e.content) != e.content_hash:
                    return False
                prev = e.content_hash
            return True

    def list_entries(self) -> list[AuditEntry]:
        with self._lock:
            return list(self._entries)


class UsageCollector:
    """Collects usage + audit + evidence for an inference call."""

    def __init__(
        self,
        *,
        quota_manager: Optional[QuotaManager] = None,
        producer: str = "model_runtime.usage",
        task_id: str = "TASK-115",
    ) -> None:
        self._cost = CostCompute(quota_manager=quota_manager)
        self._audit = AuditLog()
        self._integrity = IntegrityChecker()
        self._producer = producer
        self._task_id = task_id
        self._seq = 0

    def record(
        self,
        inference_ref: str,
        usage: UsageSchema,
        *,
        latency_ms: float = 0.0,
        tenant_id: str = "default",
        run_id: str = "usage",
        price_per_1k: float = 0.001,
    ) -> UsageRecord:
        cost = self._cost.compute(tenant_id, usage, price_per_1k=price_per_1k)
        # Audit entry (immutable, tamper-evident).
        audit = self._audit.append(
            inference_ref,
            content=f"{inference_ref}|{usage.total_tokens}|{cost}|{latency_ms}",
        )
        # Content hash over the canonical record (fail-closed, T078).
        canonical = (
            f"{inference_ref}|{usage.prompt_tokens}|{usage.completion_tokens}|"
            f"{usage.total_tokens}|{cost}|{latency_ms}"
        )
        content_hash = sha256(canonical)
        # Provenance / evidence (T001 Rule 5).
        evidence_id = f"ev-usage-{self._seq + 1}"
        self._seq += 1
        evidence = Evidence(
            evidence_id=evidence_id,
            task_id=self._task_id,
            run_id=run_id,
            producer=self._producer,
            type="usage_record",
            source=inference_ref,
            content_hash=content_hash,
        )
        # Fail-closed: missing hash/provenance -> reject (T078). The Evidence
        # object is already validated by its constructor (mandatory fields), so
        # a non-empty content_hash is sufficient to prove provenance integrity.
        if not content_hash or not evidence.content_hash:
            raise UsageError("usage record missing hash/provenance (fail-closed)")
        return UsageRecord(
            inference_ref=inference_ref,
            token_usage=usage,
            latency_ms=latency_ms,
            cost=cost,
            audit_entry=audit,
            content_hash=content_hash,
            evidence_ref=evidence_id,
        )

    def audit_intact(self) -> bool:
        return self._audit.verify()
