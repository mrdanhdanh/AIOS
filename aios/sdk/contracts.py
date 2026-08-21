"""SDK contracts."""
from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class SDKError(Exception): pass

class ErrorCode(str, Enum):
    VALIDATION_ERROR = "validation_error"
    AUTH_ERROR = "auth_error"
    NOT_FOUND = "not_found"
    INTERNAL_ERROR = "internal_error"

@dataclass
class SDKConfig:
    base_url: str = "http://localhost:8000"
    api_version: str = "v1"
    sdk_version: str = "1.0.0"
    timeout_seconds: float = 30.0
    tenant_id: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"base_url": self.base_url, "api_version": self.api_version, "sdk_version": self.sdk_version}

@dataclass
class SDKResponse:
    success: bool = True
    data: Any = None
    error_code: ErrorCode | None = None
    error_message: str = ""
    request_id: str = ""
    timestamp: float = field(default_factory=time.time)
    provenance: list = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {"success": self.success, "error_message": self.error_message, "request_id": self.request_id}
