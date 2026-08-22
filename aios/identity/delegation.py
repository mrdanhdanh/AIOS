"""Delegation manager — delegates permissions with capability attenuation.

A delegatee can never receive broader permissions than the delegator holds
(capability attenuation). Fail-closed: invalid delegations are rejected.
"""

from __future__ import annotations

from aios.identity.contracts import Delegation, IdentityError, Permission, Principal


class DelegationManager:
    """Manages delegations between principals."""

    def __init__(self) -> None:
        self._delegations: dict[str, Delegation] = {}

    def delegate(
        self,
        delegator: Principal,
        delegatee: Principal,
        permissions: set[Permission],
        resource_scope: str = "",
    ) -> Delegation:
        """Create a delegation, attenuating to the delegator's permissions."""
        delegator_perms = delegator.effective_permissions()
        attenuated = permissions & delegator_perms
        if not attenuated:
            raise IdentityError(
                "Delegation would grant permissions the delegator does not hold"
            )
        delegation = Delegation(
            delegator_id=delegator.principal_id,
            delegatee_id=delegatee.principal_id,
            permissions=attenuated,
            resource_scope=resource_scope,
        )
        self._delegations[delegation.delegation_id] = delegation
        return delegation

    def revoke(self, delegation_id: str) -> None:
        d = self._delegations.get(delegation_id)
        if d is None:
            raise IdentityError(f"Delegation {delegation_id!r} not found")
        d.active = False

    def active_for(self, delegatee_id: str) -> list[Delegation]:
        return [
            d
            for d in self._delegations.values()
            if d.delegatee_id == delegatee_id and d.active
        ]

    def permissions_for(self, delegatee_id: str) -> set[Permission]:
        perms: set[Permission] = set()
        for d in self.active_for(delegatee_id):
            perms.update(d.permissions)
        return perms
