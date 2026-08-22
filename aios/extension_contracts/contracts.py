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

@dataclass
class ExtensionContext:
    """Runtime context an extension executes within (public contract only)."""
    tenant_id: str = ""
    scope: str = "public"
    runtime_version: str = "1.0.0"
    allowed_internal_access: bool = False
    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "scope": self.scope,
            "runtime_version": self.runtime_version,
            "allowed_internal_access": self.allowed_internal_access,
        }

@dataclass
class ExtensionError:
    """Structured error contract for extensions."""
    code: str = ""
    message: str = ""
    extension_id: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "extension_id": self.extension_id}

@dataclass
class ExtensionEvidence:
    """Evidence contract linking an extension action to its provenance."""
    evidence_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    extension_id: str = ""
    action: str = ""
    provenance: list[str] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "extension_id": self.extension_id,
            "action": self.action,
            "provenance": self.provenance,
        }
