"""Resume protocol (TASK-066).

Fail-closed: resume ONLY from the most recent *verified* checkpoint. Never
resume from an unverified checkpoint -- raise instead. This guarantees a
crashed / unverified tail is never replayed as if it had succeeded.

Layering: ``durable`` is a runtime-level durability concern; it imports no
peer packages directly.
"""

from __future__ import annotations

from .checkpoint import Checkpoint
from .store import CheckpointStore


class ResumeError(Exception):
    """Raised when resume is attempted but cannot proceed (fail-closed)."""


class ResumeProtocol:
    """Resumes an execution from its most recent verified checkpoint."""

    def __init__(self, store: CheckpointStore) -> None:
        self._store = store

    def resume(self, execution_id: str) -> Checkpoint:
        """Return the most recent verified checkpoint for ``execution_id``.

        Fail-closed: raises :class:`ResumeError` if there are no checkpoints
        at all, or if none of them are verified (never resume from an
        unverified checkpoint).
        """
        checkpoints = self._store.load(execution_id)
        if not checkpoints:
            raise ResumeError(
                f"Fail-closed: no checkpoints available for {execution_id!r}"
            )
        verified = [c for c in checkpoints if c.verified]
        if not verified:
            raise ResumeError(
                f"Fail-closed: no verified checkpoint for {execution_id!r}; "
                f"refusing to resume from unverified state"
            )
        # Most recent verified checkpoint (deterministic tie-break).
        return max(verified, key=lambda c: (c.created_at, c.checkpoint_id))

    def can_resume(self, execution_id: str) -> bool:
        """Non-raising probe: is a verified checkpoint available to resume?"""
        try:
            self.resume(execution_id)
            return True
        except ResumeError:
            return False
