"""Resource + Network + Command Policy (TASK-138, M20).

Enforces resource (cpu/mem), network (egress) and command (allow/deny) policy
for executions (T135). Fail-closed: any violation yields ``decision=deny`` ->
BLOCK (T078). Every decision carries provenance (T001 Rule 5). Deterministic:
same policy + same request -> same decision.

Layering: ``execution`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple

from aios.execution._common import ExecutionError, _hash


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass
class ResourceLimit:
    """CPU/memory quota (T039)."""

    cpu: float  # cores
    mem_mb: int

    def __post_init__(self) -> None:
        if self.cpu <= 0 or self.mem_mb <= 0:
            raise ExecutionError("Resource limits must be positive (T039).")


@dataclass
class ExecutionPolicy:
    """Resource + network + command policy bound to an execution (T138)."""

    execution_ref: str
    resource_limit: ResourceLimit
    network_egress: bool  # True = allow egress
    command_allowlist: Tuple[str, ...] = field(default_factory=tuple)
    policy_id: str = field(default_factory=lambda: f"pol-{uuid.uuid4().hex[:12]}")
    evidence_ref: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.execution_ref:
            raise ExecutionError("execution_ref required (T135).")


@dataclass
class PolicyDecision:
    """Result of a policy evaluation (T138)."""

    decision: Decision
    reason: str
    policy_ref: str
    evidence_ref: str = field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:12]}")

    def content_hash(self) -> str:
        return _hash(f"{self.policy_ref}|{self.decision.value}|{self.reason}")


class PolicyEngine:
    """Fail-closed policy enforcement for executions (T138)."""

    def __init__(self) -> None:
        self._policies: Dict[str, ExecutionPolicy] = {}

    def register(self, policy: ExecutionPolicy) -> ExecutionPolicy:
        if policy.policy_id in self._policies:
            raise ExecutionError(f"Duplicate policy_id '{policy.policy_id}'.")
        self._policies[policy.policy_id] = policy
        return policy

    def evaluate(
        self,
        policy_id: str,
        command: str,
        cpu_request: float = 0.0,
        mem_request: int = 0,
        network_egress: bool = False,
    ) -> PolicyDecision:
        policy = self._policies.get(policy_id)
        if policy is None:
            raise ExecutionError(f"Unknown policy '{policy_id}'.")
        # Resource policy (T039)
        if cpu_request > policy.resource_limit.cpu:
            return self._deny(policy, f"cpu {cpu_request} > limit {policy.resource_limit.cpu}")
        if mem_request > policy.resource_limit.mem_mb:
            return self._deny(policy, f"mem {mem_request} > limit {policy.resource_limit.mem_mb}")
        # Network policy (T040)
        if network_egress and not policy.network_egress:
            return self._deny(policy, "network egress denied")
        # Command policy
        if policy.command_allowlist and command not in policy.command_allowlist:
            return self._deny(policy, f"command '{command}' not allowlisted")
        return PolicyDecision(Decision.ALLOW, "ok", policy.policy_id)

    def _deny(self, policy: ExecutionPolicy, reason: str) -> PolicyDecision:
        return PolicyDecision(Decision.DENY, reason, policy.policy_id)

    def provenance(self, policy_id: str) -> dict:
        policy = self._policies.get(policy_id)
        if policy is None:
            raise ExecutionError(f"Unknown policy '{policy_id}'.")
        payload = (
            f"{policy.policy_id}|{policy.resource_limit.cpu}|"
            f"{policy.resource_limit.mem_mb}|{policy.network_egress}|"
            f"{sorted(policy.command_allowlist)}"
        )
        return {
            "policy_id": policy.policy_id,
            "execution_ref": policy.execution_ref,
            "resource_limit": f"{policy.resource_limit.cpu}c/{policy.resource_limit.mem_mb}mb",
            "network_egress": policy.network_egress,
            "command_allowlist": list(policy.command_allowlist),
            "evidence_ref": policy.evidence_ref,
            "content_hash": _hash(payload),
        }
