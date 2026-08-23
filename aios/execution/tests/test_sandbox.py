"""Tests for the sandbox manager (T136)."""

import pytest

from aios.execution import IsolationLevel, SandboxManager, SandboxStatus
from aios.execution._common import ExecutionError


def test_create_immutable_id():
    m = SandboxManager()
    rec = m.create(IsolationLevel.PROCESS, policy_ref="pol1")
    assert rec.sandbox_id
    assert rec.status == SandboxStatus.CREATED


def test_duplicate_id_rejected():
    m = SandboxManager()
    m.create(IsolationLevel.FS, sandbox_id="sb1", policy_ref="pol1")
    with pytest.raises(ExecutionError):
        m.create(IsolationLevel.FS, sandbox_id="sb1", policy_ref="pol1")


def test_isolate_requires_policy():
    m = SandboxManager()
    rec = m.create(IsolationLevel.NETWORK)
    with pytest.raises(ExecutionError):
        m.isolate(rec.sandbox_id)


def test_isolate_sets_isolated():
    m = SandboxManager()
    rec = m.create(IsolationLevel.PROCESS, policy_ref="pol1")
    m.isolate(rec.sandbox_id)
    assert m.get(rec.sandbox_id).status == SandboxStatus.ISOLATED


def test_healthcheck():
    m = SandboxManager()
    rec = m.create(IsolationLevel.FS, policy_ref="pol1")
    assert m.healthcheck(rec.sandbox_id) is True


def test_destroy():
    m = SandboxManager()
    rec = m.create(IsolationLevel.FS, policy_ref="pol1")
    m.destroy(rec.sandbox_id)
    assert m.get(rec.sandbox_id).status == SandboxStatus.DESTROYED


def test_is_usable_requires_isolated_healthy():
    m = SandboxManager()
    rec = m.create(IsolationLevel.FS, policy_ref="pol1")
    assert m.is_usable(rec.sandbox_id) is False  # not isolated yet
    m.isolate(rec.sandbox_id)
    assert m.is_usable(rec.sandbox_id) is True


def test_provenance_hash():
    m = SandboxManager()
    rec = m.create(IsolationLevel.FS, policy_ref="pol1")
    prov = m.provenance(rec.sandbox_id)
    assert prov["sandbox_id"] == rec.sandbox_id
    assert prov["content_hash"]
