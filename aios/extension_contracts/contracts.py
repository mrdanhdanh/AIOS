"""Extension contracts."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Any

@dataclass
class CapabilityExport:
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "version": self.version}

@dataclass
class ExtensionSpec:
    spec_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    version: str = "1.0.0"
    capabilities: list = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {"spec_id": self.spec_id, "name": self.name, "version": self.version}

@dataclass
class ExtensionManifest:
    manifest_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    extension: ExtensionSpec | None = None
    author: str = ""
    license: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"manifest_id": self.manifest_id, "author": self.author}
