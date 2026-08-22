"""Ecosystem hub contracts."""
from __future__ import annotations
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Any

class HubStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"

@dataclass
class HubEntry:
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    version: str = "1.0.0"
    status: HubStatus = HubStatus.DRAFT
    author: str = ""
    downloads: int = 0
    capabilities: list[str] = field(default_factory=list)
    checksum: str = ""
    provenance: list[str] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "name": self.name,
            "version": self.version,
            "status": self.status.value,
            "downloads": self.downloads,
            "capabilities": self.capabilities,
            "checksum": self.checksum,
            "provenance": self.provenance,
        }
