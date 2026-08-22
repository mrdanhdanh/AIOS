"""SDK contracts."""
from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class SDKError(Exception):
    """Base SDK error with code + message + optional details."""
    code: str = "sdk_error"

    def __init__(self, message: str = "", details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class ValidationError(SDKError):
    code = "validation_error"


class NotFoundError(SDKError):
    code = "not_found"


class AuthError(SDKError):
    code = "auth_error"


class RateLimitError(SDKError):
    code = "rate_limit"


class TimeoutError(SDKError):
    code = "timeout"


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "validation_error"
    AUTH_ERROR = "auth_error"
    NOT_FOUND = "not_found"
    INTERNAL_ERROR = "internal_error"


@dataclass
class SDKVersion:
    """Semantic version with compatibility check (fail-closed)."""
    major: int = 1
    minor: int = 0
    patch: int = 0

    @classmethod
    def parse(cls, version: str) -> "SDKVersion":
        parts = version.split(".")
        nums = [int(p.split("-")[0]) for p in parts[:3]]
        while len(nums) < 3:
            nums.append(0)
        return cls(major=nums[0], minor=nums[1], patch=nums[2])

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_compatible_with(self, contract_version: "SDKVersion") -> bool:
        """Compatible if major matches and SDK minor >= contract minor."""
        if self.major != contract_version.major:
            return False
        if self.minor < contract_version.minor:
            return False
        return True


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
