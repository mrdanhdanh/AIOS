"""API contracts & versioning (TASK-017).

Layering: ``api`` layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from aios.core.version import SemVer, VersionError

CURRENT_API_VERSION = "1.0.0"
SUPPORTED_VERSIONS = ["1.0.0"]
API_PREFIX = "/api/v1"


@dataclass
class ApiVersion:
    version: str = CURRENT_API_VERSION

    def __post_init__(self) -> None:
        self.semver = SemVer.parse(self.version)

    def is_compatible(self, required: str) -> bool:
        try:
            req = SemVer.parse(required)
        except VersionError:
            return False
        return self.semver.major == req.major

    def __str__(self) -> str:
        return self.version


@dataclass
class ApiContract:
    endpoint: str
    method: str
    version: str = CURRENT_API_VERSION
    description: str = ""
    deprecated: bool = False


def negotiate_version(requested: Optional[str], supported: Optional[List[str]] = None) -> ApiVersion:
    supported = supported or SUPPORTED_VERSIONS
    if not requested:
        return ApiVersion(CURRENT_API_VERSION)
    req = requested.strip()
    if "version=" in req:
        for part in req.split(";"):
            part = part.strip()
            if part.startswith("version="):
                req = part.split("=", 1)[1].strip().strip('"').strip("'")
                break
    if req in supported:
        return ApiVersion(req)
    try:
        req_sv = SemVer.parse(req)
        for sv in supported:
            if SemVer.parse(sv).major == req_sv.major:
                return ApiVersion(sv)
    except VersionError:
        pass
    raise ValueError(f"Unsupported API version {requested!r}; supported: {supported}")
