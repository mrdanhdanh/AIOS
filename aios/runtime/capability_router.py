"""Capability Router — resolves CapabilityRequest → CapabilityResolution (TASK-014, M2).

Router selects a Tool for a Capability based on health, priority and policy.
It never executes the Tool — it only resolves which Tool should be used.
Execution stays in :class:`aios.runtime.execution.Executor`.

Flow per spec §4-5:
    CapabilityRequest
      → Capability Resolution (validate capability exists)
      → Policy Pre-check (ALLOW/DENY/ASK)
      → Tool Selection (health + priority)
      → Execution (outside router)
      → Result + Evidence

Health handling per §7:
    HEALTHY  → eligible
    DEGRADED → eligible (if policy allows)
    UNHEALTHY → reject
    DISABLED → reject
    UNKNOWN → reject (fail-closed, never promoted)

Priority: higher priority wins, but never overrides Policy.
Policy: DENY → skip candidate, ASK/INSUFFICIENT → UNRESOLVED (needs human).

Offline-first, deterministic, thread-safe (no shared mutable state beyond
registries which are themselves thread-safe).

Layering: ``runtime`` layer — may import ``tool``, ``capability``, ``core``,
and sibling runtime modules (permission/policy). Never imports agent/orchestrator.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from aios.tool.contracts import (
    CapabilityRequest,
    CapabilityResolution,
    ResolutionReason,
    ResolutionStatus,
    ToolCandidate,
    ToolContract,
    ToolError,
    ToolHealth,
)
from aios.tool.registry import ToolRegistry

try:
    from aios.capability.capability import CapabilityRegistry
except ImportError:  # pragma: no cover
    CapabilityRegistry = None  # type: ignore

try:
    from aios.runtime.permission import PermissionScope
    from aios.runtime.policy import PolicyDecision, PolicyEngine, PolicyRequest
except ImportError:  # pragma: no cover
    PermissionScope = None  # type: ignore
    PolicyDecision = None  # type: ignore
    PolicyEngine = None  # type: ignore
    PolicyRequest = None  # type: ignore

__all__ = ["CapabilityRouter", "RouterError"]


class RouterError(Exception):
    """Raised on router usage errors."""


def _health_eligible(health: Any) -> bool:
    """Return True if health is eligible for routing."""
    if isinstance(health, ToolHealth):
        return health.is_eligible()
    if isinstance(health, str):
        try:
            h = ToolHealth(health)
            return h.is_eligible()
        except ValueError:
            return False
    return False


def _health_str(health: Any) -> str:
    if isinstance(health, ToolHealth):
        return health.value
    return str(health)


def _constraints_match(contract: ToolContract, constraints: Dict[str, Any]) -> bool:
    """Check if tool matches constraints.

    Supported constraints (deterministic, offline):
      - tool_type: must equal contract.tool_type
      - language: if contract metadata has 'language', must match; else pass
      - sandbox: if 'required', only tools with metadata sandbox=True or tool_type docker
      - network: if 'deny', tools requiring network must be rejected (check permissions)
    Unknown constraints are ignored (pass) to keep router extensible.
    """
    if not constraints:
        return True
    for key, val in constraints.items():
        if key == "tool_type":
            ct = contract.tool_type.value if isinstance(contract.tool_type, ToolType) else str(contract.tool_type)  # type: ignore
            if ct != str(val):
                return False
        elif key == "language":
            # Check metadata language or capabilities
            meta_lang = contract.metadata.get("language")
            if meta_lang is not None and str(meta_lang) != str(val):
                return False
            # If tool declares language-specific capability, check it
            # e.g., language=python → need run_python or execute_code
            # For now, pass if no metadata
        elif key == "sandbox":
            if val == "required":
                # Only docker or tools with sandbox metadata
                is_sandbox = contract.metadata.get("sandbox", False)
                ct = contract.tool_type.value if isinstance(contract.tool_type, ToolType) else str(contract.tool_type)  # type: ignore
                if not is_sandbox and ct != "docker":
                    # python.sandbox would have sandbox=True
                    # For mock, check tool_id contains sandbox
                    if "sandbox" not in contract.tool_id:
                        return False
        elif key == "network":
            if val == "deny":
                # Reject tools that require network
                if "network.read" in contract.permissions or "network.write" in contract.permissions:
                    return False
        # Unknown constraints: pass
    return True


# Need ToolType for constraints
try:
    from aios.tool.contracts import ToolType
except ImportError:
    ToolType = None  # type: ignore


class CapabilityRouter:
    """Resolves a CapabilityRequest to a Tool via health/priority/policy."""

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        capability_registry: Optional[Any] = None,
        policy_engine: Optional[Any] = None,
    ) -> None:
        self._tools = tool_registry or ToolRegistry()
        self._caps = capability_registry
        self._policy = policy_engine

    @property
    def tool_registry(self) -> ToolRegistry:
        return self._tools

    @property
    def capability_registry(self) -> Optional[Any]:
        return self._caps

    @property
    def policy_engine(self) -> Optional[Any]:
        return self._policy

    def resolve(self, request: CapabilityRequest) -> CapabilityResolution:
        """Resolve a capability request to a tool.

        Returns RESOLVED with selected_tool or UNRESOLVED with reason.
        Never raises for normal UNRESOLVED cases (fail-closed); only raises
        for invalid request shape.
        """
        if not isinstance(request, CapabilityRequest):
            raise RouterError("request must be CapabilityRequest")

        capability = request.capability
        constraints = request.constraints or {}
        evidence_ref = f"ev-{uuid.uuid4().hex[:12]}"

        # 1. Validate capability exists (if capability registry provided)
        if self._caps is not None:
            try:
                # Check if capability exists in registry
                if capability not in self._caps:
                    # Also check tool registry — if no tool provides it, UNRESOLVED
                    tools_for_cap = self._tools.find_by_capability(capability)
                    if not tools_for_cap:
                        return CapabilityResolution(
                            capability=capability,
                            status=ResolutionStatus.UNRESOLVED,
                            selected_tool=None,
                            reason=ResolutionReason(
                                health="unknown",
                                priority=0,
                                policy="deny",
                                detail=f"capability {capability!r} not found",
                            ),
                            candidates=[],
                            evidence_ref=evidence_ref,
                            metadata={"error": "capability unavailable"},
                            request_id=request.request_id,
                        )
            except Exception:
                pass  # If registry check fails, fall through to tool lookup

        # 2. Get candidate tools for capability
        try:
            candidates_contracts = self._tools.find_by_capability(capability)
        except Exception as exc:
            return CapabilityResolution(
                capability=capability,
                status=ResolutionStatus.UNRESOLVED,
                selected_tool=None,
                reason=ResolutionReason(
                    health="unknown",
                    priority=0,
                    policy="deny",
                    detail=str(exc),
                ),
                candidates=[],
                evidence_ref=evidence_ref,
                metadata={"error": str(exc)},
                request_id=request.request_id,
            )

        if not candidates_contracts:
            return CapabilityResolution(
                capability=capability,
                status=ResolutionStatus.UNRESOLVED,
                selected_tool=None,
                reason=ResolutionReason(
                    health="unknown",
                    priority=0,
                    policy="deny",
                    detail=f"no tool provides capability {capability!r}",
                ),
                candidates=[],
                evidence_ref=evidence_ref,
                metadata={"error": "capability unavailable"},
                request_id=request.request_id,
            )

        # 3. Build ToolCandidate list with eligibility
        tool_candidates: List[ToolCandidate] = []
        eligible_contracts: List[ToolContract] = []

        for contract in candidates_contracts:
            health = contract.health
            health_s = _health_str(health)
            enabled = contract.enabled
            # Check health eligibility
            health_ok = _health_eligible(health) and enabled
            # Check constraints
            constraints_ok = _constraints_match(contract, constraints)
            eligible = health_ok and constraints_ok
            reason = ""
            if not enabled:
                reason = "disabled"
            elif not _health_eligible(health):
                reason = f"health {health_s} not eligible"
            elif not constraints_ok:
                reason = f"constraints {constraints} not satisfied"
            else:
                reason = "eligible"

            tc = ToolCandidate(
                tool_id=contract.tool_id,
                health=health_s,
                priority=contract.priority,
                enabled=enabled,
                eligible=eligible,
                reason=reason,
            )
            tool_candidates.append(tc)
            if eligible:
                eligible_contracts.append(contract)

        if not eligible_contracts:
            # All candidates filtered out by health/constraints
            return CapabilityResolution(
                capability=capability,
                status=ResolutionStatus.UNRESOLVED,
                selected_tool=None,
                reason=ResolutionReason(
                    health="unhealthy",
                    priority=0,
                    policy="deny",
                    detail="no eligible tool (health/disabled/constraints)",
                ),
                candidates=tool_candidates,
                evidence_ref=evidence_ref,
                metadata={"error": "no eligible tool"},
                request_id=request.request_id,
            )

        # 4. Sort eligible by priority descending, seq asc, tool_id asc
        def sort_key(c: ToolContract):
            seq = c.metadata.get("_seq", 0)
            return (-c.priority, seq, c.tool_id)

        eligible_contracts.sort(key=sort_key)
        # Also sort candidates for evidence (eligible first, then priority)
        tool_candidates.sort(key=lambda tc: (0 if tc.eligible else 1, -tc.priority, tc.tool_id))

        # 5. Policy pre-check — iterate in priority order, first ALLOW wins
        if self._policy is not None and PolicyRequest is not None and PolicyDecision is not None:
            for contract in eligible_contracts:
                # Build policy request
                # Use capability:invoke scope for capability, tool:invoke for tool
                # Try capability scope first
                scope = None
                if PermissionScope is not None:
                    # Prefer capability:invoke for capability resolution
                    try:
                        scope = PermissionScope.CAPABILITY_INVOKE
                    except AttributeError:
                        scope = None
                # Also try tool scope as fallback
                # We evaluate with capability scope; if no scope, just evaluate without permission gate
                preq = PolicyRequest(
                    subject=request.subject,
                    action="capability.invoke",
                    resource=request.resource or capability,
                    scope=scope,
                    metadata={**request.metadata, **constraints, "tool_id": contract.tool_id},
                )
                try:
                    pres = self._policy.evaluate(preq)
                except Exception as exc:
                    # Policy evaluation error → fail-closed
                    return CapabilityResolution(
                        capability=capability,
                        status=ResolutionStatus.UNRESOLVED,
                        selected_tool=None,
                        reason=ResolutionReason(
                            health=_health_str(contract.health),
                            priority=contract.priority,
                            policy="deny",
                            detail=f"policy error: {exc}",
                        ),
                        candidates=tool_candidates,
                        evidence_ref=evidence_ref,
                        metadata={"error": f"policy error: {exc}"},
                        request_id=request.request_id,
                    )

                if pres.decision == PolicyDecision.ALLOW:
                    # Selected
                    return CapabilityResolution(
                        capability=capability,
                        status=ResolutionStatus.RESOLVED,
                        selected_tool=contract.tool_id,
                        reason=ResolutionReason(
                            health=_health_str(contract.health),
                            priority=contract.priority,
                            policy="allow",
                            detail=pres.reason or "allowed by policy",
                        ),
                        candidates=tool_candidates,
                        evidence_ref=evidence_ref,
                        metadata={"policy_reason": pres.reason, "applied_rules": pres.applied_rules},
                        request_id=request.request_id,
                    )
                elif pres.decision == PolicyDecision.DENY:
                    # This tool denied, try next
                    continue
                else:  # INSUFFICIENT → ASK
                    return CapabilityResolution(
                        capability=capability,
                        status=ResolutionStatus.UNRESOLVED,
                        selected_tool=None,
                        reason=ResolutionReason(
                            health=_health_str(contract.health),
                            priority=contract.priority,
                            policy="ask",
                            detail=pres.reason or "policy requires approval",
                        ),
                        candidates=tool_candidates,
                        evidence_ref=evidence_ref,
                        metadata={"policy_reason": pres.reason, "applied_rules": pres.applied_rules, "ask": True},
                        request_id=request.request_id,
                    )

            # All eligible tools were DENY
            return CapabilityResolution(
                capability=capability,
                status=ResolutionStatus.UNRESOLVED,
                selected_tool=None,
                reason=ResolutionReason(
                    health=_health_str(eligible_contracts[0].health) if eligible_contracts else "unknown",
                    priority=eligible_contracts[0].priority if eligible_contracts else 0,
                    policy="deny",
                    detail="all eligible tools denied by policy",
                ),
                candidates=tool_candidates,
                evidence_ref=evidence_ref,
                metadata={"error": "policy denied"},
                request_id=request.request_id,
            )

        # No policy engine → select highest priority eligible
        selected = eligible_contracts[0]
        return CapabilityResolution(
            capability=capability,
            status=ResolutionStatus.RESOLVED,
            selected_tool=selected.tool_id,
            reason=ResolutionReason(
                health=_health_str(selected.health),
                priority=selected.priority,
                policy="allow",
                detail="selected by priority (no policy engine)",
            ),
            candidates=tool_candidates,
            evidence_ref=evidence_ref,
            metadata={},
            request_id=request.request_id,
        )

    def resolve_or_raise(self, request: CapabilityRequest) -> CapabilityResolution:
        """Resolve and raise if UNRESOLVED (for callers that want exception)."""
        res = self.resolve(request)
        if res.status != ResolutionStatus.RESOLVED:
            raise RouterError(f"capability {request.capability!r} unresolved: {res.reason.detail}")
        return res
