"""Single-active lease manager — ensures only one active primary at a time."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Lease:
    resource: str
    holder: str
    granted_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 30.0)
    epoch: int = 0

    def is_valid(self, now: float | None = None) -> bool:
        now = now if now is not None else time.time()
        return now <= self.expires_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource": self.resource,
            "holder": self.holder,
            "granted_at": self.granted_at,
            "expires_at": self.expires_at,
            "epoch": self.epoch,
        }


class LeaseManager:
    """Grants and validates single-active leases (fail-closed on conflict)."""

    def __init__(self, ttl: float = 30.0) -> None:
        self._ttl = ttl
        self._leases: dict[str, Lease] = {}

    def acquire(self, resource: str, holder: str, now: float | None = None) -> Lease:
        """Acquire (or renew) the lease for `resource`. Single active holder."""
        now = now if now is not None else time.time()
        existing = self._leases.get(resource)
        if existing is not None and existing.is_valid(now) and existing.holder != holder:
            raise RuntimeError(f"Lease for {resource} held by {existing.holder}")
        if existing is not None and existing.holder == holder:
            existing.expires_at = now + self._ttl
            existing.epoch += 1
            return existing
        lease = Lease(resource=resource, holder=holder, granted_at=now,
                      expires_at=now + self._ttl, epoch=1)
        self._leases[resource] = lease
        return lease

    def validate(self, resource: str, holder: str, now: float | None = None) -> bool:
        """Fail-closed: invalid if missing, expired, or held by another."""
        now = now if now is not None else time.time()
        lease = self._leases.get(resource)
        if lease is None:
            return False
        if not lease.is_valid(now):
            return False
        return lease.holder == holder

    def release(self, resource: str, holder: str) -> None:
        lease = self._leases.get(resource)
        if lease is not None and lease.holder == holder:
            del self._leases[resource]
