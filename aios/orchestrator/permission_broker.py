"""Permission Broker — orchestration-level permission aggregation (TASK-012).

Collects, normalizes, deduplicates permissions from workflow/task, checks
scope, delegates to runtime PermissionBroker/PolicyEngine, returns
ALLOW/DENY/ASK. Does NOT decide policy itself — authority stays with
runtime Policy/Permission layer. DENY → BLOCKED, ASK → human approval.

Layering: orchestrator — may import runtime.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from aios.runtime.permission import Permission, PermissionBroker, PermissionScope
from aios.runtime.policy import PolicyDecision, PolicyEngine, PolicyRequest

__all__ = [
    "OrchestratorPermissionDecision",
    "PermissionRequestRecord",
    "OrchestratorPermissionBroker",
    "OrchestratorPermissionBrokerError",
]


class OrchestratorPermissionBrokerError(Exception):
    pass


class OrchestratorPermissionDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ASK = "ASK"


@dataclass
class PermissionRequestRecord:
    request_id: str
    subject: str
    permissions: List[str]
    resource: str
    decision: OrchestratorPermissionDecision
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None
    resolved_decision: Optional[OrchestratorPermissionDecision] = None
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "subject": self.subject,
            "permissions": list(self.permissions),
            "resource": self.resource,
            "decision": self.decision.value,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
            "resolved_decision": self.resolved_decision.value if self.resolved_decision else None,
            "evidence": dict(self.evidence),
        }


def _infer_scope(perm: str) -> PermissionScope:
    perm_l = perm.lower()
    if "read" in perm_l:
        return PermissionScope.READ
    if "write" in perm_l:
        return PermissionScope.WRITE
    if "delete" in perm_l:
        return PermissionScope.DELETE
    if "execute" in perm_l or "shell" in perm_l or "process" in perm_l:
        return PermissionScope.EXECUTE
    if "capability" in perm_l:
        return PermissionScope.CAPABILITY_INVOKE
    if "tool" in perm_l:
        return PermissionScope.TOOL_INVOKE
    if "memory" in perm_l:
        return PermissionScope.MEMORY_READ if "read" in perm_l else PermissionScope.MEMORY_WRITE
    return PermissionScope.EXECUTE


class OrchestratorPermissionBroker:
    """Orchestration-level broker that aggregates and delegates to runtime."""

    def __init__(
        self,
        permission_broker: Optional[PermissionBroker] = None,
        policy_engine: Optional[PolicyEngine] = None,
    ) -> None:
        self.permission_broker = permission_broker or PermissionBroker()
        # PolicyEngine must share the same broker instance
        if policy_engine is not None:
            self.policy_engine = policy_engine
        else:
            self.policy_engine = PolicyEngine(broker=self.permission_broker)
        self._lock = threading.RLock()
        self._pending: Dict[str, PermissionRequestRecord] = {}
        self._history: List[PermissionRequestRecord] = []

    def aggregate(self, permissions: List[str]) -> List[str]:
        """Collect, normalize, deduplicate permissions (deterministic sorted)."""
        seen: set = set()
        out: List[str] = []
        for p in permissions:
            if not isinstance(p, str) or not p.strip():
                continue
            n = p.strip().lower()
            # Normalize: keep as-is but lowercased, deduplicate
            if n not in seen:
                seen.add(n)
                out.append(n)
        return sorted(out)

    def check(
        self,
        subject: str,
        permissions: List[str],
        resource: str = "*",
        context_id: Optional[str] = None,
    ) -> OrchestratorPermissionDecision:
        """Delegate to runtime PolicyEngine for each permission."""
        if not subject or not subject.strip():
            raise OrchestratorPermissionBrokerError("subject must be non-empty")
        perms = self.aggregate(permissions) if permissions else []
        # If no explicit permissions, check resource directly
        targets = perms if perms else [resource]
        has_ask = False
        for target in targets:
            scope = _infer_scope(target)
            req = PolicyRequest(
                subject=subject,
                action="execute",
                resource=target,
                scope=scope,
                context_id=context_id,
            )
            result = self.policy_engine.evaluate(req)
            if result.decision == PolicyDecision.DENY:
                return OrchestratorPermissionDecision.DENY
            if result.decision == PolicyDecision.INSUFFICIENT:
                has_ask = True
        if has_ask:
            return OrchestratorPermissionDecision.ASK
        return OrchestratorPermissionDecision.ALLOW

    def request(
        self,
        subject: str,
        permissions: List[str],
        resource: str = "*",
        context_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Tuple[str, OrchestratorPermissionDecision]:
        """Create a permission request, store pending if ASK, return decision."""
        decision = self.check(subject, permissions, resource, context_id)
        rid = request_id or f"perm-{uuid.uuid4().hex[:12]}"
        record = PermissionRequestRecord(
            request_id=rid,
            subject=subject,
            permissions=self.aggregate(permissions),
            resource=resource,
            decision=decision,
            evidence={"policy_checked": True, "permissions": self.aggregate(permissions)},
        )
        with self._lock:
            if rid in self._pending:
                raise OrchestratorPermissionBrokerError(f"request {rid!r} already exists")
            self._pending[rid] = record
            self._history.append(record)
        return rid, decision

    def approve(self, request_id: str, approved: bool) -> OrchestratorPermissionDecision:
        """Human approval for ASK requests — grants permissions if approved."""
        with self._lock:
            rec = self._pending.get(request_id)
            if rec is None:
                raise OrchestratorPermissionBrokerError(f"unknown request {request_id!r}")
            if rec.decision != OrchestratorPermissionDecision.ASK:
                raise OrchestratorPermissionBrokerError(f"request {request_id!r} is not ASK (is {rec.decision.value})")
            new_decision = OrchestratorPermissionDecision.ALLOW if approved else OrchestratorPermissionDecision.DENY
            rec.resolved_at = datetime.now(timezone.utc).isoformat()
            rec.resolved_decision = new_decision
            rec.evidence["human_approved"] = approved
            if approved:
                for perm in rec.permissions:
                    scope = _infer_scope(perm)
                    self.permission_broker.grant(rec.subject, Permission(scope, perm))
                # Also grant resource if different
                if rec.resource != "*" and rec.resource not in rec.permissions:
                    scope = _infer_scope(rec.resource)
                    self.permission_broker.grant(rec.subject, Permission(scope, rec.resource))
            return new_decision

    def get(self, request_id: str) -> PermissionRequestRecord:
        with self._lock:
            rec = self._pending.get(request_id)
            if rec is None:
                raise OrchestratorPermissionBrokerError(f"unknown request {request_id!r}")
            return rec

    def list_pending(self) -> List[PermissionRequestRecord]:
        with self._lock:
            return [r for r in self._pending.values() if r.decision == OrchestratorPermissionDecision.ASK and r.resolved_decision is None]

    def history(self) -> List[PermissionRequestRecord]:
        with self._lock:
            return list(self._history)

    def clear(self) -> None:
        with self._lock:
            self._pending.clear()
            self._history.clear()
