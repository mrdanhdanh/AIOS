"""Certification contracts."""
from __future__ import annotations
import uuid
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Any

class CertStatus(Enum):
    PENDING = "pending"
    CERTIFIED = "certified"
    REVOKED = "revoked"
    EXPIRED = "expired"

class RevocationReason(str, Enum):
    SECURITY = "security"
    POLICY = "policy"
    DEPRECATED = "deprecated"
    MANUAL = "manual"

@dataclass
class CertCheck:
    """A single certification check."""
    name: str = ""
    passed: bool = False
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


@dataclass
class CertProfile:
    """A named set of checks a target must pass to be certified."""
    profile_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    checks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"profile_id": self.profile_id, "name": self.name, "checks": self.checks}


@dataclass
class Certification:
    cert_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    target_id: str = ""
    status: CertStatus = CertStatus.PENDING
    issued_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    issuer: str = ""
    profile_id: str = ""
    evidence: list[str] = field(default_factory=list)
    signature: str = ""
    revocation_reason: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {
            "cert_id": self.cert_id,
            "target_id": self.target_id,
            "status": self.status.value,
            "profile_id": self.profile_id,
            "evidence": self.evidence,
            "signature": self.signature,
            "revocation_reason": self.revocation_reason,
        }
