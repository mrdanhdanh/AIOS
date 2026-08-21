"""Tests for identity module."""
from __future__ import annotations
import pytest
from aios.identity.contracts import IdentityError, Permission, Principal, Policy, Role
from aios.identity.identity_service import IdentityService
from aios.identity.rbac import RBACEnforcer

class TestIdentity:
    def test_role_permissions(self):
        r = Role(name="admin", permissions={Permission.READ, Permission.WRITE})
        assert r.has_permission(Permission.READ)
        assert not r.has_permission(Permission.DELETE)
    def test_principal_effective_permissions(self):
        r1 = Role(name="r", permissions={Permission.READ})
        p = Principal(name="u", roles=[r1])
        assert Permission.READ in p.effective_permissions()
    def test_service_create_role(self):
        svc = IdentityService()
        role = svc.create_role("admin", {Permission.ADMIN})
        assert role.name == "admin"
    def test_service_duplicate_role(self):
        svc = IdentityService()
        svc.create_role("admin")
        with pytest.raises(IdentityError): svc.create_role("admin")
    def test_assign_revoke_role(self):
        svc = IdentityService()
        role = svc.create_role("w", {Permission.WRITE})
        p = svc.create_principal("bob")
        svc.assign_role(p.principal_id, role.role_id)
        assert len(p.roles) == 1
        svc.revoke_role(p.principal_id, role.role_id)
        assert len(p.roles) == 0
    def test_rbac_enforcer(self):
        enforcer = RBACEnforcer()
        pol = Policy(name="read_ok", required_permission=Permission.READ, effect="allow")
        enforcer.add_policy(pol)
        result = enforcer.evaluate(Principal(name="u"), Permission.READ)
        assert result["allowed"] is True
    def test_rbac_no_policy_fallback(self):
        enforcer = RBACEnforcer()
        r = Role(name="r", permissions={Permission.READ})
        result = enforcer.evaluate(Principal(name="u", roles=[r]), Permission.READ)
        assert result["allowed"] is True
        assert result["reason"] == "rbac_fallback"
