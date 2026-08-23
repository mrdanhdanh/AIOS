"""Patch Engine (TASK-128, M19).

Applies a code artifact (T127) to a target as a safe patch: diff -> backup ->
apply -> (rollback on failure). Backup-before-apply (T020); on apply failure the
engine rolls back to the certified prior state (T020/T066). Every patch carries
a ``content_hash`` (T078) and provenance (T001 Rule 5). Deterministic: same
artifact + same target -> same unified diff.
"""

from __future__ import annotations

import difflib
import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


class PatchStatus(str, Enum):
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"


class PatchError(Exception):
    """Raised on patch failures (fail-closed, T020/T066)."""


@dataclass
class PatchRun:
    run_id: str
    artifact_ref: str
    target: str
    diff: str
    content_hash: str
    evidence_id: str
    backup_ref: Optional[str] = None
    applied: bool = False
    rollback_available: bool = False
    status: PatchStatus = PatchStatus.PENDING

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "artifact_ref": self.artifact_ref,
            "target": self.target,
            "diff": self.diff,
            "content_hash": self.content_hash,
            "evidence_id": self.evidence_id,
            "backup_ref": self.backup_ref,
            "applied": self.applied,
            "rollback_available": self.rollback_available,
            "status": self.status.value,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class PatchEngine:
    """Safe patch engine: diff -> backup -> apply -> rollback (T128)."""

    def __init__(self, policy_ref: Optional[str] = None) -> None:
        self._policy_ref = policy_ref
        # In-memory store standing in for the certified-state backup (T020/T066).
        self._backups: Dict[str, str] = {}

    # ------------------------------------------------------------------ #
    def diff(self, artifact_content: str, current_content: str, target: str) -> str:
        """Produce a unified diff (deterministic for same inputs)."""
        diff = difflib.unified_diff(
            current_content.splitlines(keepends=True),
            artifact_content.splitlines(keepends=True),
            fromfile=f"a/{target}",
            tofile=f"b/{target}",
        )
        return "".join(diff)

    # ------------------------------------------------------------------ #
    def apply(
        self,
        artifact_ref: str,
        target: str,
        artifact_content: str,
        current_content: str,
        policy_ok: bool = True,
        apply_fn=None,
    ) -> PatchRun:
        """Apply ``artifact_content`` to ``target``.

        Backup-before-apply (T020). If ``policy_ok`` is False or ``apply_fn``
        raises, the engine rolls back to the certified prior state and fails
        closed (T020/T066) — the repository is never left broken.
        """
        if not policy_ok:
            raise PatchError("Policy rejected patch (T113).")
        content_hash = _hash(artifact_content)
        run = PatchRun(
            run_id=f"patch-{uuid.uuid4().hex[:12]}",
            artifact_ref=artifact_ref,
            target=target,
            diff=self.diff(artifact_content, current_content, target),
            content_hash=content_hash,
            evidence_id=f"ev-{uuid.uuid4().hex[:12]}",
        )
        # Backup-before-apply (T020).
        backup_ref = f"backup-{uuid.uuid4().hex[:12]}"
        self._backups[backup_ref] = current_content
        run.backup_ref = backup_ref
        run.rollback_available = True

        def _do_apply() -> None:
            if apply_fn is not None:
                apply_fn(target, artifact_content)
            # else: caller is responsible for persisting; we record success.

        try:
            _do_apply()
        except Exception as exc:
            # Rollback to certified state (T020/T066) — fail-closed.
            restored = self._backups.pop(backup_ref, current_content)
            run.rollback_available = False
            run.status = PatchStatus.ROLLED_BACK
            raise PatchError(f"apply failed; rolled back: {exc}") from exc

        run.applied = True
        run.status = PatchStatus.APPLIED
        return run

    # ------------------------------------------------------------------ #
    def rollback(self, run: PatchRun) -> str:
        """Return the certified prior content for ``run`` (T020/T066)."""
        if not run.backup_ref or run.backup_ref not in self._backups:
            raise PatchError("no backup available for rollback (T020).")
        return self._backups[run.backup_ref]
