"""Tests for the workspace / snapshot manager (T137)."""

import pytest

from aios.execution import WorkspaceManager, WorkspaceStatus
from aios.execution._common import ExecutionError


def test_create_immutable_id():
    m = WorkspaceManager()
    rec = m.create(policy_ref="pol1")
    assert rec.workspace_id
    assert rec.status == WorkspaceStatus.ACTIVE


def test_duplicate_id_rejected():
    m = WorkspaceManager()
    m.create(workspace_id="ws1", policy_ref="pol1")
    with pytest.raises(ExecutionError):
        m.create(workspace_id="ws1", policy_ref="pol1")


def test_snapshot_requires_state():
    m = WorkspaceManager()
    rec = m.create(policy_ref="pol1")
    with pytest.raises(ExecutionError):
        m.snapshot(rec.workspace_id, "")


def test_snapshot_has_hash():
    m = WorkspaceManager()
    rec = m.create(policy_ref="pol1")
    snap = m.snapshot(rec.workspace_id, "state-data", policy_ref="pol1")
    assert snap.state_hash
    assert snap.restore_available is True


def test_restore_returns_hash():
    m = WorkspaceManager()
    rec = m.create(policy_ref="pol1")
    snap = m.snapshot(rec.workspace_id, "state-data", policy_ref="pol1")
    assert m.restore(snap.snapshot_id) == snap.state_hash


def test_restore_unknown_fails():
    m = WorkspaceManager()
    with pytest.raises(ExecutionError):
        m.restore("sn-missing")


def test_archive():
    m = WorkspaceManager()
    rec = m.create(policy_ref="pol1")
    m.archive(rec.workspace_id)
    assert m.get(rec.workspace_id).status == WorkspaceStatus.ARCHIVED


def test_provenance():
    m = WorkspaceManager()
    rec = m.create(policy_ref="pol1")
    m.snapshot(rec.workspace_id, "state-data", policy_ref="pol1")
    prov = m.provenance(rec.workspace_id)
    assert prov["workspace_id"] == rec.workspace_id
    assert prov["snapshot_count"] == 1
    assert prov["content_hash"]
