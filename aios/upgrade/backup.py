"""Backup engine — creates certified snapshots before migration.

AC-020-04: Backup/snapshot exists before migration.
AC-020-09: Certified state restored accurately.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BackupManifest:
    """Metadata for a backup snapshot."""

    backup_id: str
    version: str
    timestamp: float = field(default_factory=time.time)
    items: list[str] = field(default_factory=list)
    checksum: str = ""

    def compute_checksum(self) -> str:
        """Compute checksum of backup contents."""
        content = f"{self.backup_id}:{self.version}:{':'.join(self.items)}"
        self.checksum = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self.checksum

    def to_dict(self) -> dict[str, Any]:
        return {
            "backup_id": self.backup_id,
            "version": self.version,
            "timestamp": self.timestamp,
            "items": self.items,
            "checksum": self.checksum,
        }


class BackupEngine:
    """Creates and manages backup snapshots.

    Captures targeted state (not entire filesystem).
    """

    def __init__(self) -> None:
        self._backups: dict[str, BackupManifest] = {}
        self._backup_data: dict[str, dict[str, Any]] = {}
        self._counter: int = 0

    @property
    def backup_count(self) -> int:
        return len(self._backups)

    def create_backup(
        self,
        version: str,
        state: dict[str, Any],
        items: list[str] | None = None,
    ) -> BackupManifest:
        """Create a backup snapshot of the given state.

        AC-020-04: Backup exists before migration.
        """
        self._counter += 1
        backup_id = f"backup-{self._counter:04d}"
        manifest = BackupManifest(
            backup_id=backup_id,
            version=version,
            items=items or list(state.keys()),
        )
        manifest.compute_checksum()
        self._backups[backup_id] = manifest
        self._backup_data[backup_id] = dict(state)
        return manifest

    def get_backup(self, backup_id: str) -> BackupManifest | None:
        return self._backups.get(backup_id)

    def get_backup_data(self, backup_id: str) -> dict[str, Any] | None:
        """Get the backed-up state data."""
        data = self._backup_data.get(backup_id)
        return dict(data) if data is not None else None

    def restore_backup(self, backup_id: str) -> dict[str, Any] | None:
        """Restore state from a backup.

        AC-020-09: Certified state restored accurately.
        """
        return self.get_backup_data(backup_id)

    def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity."""
        manifest = self._backups.get(backup_id)
        if manifest is None:
            return False
        data = self._backup_data.get(backup_id)
        if data is None:
            return False
        # Verify items exist in data
        return all(item in data for item in manifest.items)

    def list_backups(self) -> list[BackupManifest]:
        return list(self._backups.values())

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup."""
        if backup_id in self._backups:
            del self._backups[backup_id]
            self._backup_data.pop(backup_id, None)
            return True
        return False
