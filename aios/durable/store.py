"""Durable checkpoint store (TASK-066).

Persists :class:`Checkpoint` objects across process restarts using an
in-memory index plus an optional JSON file backend. Designed to be simple and
deterministic -- no external dependencies, no parallel execution store (it
reuses runtime state-store concepts from T065; the runtime ``StateStore``
remains the source of truth for live execution state).

Layering: ``durable`` is a runtime-level durability concern; it imports no
peer packages directly.
"""

from __future__ import annotations

import json
import os
import threading
from typing import Dict, List, Optional

from .checkpoint import Checkpoint


class CheckpointStore:
    """Thread-safe durable store of checkpoints keyed by execution id."""

    def __init__(self, path: Optional[str] = None) -> None:
        self._path = path
        self._store: Dict[str, List[Checkpoint]] = {}
        self._lock = threading.RLock()
        if path:
            self._load_file()

    # -- write ---------------------------------------------------------- #
    def save(self, checkpoint: Checkpoint) -> None:
        if not isinstance(checkpoint, Checkpoint):
            raise TypeError("CheckpointStore only holds Checkpoint instances")
        with self._lock:
            self._store.setdefault(checkpoint.execution_id, []).append(checkpoint)
            if self._path:
                self._persist()

    # -- read ----------------------------------------------------------- #
    def load(self, execution_id: str) -> List[Checkpoint]:
        with self._lock:
            return list(self._store.get(execution_id, []))

    def load_latest(self, execution_id: str) -> Optional[Checkpoint]:
        checkpoints = self.load(execution_id)
        if not checkpoints:
            return None
        return max(checkpoints, key=lambda c: (c.created_at, c.checkpoint_id))

    def load_latest_verified(self, execution_id: str) -> Optional[Checkpoint]:
        verified = [c for c in self.load(execution_id) if c.verified]
        if not verified:
            return None
        return max(verified, key=lambda c: (c.created_at, c.checkpoint_id))

    def exists(self, execution_id: str) -> bool:
        with self._lock:
            return execution_id in self._store

    def __len__(self) -> int:
        with self._lock:
            return sum(len(v) for v in self._store.values())

    # -- persistence ---------------------------------------------------- #
    def _persist(self) -> None:
        assert self._path is not None
        data = [c.to_dict() for cps in self._store.values() for c in cps]
        # Deterministic ordering for stable, reproducible file output.
        data.sort(key=lambda d: (d["created_at"], d["checkpoint_id"]))
        tmp = f"{self._path}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, sort_keys=True, indent=2)
        os.replace(tmp, self._path)

    def _load_file(self) -> None:
        assert self._path is not None
        if not os.path.exists(self._path):
            return
        with open(self._path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        with self._lock:
            self._store.clear()
            for d in data:
                cp = Checkpoint.from_dict(d)
                self._store.setdefault(cp.execution_id, []).append(cp)
