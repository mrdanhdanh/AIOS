"""Delegation engine (TASK-059).

Authority attenuation (multi-dimensional) + anti-amplification guard +
bounded resource limits + delegation provenance. The parent remains
accountable for the aggregated outcome.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from aios.multi_agent_autonomy.contracts import (
    Authority,
    DelegationDecision,
    DelegationVerdict,
    DelegateRequest,
)

_RISK_ORDER = ["low", "medium", "high", "critical"]


class AuthorityAttenuator:
    """Computes child authority = Parent ∩ Scope ∩ Policy ∩ Budget."""

    def attenuate(
        self,
        parent: Authority,
        scope: Authority,
        policy: Authority,
    ) -> Authority:
        capabilities = (
            parent.capabilities & scope.capabilities & policy.capabilities
        )
        tool_permissions = (
            parent.tool_permissions & scope.tool_permissions & policy.tool_permissions
        )
        resource_budget = min(parent.resource_budget, scope.resource_budget, policy.resource_budget)
        deadline = min(parent.deadline, scope.deadline, policy.deadline)
        # tenant scope must be a subset of parent's; otherwise it is a scope escape.
        tenant_scope = scope.tenant_scope if (
            not parent.tenant_scope or scope.tenant_scope == parent.tenant_scope
        ) else ""
        approval_required = parent.approval_required or scope.approval_required or policy.approval_required
        max_depth = min(parent.max_depth, scope.max_depth, policy.max_depth) - 1
        risk_idx = min(
            _RISK_ORDER.index(parent.risk_level) if parent.risk_level in _RISK_ORDER else 0,
            _RISK_ORDER.index(scope.risk_level) if scope.risk_level in _RISK_ORDER else 0,
            _RISK_ORDER.index(policy.risk_level) if policy.risk_level in _RISK_ORDER else 0,
        )
        return Authority(
            capabilities=capabilities,
            resource_budget=resource_budget,
            deadline=deadline,
            tenant_scope=tenant_scope,
            tool_permissions=tool_permissions,
            approval_required=approval_required,
            max_depth=max_depth,
            risk_level=_RISK_ORDER[risk_idx],
        )


class DelegationManager:
    def __init__(
        self,
        governor_decision: Callable[[DelegateRequest, Authority], DelegationVerdict] | None = None,
    ) -> None:
        self._attenuator = AuthorityAttenuator()
        self._governor = governor_decision
        self._child_count: dict[str, int] = {}
        self._cumulative_resource: dict[str, float] = {}
        self._records: list[dict[str, Any]] = []

    def _anti_amplification_ok(self, parent: Authority, child: Authority) -> tuple[bool, str]:
        if not child.capabilities.issubset(parent.capabilities):
            return False, "child capabilities exceed parent"
        if child.resource_budget > parent.resource_budget:
            return False, "child resource budget exceeds parent"
        if parent.tenant_scope and child.tenant_scope != parent.tenant_scope:
            return False, "child tenant scope escapes parent"
        if child.max_depth > parent.max_depth:
            return False, "child max_depth exceeds parent"
        if _RISK_ORDER.index(child.risk_level) > _RISK_ORDER.index(parent.risk_level):
            return False, "child risk level exceeds parent"
        return True, ""

    def decide(
        self,
        request: DelegateRequest,
        parent_authority: Authority,
        scope_authority: Authority,
        policy_authority: Authority,
    ) -> DelegationDecision:
        # 1. Attenuate.
        child = self._attenuator.attenuate(parent_authority, scope_authority, policy_authority)
        if not child.capabilities and child.resource_budget <= 0:
            return DelegationDecision(DelegationVerdict.BLOCKED, "empty attenuated authority", request=request)
        # 2. Anti-amplification.
        ok, reason = self._anti_amplification_ok(parent_authority, child)
        if not ok:
            return DelegationDecision(DelegationVerdict.BLOCKED, reason, child, request)
        # 3. Bounded limits.
        gid = request.parent_goal_id
        if child.max_depth < 0:
            return DelegationDecision(DelegationVerdict.BLOCKED, "delegation depth exceeded", child, request)
        if request.max_children and self._child_count.get(gid, 0) >= request.max_children:
            return DelegationDecision(DelegationVerdict.BLOCKED, "child count exceeded", child, request)
        if request.delegation_budget <= 0:
            return DelegationDecision(DelegationVerdict.BLOCKED, "delegation budget exhausted", child, request)
        cum = self._cumulative_resource.get(gid, 0.0) + request.execution_budget
        if cum > parent_authority.resource_budget:
            return DelegationDecision(DelegationVerdict.BLOCKED, "cumulative resource exceeded", child, request)
        # 4. Governor authority.
        if self._governor is not None:
            gv = self._governor(request, child)
            if gv == DelegationVerdict.BLOCKED:
                return DelegationDecision(DelegationVerdict.BLOCKED, "governor blocked", child, request)
            if gv == DelegationVerdict.ASK_HUMAN:
                return DelegationDecision(DelegationVerdict.ASK_HUMAN, "governor requires approval", child, request)
        # 5. Approve + record provenance.
        self._child_count[gid] = self._child_count.get(gid, 0) + 1
        self._cumulative_resource[gid] = cum
        self._records.append({
            "parent_goal_id": gid,
            "sub_goal": request.sub_goal,
            "child_authority": child.to_dict(),
            "evidence_ref": request.evidence_ref,
        })
        return DelegationDecision(DelegationVerdict.APPROVED, "delegation approved", child, request)

    @property
    def records(self) -> list[dict[str, Any]]:
        return list(self._records)
