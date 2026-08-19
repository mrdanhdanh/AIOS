"""Automated tests for the Task Registry gate (Rule 1)."""

import pytest

from aios.governance.task_registry import (
    RegistryError,
    TaskRegistry,
    TaskStatus,
)


def test_create_and_get_task():
    reg = TaskRegistry()
    t = reg.create_task("TASK-001", "Governance", milestone="M0")
    assert t.task_id == "TASK-001"
    assert reg.get("TASK-001") is t
    assert reg.exists("TASK-001")
    assert not reg.exists("TASK-999")


def test_duplicate_id_is_rejected():
    """Rule 1: creating a task with an existing ID must be rejected."""
    reg = TaskRegistry()
    reg.create_task("TASK-001", "Governance")
    with pytest.raises(RegistryError):
        reg.create_task("TASK-001", "Duplicate")


def test_deprecated_id_is_never_reused():
    """Rule 1: a deprecated ID must not be reused."""
    reg = TaskRegistry()
    reg.create_task("TASK-010", "Old")
    reg.deprecate("TASK-010")
    assert reg.is_deprecated("TASK-010")
    assert reg.get("TASK-010").status == TaskStatus.DEPRECATED
    with pytest.raises(RegistryError):
        reg.create_task("TASK-010", "Reuse attempt")


def test_deprecate_does_not_delete():
    reg = TaskRegistry()
    reg.create_task("TASK-011", "Temp")
    reg.deprecate("TASK-011")
    # Still retrievable, still registered, but terminal.
    assert reg.exists("TASK-011")
    assert reg.get("TASK-011").status == TaskStatus.DEPRECATED


def test_dependency_must_reference_registered_task():
    reg = TaskRegistry()
    reg.create_task("TASK-001", "Governance")
    with pytest.raises(RegistryError):
        reg.add_dependency("TASK-001", "TASK-002")  # not registered


def test_self_dependency_rejected():
    reg = TaskRegistry()
    reg.create_task("TASK-001", "Governance")
    with pytest.raises(RegistryError):
        reg.add_dependency("TASK-001", "TASK-001")
