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

@dataclass
class RegistryEntry:
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    version: str = "1.0.0"
    status: RegistryStatus = RegistryStatus.PENDING
    author: str = ""
    description: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"entry_id": self.entry_id, "name": self.name, "status": self.status.value}
