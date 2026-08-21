"""Tests for tenancy module."""
from __future__ import annotations
import pytest
from aios.tenancy.contracts import Tenant, TenantBoundary, TenantError, TenantStatus
from aios.tenancy.tenant_manager import TenantManager

class TestTenancy:
    def test_create_tenant(self):
        mgr = TenantManager()
        t = mgr.create_tenant("acme")
        assert t.name == "acme"
        assert t.is_active
    def test_duplicate_tenant(self):
        mgr = TenantManager()
        mgr.create_tenant("acme")
        with pytest.raises(TenantError): mgr.create_tenant("acme")
    def test_suspend(self):
        mgr = TenantManager()
        t = mgr.create_tenant("acme")
        mgr.suspend_tenant(t.tenant_id)
        assert t.status == TenantStatus.SUSPENDED
    def test_boundary_check(self):
        mgr = TenantManager()
        t = mgr.create_tenant("acme", TenantBoundary.DEDICATED)
        assert mgr.check_boundary(t.tenant_id, TenantBoundary.SHARED)
        assert mgr.check_boundary(t.tenant_id, TenantBoundary.DEDICATED)
        assert not mgr.check_boundary(t.tenant_id, TenantBoundary.ISOLATED)
    def test_list_tenants(self):
        mgr = TenantManager()
        mgr.create_tenant("a"); mgr.create_tenant("b")
        assert len(mgr.list_tenants()) == 2
