"""Security contracts."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class CredentialType(Enum):
    API_KEY = "api_key"
    TOKEN = "token"
    PASSWORD = "password"

@dataclass
class Credential:
    cred_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    cred_type: CredentialType = CredentialType.API_KEY
    value: str = ""
    expires_at: float = 0.0
    def is_valid(self) -> bool: return bool(self.value)
    def to_dict(self) -> dict[str, Any]:
        return {"cred_id": self.cred_id, "cred_type": self.cred_type.value, "expires_at": self.expires_at}

@dataclass
class NetworkPolicy:
    policy_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    rules: list = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {"policy_id": self.policy_id, "name": self.name, "rules": self.rules}

@dataclass
class SandboxConfig:
    sandbox_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    isolation_level: str = "process"
    network_access: bool = False
    filesystem_access: bool = False
    def to_dict(self) -> dict[str, Any]:
        return {"sandbox_id": self.sandbox_id, "isolation_level": self.isolation_level}
