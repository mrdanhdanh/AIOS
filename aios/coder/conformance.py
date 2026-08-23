"""Coder Conformance Harness + Security (TASK-131, M19).

A conformance harness that validates coder-pipeline artifacts/plans/reports
against the M19 invariants (hash present, provenance chain, integrity verified,
deterministic). The verdict is fail-closed: UNKNOWN is never promoted to PASS.
A security boundary rejects artifacts that carry forbidden operations or an
unauthorized producer.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class ConformanceStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class SecurityStatus(str, Enum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"


class ConformanceError(Exception):
    """Raised on conformance/security contract violations."""


@dataclass
class ConformanceResult:
    check_id: str
    status: ConformanceStatus
    producer: str
    security: SecurityStatus
    reasons: List[str]
    content_hash: str
    evidence_id: str
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "status": self.status.value,
            "producer": self.producer,
            "security": self.security.value,
            "reasons": self.reasons,
            "content_hash": self.content_hash,
            "evidence_id": self.evidence_id,
            "timestamp": self.timestamp,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# Forbidden operations a coder artifact must never carry (security boundary).
_FORBIDDEN_OPS = [
    (r"\bimport subprocess\b", "no-subprocess"),
    (r"\bos\.system\s*\(", "no-os-system"),
    (r"\brm\s+-rf\b", "no-rm-rf"),
]


class CoderConformanceHarness:
    """Validates coder artifacts/plans/reports against M19 invariants (T131)."""

    def __init__(self, authorized_producers: Optional[set] = None) -> None:
        self._authorized = authorized_producers or {"coder-1", "reviewer-1", "patch-1"}

    def check(
        self,
        content: str,
        content_hash: str,
        producer: str,
        evidence_present: bool,
        integrity_verified: bool,
    ) -> ConformanceResult:
        """Run conformance + security checks.

        Fail-closed: any missing invariant -> FAIL; UNKNOWN is never promoted to
        PASS. Security: unauthorized producer or forbidden op -> DENIED.
        """
        reasons: List[str] = []
        status = ConformanceStatus.PASS
        security = SecurityStatus.ALLOWED

        if producer not in self._authorized:
            security = SecurityStatus.DENIED
            reasons.append(f"unauthorized producer: {producer}")
        for pattern, rule in _FORBIDDEN_OPS:
            if re.search(pattern, content):
                security = SecurityStatus.DENIED
                reasons.append(f"forbidden op: {rule}")
        if _hash(content) != content_hash:
            status = ConformanceStatus.FAIL
            reasons.append("content_hash mismatch")
        if not evidence_present:
            status = ConformanceStatus.FAIL
            reasons.append("missing provenance (T001 Rule 5)")
        if not integrity_verified:
            status = ConformanceStatus.FAIL
            reasons.append("integrity not verified (T078)")

        # Fail-closed: security denial forces FAIL; UNKNOWN never -> PASS.
        if security is SecurityStatus.DENIED:
            status = ConformanceStatus.FAIL

        return ConformanceResult(
            check_id=f"conf-{uuid.uuid4().hex[:12]}",
            status=status,
            producer=producer,
            security=security,
            reasons=reasons,
            content_hash=content_hash,
            evidence_id=f"ev-{uuid.uuid4().hex[:12]}",
            timestamp=_now(),
        )

    @staticmethod
    def promote(status: ConformanceStatus) -> bool:
        """UNKNOWN is never promoted to PASS (fail-closed, T078)."""
        return status is ConformanceStatus.PASS
