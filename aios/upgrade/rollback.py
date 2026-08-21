"""Rollback engine — restores certified state on migration failure.

AC-020-08: Migration failure auto-rollback per policy.
AC-020-09: Certified state restored accurately.
AC-020-11: Evidence for rollback events.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from aios.upgrade.backup import BackupEngine, BackupManifest


class RollbackStatus(str, Enum):
    """Status of a rollback operation."""
    NOT_NEEDED = "not_needed"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class RollbackResult:
    """Result of a rollback operation."""

    backup_id: str
    status: RollbackStatus
    restored_keys: list[str] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "backup_id": self.backup_id,
            "status": self.status.value,
            "restored_keys": self.restored_keys,
            "evidence": self.evidence,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


class RollbackEngine:
    """Restores state from a backup after migration failure.

    AC-020-08: Auto-rollback when migration fails.
    AC-020-09: Certified state restored accurately.
    """

    def __init__(self, backup_engine: BackupEngine) -> None:
        self._backup_engine = backup_engine

    def rollback(
        self,
        backup_id: str,
        target_state: dict[str, Any] | None = None,
    ) -> RollbackResult:
        """Rollback to a specific backup.

        Restores the backed-up state into target_state (if provided).
        """
        start_time = time.time()

        backup = self._backup_engine.get_backup(backup_id)
        if backup is None:
            return RollbackResult(
                backup_id=backup_id,
                status=RollbackStatus.FAILED,
                error=f"Backup {backup_id} not found",
                duration_ms=(time.time() - start_time) * 1000,
            )

        data = self._backup_engine.restore_backup(backup_id)
        if data is None:
            return RollbackResult(
                backup_id=backup_id,
                status=RollbackStatus.FAILED,
                error=f"Could not restore data from {backup_id}",
                duration_ms=(time.time() - start_time) * 1000,
            )

        # Restore data to target
        restored_keys = list(data.keys())
        if target_state is not None:
            target_state.clear()
            target_state.update(data)

        # Create evidence
        evidence = [{
            "event": "rollback",
            "backup_id": backup_id,
            "restored_keys": restored_keys,
            "timestamp": time.time(),
        }]

        return RollbackResult(
            backup_id=backup_id,
            status=RollbackStatus.SUCCESS,
            restored_keys=restored_keys,
            evidence=evidence,
            duration_ms=(time.time() - start_time) * 1000,
        )

    def auto_rollback(
        self,
        backup_id: str,
        migration_failed: bool,
        target_state: dict[str, Any] | None = None,
    ) -> RollbackResult:
        """Auto-rollback only if migration failed.

        AC-020-08: Migration failure auto-rollback per policy.
        """
        if not migration_failed:
            return RollbackResult(
                backup_id=backup_id,
                status=RollbackStatus.NOT_NEEDED,
            )
        return self.rollback(backup_id, target_state)
