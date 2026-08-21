"""RBACEnforcer — checks permissions against principal roles + ABAC policies."""
from __future__ import annotations
from aios.identity.contracts import Permission, Principal, Policy

class RBACEnforcer:
    def __init__(self) -> None:
        self._policies: list[Policy] = []
    def add_policy(self, policy: Policy) -> None: self._policies.append(policy)
    def remove_policy(self, pid: str) -> None: self._policies = [p for p in self._policies if p.policy_id != pid]
    def check_permission(self, principal: Principal, perm: Permission) -> bool: return perm in principal.effective_permissions()
    def evaluate(self, principal: Principal, perm: Permission) -> dict:
        applicable = [p for p in self._policies if p.required_permission == perm]
        if not applicable:
            return {"allowed": self.check_permission(principal, perm), "reason": "rbac_fallback", "policy_id": None}
        for pol in applicable:
            if pol.effect == "deny" and not pol.evaluate(principal):
                return {"allowed": False, "reason": f"denied_by_policy:{pol.name}", "policy_id": pol.policy_id}
        for pol in applicable:
            if pol.effect == "allow" and pol.evaluate(principal):
                return {"allowed": True, "reason": f"allowed_by_policy:{pol.name}", "policy_id": pol.policy_id}
        return {"allowed": False, "reason": "no_matching_allow_policy", "policy_id": None}
