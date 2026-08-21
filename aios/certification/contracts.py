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

@dataclass
class Certification:
    cert_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    target_id: str = ""
    status: CertStatus = CertStatus.PENDING
    issued_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    issuer: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"cert_id": self.cert_id, "target_id": self.target_id, "status": self.status.value}
