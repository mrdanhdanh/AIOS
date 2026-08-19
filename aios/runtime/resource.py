"""Resource quota / grant service (TASK-005, M1).

Finite-capacity resources (e.g. ``concurrency``, ``gpu``, ``memory_mb``) are
registered with a capacity. Requests are **granted** when capacity is available,
**queued** (waiting) when the caller opts into a wait list, or **rejected**
when no capacity and no queue. Released grants return capacity and the
longest-waiting queued request is promoted when it fits.

The decision is deterministic and offline-first. A
:class:`~aios.runtime.policy.PolicyEngine` may be wired in to authorize the
holder before granting.

Layering: ``runtime`` layer — relative imports only.
"""

from __future__ import annotations

import threading
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


__all__ = ["ResourceError", "GrantStatus", "ResourceGrant", "ResourcePool"]


class ResourceError(Exception):
    """Raised on resource pool errors."""


class GrantStatus(Enum):
    GRANTED = "granted"
    QUEUED = "queued"
    REJECTED = "rejected"


@dataclass
class ResourceGrant:
    """A grant (or queued request) for a resource amount."""

    grant_id: str
    holder: str
    resource: str
    amount: int
    status: GrantStatus
    created_at: str = field(default="")


class ResourcePool:
    """Finite-capacity resource pool with grant / queue / reject semantics."""

    def __init__(self, policy=None) -> None:
        self._capacity: Dict[str, int] = {}
        self._used: Dict[str, int] = defaultdict(int)
        self._grants: Dict[str, ResourceGrant] = {}
        self._waiting: Dict[str, deque] = defaultdict(deque)
        self._policy = policy
        self._lock = threading.RLock()

    # ------------------------------------------------------------------ #
    def register(self, resource: str, capacity: int) -> None:
        if capacity < 0:
            raise ResourceError("capacity must be non-negative")
        with self._lock:
            self._capacity[resource] = capacity
            self._used[resource] = 0

    def _available(self, resource: str) -> int:
        cap = self._capacity.get(resource)
        if cap is None:
            raise ResourceError(f"unknown resource: {resource!r}")
        return cap - self._used[resource]

    def available(self, resource: str) -> int:
        with self._lock:
            return self._available(resource)

    def usage(self, resource: str) -> int:
        with self._lock:
            return self._used.get(resource, 0)

    # ------------------------------------------------------------------ #
    def request(
        self,
        holder: str,
        resource: str,
        amount: int = 1,
        *,
        queue: bool = False,
        subject: str = "runtime",
    ) -> ResourceGrant:
        """Request *amount* of *resource* for *holder*.

        Returns GRANTED when capacity allows, QUEUED when ``queue=True`` and
        capacity is full, or REJECTED otherwise.
        """
        if amount <= 0:
            raise ResourceError("amount must be positive")
        with self._lock:
            if resource not in self._capacity:
                raise ResourceError(f"unknown resource: {resource!r}")
            # Optional policy authorization.
            if self._policy is not None:
                from .policy import PolicyDecision, PolicyRequest, PermissionScope

                pres = self._policy.evaluate(
                    PolicyRequest(
                        subject=subject, action="resource.request",
                        resource=f"resource:{resource}", scope=PermissionScope.EXECUTE,
                    )
                )
                if pres.decision == PolicyDecision.DENY:
                    return ResourceGrant(
                        grant_id=f"g-{uuid.uuid4().hex[:12]}", holder=holder,
                        resource=resource, amount=amount, status=GrantStatus.REJECTED,
                    )
            if self._available(resource) >= amount:
                gid = f"g-{uuid.uuid4().hex[:12]}"
                grant = ResourceGrant(
                    grant_id=gid, holder=holder, resource=resource,
                    amount=amount, status=GrantStatus.GRANTED,
                )
                self._grants[gid] = grant
                self._used[resource] += amount
                return grant
            if queue:
                gid = f"g-{uuid.uuid4().hex[:12]}"
                grant = ResourceGrant(
                    grant_id=gid, holder=holder, resource=resource,
                    amount=amount, status=GrantStatus.QUEUED,
                )
                self._waiting[resource].append(grant)
                return grant
            return ResourceGrant(
                grant_id=f"g-{uuid.uuid4().hex[:12]}", holder=holder,
                resource=resource, amount=amount, status=GrantStatus.REJECTED,
            )

    def release(self, grant_id: str) -> None:
        """Release a grant, promoting a waiting request if capacity allows."""
        with self._lock:
            grant = self._grants.pop(grant_id, None)
            if grant is None:
                return
            if grant.status == GrantStatus.GRANTED:
                self._used[grant.resource] -= grant.amount
            # Promote waiting requests in FIFO order while capacity allows.
            queue = self._waiting.get(grant.resource)
            while queue:
                waiting = queue[0]
                if self._available(grant.resource) >= waiting.amount:
                    queue.popleft()
                    self._grants[waiting.grant_id] = waiting
                    waiting.status = GrantStatus.GRANTED
                    self._used[grant.resource] += waiting.amount
                else:
                    break

    def status(self, grant_id: str) -> Optional[GrantStatus]:
        with self._lock:
            g = self._grants.get(grant_id)
            return g.status if g else None

    def waiting_count(self, resource: str) -> int:
        with self._lock:
            return len(self._waiting.get(resource, ()))
