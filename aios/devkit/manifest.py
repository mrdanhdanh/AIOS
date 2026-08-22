"""DevKit manifest — schema + validation for extensions/projects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DevKitManifest:
    """Manifest describing an extension/project scaffolded by the DevKit."""
    name: str = ""
    version: str = "1.0.0"
    author: str = ""
    entrypoint: str = ""
    dependencies: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "entrypoint": self.entrypoint,
            "dependencies": self.dependencies,
            "capabilities": self.capabilities,
        }

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.name:
            errors.append("name is required")
        if not self.version:
            errors.append("version is required")
        if not self.entrypoint:
            errors.append("entrypoint is required")
        return errors
