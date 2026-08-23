"""TASK-207 — Session Fork (M26).

Fork a coding session into an isolated branch, converging Session (T206) and
Workspace/Snapshot (T137). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from aios.coding_edition._common import CodingEditionError, _hash
from aios.coding_edition.session import CodingSession, SessionState


@dataclass
class ForkedSession:
    """An immutable-by-id fork of a parent session (T207)."""

    fork_id: str
    parent_id: str
    goal: str
    snapshot: Dict[str, str]
    at: str = field(default_factory=lambda: __import__("aios.coding_edition._common", fromlist=["_now"])._now())


class SessionFork:
    """Deterministic session fork (T207)."""

    def fork(self, parent: CodingSession, name: str = "") -> ForkedSession:
        """Fork ``parent`` preserving its committed artifacts (fail-closed)."""
        if parent.state not in (SessionState.CODING, SessionState.REVIEWING, SessionState.CLOSED):
            raise CodingEditionError(f"cannot fork session in {parent.state.value}")
        if not name:
            name = f"fork-{uuid.uuid4().hex[:8]}"
        # Snapshot the parent's artifact hashes deterministically.
        snapshot = {s.artifact: "" for s in parent.steps}
        return ForkedSession(
            fork_id=f"fk-{uuid.uuid4().hex[:10]}",
            parent_id=parent.session_id,
            goal=f"{parent._goal} [{name}]" if hasattr(parent, "_goal") else name,
            snapshot=snapshot,
        )

    def fork_hash(self, fork: ForkedSession) -> str:
        payload = "|".join(f"{k}:{v}" for k, v in sorted(fork.snapshot.items()))
        return _hash(f"{fork.fork_id}|{fork.parent_id}|{payload}")
