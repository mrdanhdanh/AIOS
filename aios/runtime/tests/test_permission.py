"""Automated tests for the permission broker (TASK-004)."""

import pytest

from aios.runtime.permission import Permission, PermissionBroker, PermissionScope


def test_broker_grant_and_check():
    broker = PermissionBroker()
    broker.grant("agent-1", Permission(PermissionScope.EXECUTE, "workflow:*"))
    assert broker.has("agent-1", PermissionScope.EXECUTE, "workflow:demo")
    assert broker.check("agent-1", PermissionScope.EXECUTE, "workflow:demo")


def test_broker_wildcard_resource():
    broker = PermissionBroker()
    broker.grant("agent-1", Permission(PermissionScope.READ, "*"))
    assert broker.has("agent-1", PermissionScope.READ, "anything")
    assert not broker.has("agent-1", PermissionScope.WRITE, "anything")


def test_broker_specific_resource_denies_other():
    broker = PermissionBroker()
    broker.grant("agent-1", Permission(PermissionScope.WRITE, "file:/tmp/a"))
    assert broker.has("agent-1", PermissionScope.WRITE, "file:/tmp/a")
    assert not broker.has("agent-1", PermissionScope.WRITE, "file:/tmp/b")


def test_broker_revoke():
    broker = PermissionBroker()
    perm = Permission(PermissionScope.ADMIN, "*")
    broker.grant("agent-1", perm)
    assert broker.has("agent-1", PermissionScope.ADMIN, "x")
    broker.revoke("agent-1", perm)
    assert not broker.has("agent-1", PermissionScope.ADMIN, "x")


def test_broker_unknown_subject_denied():
    broker = PermissionBroker()
    assert not broker.has("ghost", PermissionScope.EXECUTE, "workflow:x")


def test_broker_list_for():
    broker = PermissionBroker()
    broker.grant_many(
        "agent-1",
        [
            Permission(PermissionScope.READ, "*"),
            Permission(PermissionScope.WRITE, "file:/tmp"),
        ],
    )
    perms = broker.list_for("agent-1")
    assert len(perms) == 2


def test_permission_scope_values():
    assert {s.value for s in PermissionScope} >= {
        "execute",
        "read",
        "write",
        "delete",
        "admin",
        "capability:invoke",
        "tool:invoke",
    }


def test_permission_matches():
    p = Permission(PermissionScope.TOOL_INVOKE, "tool:*")
    assert p.matches(PermissionScope.TOOL_INVOKE, "tool:calc")
    assert not p.matches(PermissionScope.CAPABILITY_INVOKE, "tool:calc")
