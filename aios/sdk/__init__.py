"""AIOS Public SDK (M8 — TASK-043).

NOTE (audit 2026-08-22): The canonical detailtask (T043) also specifies a
TypeScript SDK. That is **deferred** — this package provides the Python SDK
(client, mock client, error model, versioning/compatibility, discovery). The
TypeScript SDK is out of scope for this implementation.
"""
from aios.sdk.client import AIOSClient
from aios.sdk.contracts import (
    AuthError,
    NotFoundError,
    RateLimitError,
    SDKConfig,
    SDKError,
    SDKResponse,
    SDKVersion,
    TimeoutError,
    ValidationError,
)
from aios.sdk.discovery import discover_contracts, discover_endpoints
from aios.sdk.mock_client import MockAIOSClient

__all__ = [
    "AIOSClient",
    "MockAIOSClient",
    "SDKConfig",
    "SDKResponse",
    "SDKError",
    "SDKVersion",
    "ValidationError",
    "NotFoundError",
    "AuthError",
    "RateLimitError",
    "TimeoutError",
    "discover_endpoints",
    "discover_contracts",
]
