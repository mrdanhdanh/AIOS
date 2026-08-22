"""Mock AIOS client — in-memory implementation of the SDK interface for tests/offline."""

from __future__ import annotations

import uuid

from aios.sdk.client import AIOSClient
from aios.sdk.contracts import SDKConfig, SDKResponse


class MockAIOSClient(AIOSClient):
    """In-memory client implementing the same interface as AIOSClient."""

    def __init__(self, config: SDKConfig | None = None) -> None:
        super().__init__(config)
        self._store: dict[str, Any] = {}
        self._executed: list[str] = []

    def health(self) -> SDKResponse:
        return SDKResponse(success=True, data={"status": "ok"}, request_id=uuid.uuid4().hex[:8])

    def execute(self, intent: str, **kwargs) -> SDKResponse:
        self._executed.append(intent)
        self._store[intent] = kwargs
        return SDKResponse(
            success=True,
            data={"intent": intent, "kwargs": kwargs},
            request_id=uuid.uuid4().hex[:8],
            provenance=[f"mock_sdk:{intent}"],
        )

    def list_resources(self, resource_type: str = "") -> SDKResponse:
        return SDKResponse(success=True, data=[], request_id=uuid.uuid4().hex[:8])

    def executed_intents(self) -> list[str]:
        return list(self._executed)
