"""IdentityService — manages principals, roles, and policies."""
from __future__ import annotations
from aios.identity.contracts import IdentityError, Permission, Principal, Policy, Role

class IdentityService:
    def __init__(self) -> None:
        self._principals: dict[str, Principal] = {}
        self._roles: dict[str, Role] = {}
        self._policies: dict[str, Policy] = {}
    def create_role(self, name: str, permissions: set | None = None) -> Role:
        if any(r.name == name for r in self._roles.values()):
            raise IdentityError(f"Role '{name}' already exists")
        role = Role(name=name, permissions=permissions or set())
        self._roles[role.role_id] = role
        return role
    def get_role(self, role_id: str) -> Role:
        if role_id not in self._roles: raise IdentityError(f"Role {role_id!r} not found")
        return self._roles[role_id]
    def list_roles(self) -> list[Role]: return list(self._roles.values())
    def create_principal(self, name: str, tenant_id: str = "") -> Principal:
        p = Principal(name=name, tenant_id=tenant_id)
        self._principals[p.principal_id] = p
        return p
    def get_principal(self, pid: str) -> Principal:
        if pid not in self._principals: raise IdentityError(f"Principal {pid!r} not found")
        return self._principals[pid]
    def assign_role(self, pid: str, rid: str) -> None:
        p, r = self.get_principal(pid), self.get_role(rid)
        if r not in p.roles: p.roles.append(r)
    def revoke_role(self, pid: str, rid: str) -> None:
        p = self.get_principal(pid)
        self.get_role(rid)
        p.roles = [r for r in p.roles if r.role_id != rid]
    def list_principals(self) -> list[Principal]: return list(self._principals.values())
    def register_policy(self, policy: Policy) -> None: self._policies[policy.policy_id] = policy
    def get_policy(self, pid: str) -> Policy:
        if pid not in self._policies: raise IdentityError(f"Policy {pid!r} not found")
        return self._policies[pid]
    def list_policies(self) -> list[Policy]: return list(self._policies.values())
    def to_dict(self) -> dict:
        return {"principals": len(self._principals), "roles": len(self._roles), "policies": len(self._policies)}
