"""File Safety Boundary + Scope Enforcement (TASK-134, M19).

Enforces that coder file operations stay within an allowed scope root. Any path
that escapes the root (path traversal, symlink escape, absolute escape) is
rejected fail-closed. This is the safety boundary that prevents the coder
subsystem from touching files outside its authorized workspace (T113 spirit /
security boundary). Provenance is recorded on every decision (T001 Rule 5).
"""

from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class ScopeStatus(str, Enum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"


class FileSafetyError(Exception):
    """Raised when a path violates the file safety boundary (fail-closed)."""


@dataclass
class ScopeDecision:
    decision_id: str
    requested_path: str
    resolved_path: str
    status: ScopeStatus
    reason: str
    evidence_id: str
    content_hash: str
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "requested_path": self.requested_path,
            "resolved_path": self.resolved_path,
            "status": self.status.value,
            "reason": self.reason,
            "evidence_id": self.evidence_id,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class FileSafetyBoundary:
    """Scope enforcement for coder file operations (T134)."""

    def __init__(self, scope_root: str) -> None:
        # Resolve to an absolute, normalized root; must exist.
        self._root = os.path.abspath(os.path.normpath(scope_root))
        if not os.path.isdir(self._root):
            raise FileSafetyError(f"scope root does not exist: {self._root}")

    @property
    def scope_root(self) -> str:
        return self._root

    def check(self, requested_path: str) -> ScopeDecision:
        """Resolve ``requested_path`` within the scope root.

        Fail-closed: any escape (absolute outside root, traversal, symlink
        escape) -> DENIED, never silently allowed. Provenance recorded (T001).
        """
        try:
            # Normalize and resolve symlinks to detect escapes.
            candidate = os.path.normpath(os.path.join(self._root, requested_path))
            resolved = os.path.realpath(candidate)
            root_resolved = os.path.realpath(self._root)
            if resolved != root_resolved and not resolved.startswith(root_resolved + os.sep):
                status = ScopeStatus.DENIED
                reason = f"path escapes scope root: {resolved}"
            else:
                status = ScopeStatus.ALLOWED
                reason = "within scope"
        except Exception as exc:
            resolved = ""
            status = ScopeStatus.DENIED
            reason = f"resolution error: {exc}"

        blob = f"{requested_path}:{resolved}:{status.value}"
        return ScopeDecision(
            decision_id=f"scope-{uuid.uuid4().hex[:12]}",
            requested_path=requested_path,
            resolved_path=resolved,
            status=status,
            reason=reason,
            evidence_id=f"ev-{uuid.uuid4().hex[:12]}",
            content_hash=_hash(blob),
            timestamp=_now(),
        )

    def require(self, requested_path: str) -> ScopeDecision:
        """Like ``check`` but raise on denial (fail-closed)."""
        decision = self.check(requested_path)
        if decision.status is ScopeStatus.DENIED:
            raise FileSafetyError(decision.reason)
        return decision
