"""Ecosystem registry contracts."""
from __future__ import annotations
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Any

class RegistryStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RETIRED = "retired"

class TrustState(Enum):
    UNVERIFIED = "unverified"
    CERTIFIED = "certified"
    EXPIRED = "expired"
    REVOKED = "revoked"

@dataclass
class RegistryEntry:
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    version: str = "1.0.0"
    status: RegistryStatus = RegistryStatus.PENDING
    trust: TrustState = TrustState.UNVERIFIED
    author: str = ""
    description: str = ""
    capabilities: list[str] = field(default_factory=list)
    entry_type: str = "extension"
    platform: str = "any"
    checksum: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "name": self.name,
            "version": self.version,
            "status": self.status.value,
            "trust": self.trust.value,
            "capabilities": self.capabilities,
            "entry_type": self.entry_type,
            "platform": self.platform,
            "checksum": self.checksum,
        }
