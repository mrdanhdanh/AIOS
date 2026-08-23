"""Workspace / Snapshot Manager (TASK-137, M20).

Manages per-execution workspaces and state snapshots (checkpoints) so an
execution (T135) can resume or roll back. ``workspace_id`` / ``snapshot_id`` are
immutable (T001 Rule 1). Snapshots carry a ``state_hash`` (T078) and provenance
(T001 Rule 5). Fail-closed: a snapshot whose state cannot be hashed is rejected.

Layering: ``execution`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from aios.execution._common import ExecutionError, _hash, _now


class WorkspaceStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class SnapshotRecord:
    """Immutable-by-id workspace snapshot (T137, T066)."""

    snapshot_id: str
    workspace_id: str
    state_hash: str
    restore_available: bool
    policy_ref: Optional[str] = None
    evidence_ref: Optional[str] = None
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.snapshot_id:
            raise ExecutionError("snapshot_id required (T001 Rule 1, immutable).")
        if not self.state_hash:
            raise ExecutionError("state_hash required (T078).")


@dataclass
class WorkspaceRecord:
    """Immutable-by-id workspace record (T137)."""

    workspace_id: str
    status: WorkspaceStatus
    policy_ref: Optional[str] = None
    evidence_ref: Optional[str] = None
    created_at: str = field(default_factory=_now)


class WorkspaceManager:
    """Manages workspaces and snapshots with fail-closed restore (T137)."""

    def __init__(self) -> None:
        self._workspaces: Dict[str, WorkspaceRecord] = {}
        self._snapshots: Dict[str, SnapshotRecord] = {}
        self._snapshots_by_ws: Dict[str, List[str]] = {}

    def create(
        self,
        policy_ref: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> WorkspaceRecord:
        wid = workspace_id or f"ws-{uuid.uuid4().hex[:12]}"
        if wid in self._workspaces:
            raise ExecutionError(f"Duplicate workspace_id '{wid}' (T001 Rule 1).")
        rec = WorkspaceRecord(
            workspace_id=wid,
            status=WorkspaceStatus.ACTIVE,
            policy_ref=policy_ref,
            evidence_ref=f"ev-{uuid.uuid4().hex[:12]}",
        )
        self._workspaces[wid] = rec
        self._snapshots_by_ws[wid] = []
        return rec

    def snapshot(
        self,
        workspace_id: str,
        state: str,
        policy_ref: Optional[str] = None,
    ) -> SnapshotRecord:
        self._require_ws(workspace_id)
        # Fail-closed: cannot hash empty state (T078).
        if not state:
            raise ExecutionError("Cannot snapshot empty state (fail-closed, T078).")
        sid = f"sn-{uuid.uuid4().hex[:12]}"
        if sid in self._snapshots:
            raise ExecutionError(f"Duplicate snapshot_id '{sid}' (T001 Rule 1).")
        rec = SnapshotRecord(
            snapshot_id=sid,
            workspace_id=workspace_id,
            state_hash=_hash(state),
            restore_available=True,
            policy_ref=policy_ref,
            evidence_ref=f"ev-{uuid.uuid4().hex[:12]}",
        )
        self._snapshots[sid] = rec
        self._snapshots_by_ws[workspace_id].append(sid)
        return rec

    def restore(self, snapshot_id: str) -> str:
        """Roll back to a snapshot; returns the restored state hash.

        Fail-closed: if the snapshot is not restorable, raise (caller rolls back
        to the previous snapshot per T020/T066).
        """
        rec = self._snapshots.get(snapshot_id)
        if rec is None:
            raise ExecutionError(f"Unknown snapshot '{snapshot_id}'.")
        if not rec.restore_available:
            raise ExecutionError(f"Snapshot '{snapshot_id}' not restorable (T020/T066).")
        return rec.state_hash

    def archive(self, workspace_id: str) -> WorkspaceRecord:
        rec = self._require_ws(workspace_id)
        rec.status = WorkspaceStatus.ARCHIVED
        return rec

    def list_snapshots(self, workspace_id: str) -> List[SnapshotRecord]:
        self._require_ws(workspace_id)
        return [self._snapshots[s] for s in self._snapshots_by_ws[workspace_id]]

    def get(self, workspace_id: str) -> WorkspaceRecord:
        return self._require_ws(workspace_id)

    def _require_ws(self, workspace_id: str) -> WorkspaceRecord:
        if workspace_id not in self._workspaces:
            raise ExecutionError(f"Unknown workspace '{workspace_id}'.")
        return self._workspaces[workspace_id]

    def provenance(self, workspace_id: str) -> dict:
        rec = self._require_ws(workspace_id)
        payload = f"{rec.workspace_id}|{rec.status.value}|{rec.policy_ref}"
        return {
            "workspace_id": rec.workspace_id,
            "status": rec.status.value,
            "policy_ref": rec.policy_ref,
            "evidence_ref": rec.evidence_ref,
            "snapshot_count": len(self._snapshots_by_ws[workspace_id]),
            "content_hash": _hash(payload),
        }
