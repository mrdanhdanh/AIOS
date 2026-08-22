"""Tests for TASK-036 tenant isolation (INV-023)."""

from __future__ import annotations

from aios.tenancy.contracts import TenantResource, TenantScope
from aios.tenancy.tenant_manager import TenantManager


def test_tenant_new_fields() -> None:
    mgr = TenantManager()
    t = mgr.create_tenant("acme")
    t.organization_id = "org-1"
    t.project = "proj-1"
    t.workspace = "ws-1"
    assert t.to_dict()["organization_id"] == "org-1"


def test_resolve_scope() -> None:
    mgr = TenantManager()
    t = mgr.create_tenant("acme")
    proj = mgr.create_project("p", t.tenant_id)
    ws = mgr.create_workspace("w", proj.project_id)
    ctx = mgr.resolve_scope(t.tenant_id, proj.project_id, ws.workspace_id)
    assert ctx.scope == TenantScope.WORKSPACE
    assert ctx.workspace_id == ws.workspace_id


def test_assert_same_tenant_pass_and_raise() -> None:
    mgr = TenantManager()
    a = mgr.create_tenant("a")
    b = mgr.create_tenant("b")
    mgr.assert_same_tenant(a.tenant_id, a.tenant_id)
    try:
        mgr.assert_same_tenant(a.tenant_id, b.tenant_id)
        assert False, "should raise"
    except Exception:
        pass


def test_filter_by_tenant() -> None:
    mgr = TenantManager()
    a = mgr.create_tenant("a")
    b = mgr.create_tenant("b")
    items = [
        TenantResource("r1", a.tenant_id, "x"),
        TenantResource("r2", b.tenant_id, "x"),
    ]
    out = mgr.filter_by_tenant(items, a.tenant_id)
    assert [r.resource_id for r in out] == ["r1"]


def test_authorize_isolation() -> None:
    mgr = TenantManager()
    a = mgr.create_tenant("a")
    b = mgr.create_tenant("b")
    ctx = mgr.resolve_scope(a.tenant_id)
    assert mgr.authorize(ctx, TenantResource("r", a.tenant_id, "x")) is True
    assert mgr.authorize(ctx, TenantResource("r", b.tenant_id, "x")) is False
