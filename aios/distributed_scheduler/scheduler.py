"""DistributedScheduler."""
from __future__ import annotations
from aios.distributed_scheduler.contracts import Lease, LeaseState

class DistributedScheduler:
    def __init__(self) -> None:
        self._leases: dict[str, Lease] = {}
    def acquire_lease(self, node_id: str, resource_id: str, ttl: int = 300) -> Lease:
        # Check if resource already held
        for l in self._leases.values():
            if l.resource_id == resource_id and l.state == LeaseState.HELD:
                raise RuntimeError(f"Resource {resource_id} already held")
        lease = Lease(node_id=node_id, resource_id=resource_id, ttl_seconds=ttl)
        self._leases[lease.lease_id] = lease
        return lease
    def release_lease(self, lease_id: str) -> Lease:
        if lease_id not in self._leases: raise RuntimeError(f"Lease {lease_id!r} not found")
        l = self._leases[lease_id]; l.state = LeaseState.RELEASED; return l
    def check_expired(self) -> list[Lease]:
        expired = [l for l in self._leases.values() if l.state == LeaseState.HELD]
        for l in expired: l.state = LeaseState.EXPIRED
        return expired
    def list_leases(self) -> list[Lease]: return list(self._leases.values())
