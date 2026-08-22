"""SDK discovery — locates available AIOS endpoints/contracts for a client."""

from __future__ import annotations

from typing import Any

from aios.sdk.contracts import SDKConfig

KNOWN_ENDPOINTS: tuple[str, ...] = (
    "/health",
    "/system",
    "/executions",
    "/workflows",
    "/tasks",
    "/agents",
    "/capabilities",
    "/tools",
    "/skills",
    "/memory",
    "/artifacts",
    "/models",
    "/prompts",
    "/events",
)


def discover_endpoints(config: SDKConfig) -> list[str]:
    """Return the full list of API endpoints for a given SDK config."""
    base = config.base_url.rstrip("/")
    api = config.api_version
    return [f"{base}/api/{api}{ep}" for ep in KNOWN_ENDPOINTS]


def discover_contracts() -> dict[str, Any]:
    """Return the set of public contract names exposed by the SDK."""
    return {
        "client": "AIOSClient",
        "mock_client": "MockAIOSClient",
        "config": "SDKConfig",
        "response": "SDKResponse",
        "version": "SDKVersion",
        "errors": ["ValidationError", "NotFoundError", "AuthError", "RateLimitError", "TimeoutError"],
    }
