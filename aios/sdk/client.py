"""AIOSClient — public SDK client."""
from __future__ import annotations
import uuid
from aios.sdk.contracts import SDKConfig, SDKResponse

class AIOSClient:
    def __init__(self, config: SDKConfig | None = None) -> None:
        self._config = config or SDKConfig()
    @property
    def config(self) -> SDKConfig: return self._config
    def health(self) -> SDKResponse:
        return SDKResponse(success=True, data={"status": "ok"}, request_id=uuid.uuid4().hex[:8])
    def execute(self, intent: str, **kwargs) -> SDKResponse:
        return SDKResponse(success=True, data={"intent": intent}, request_id=uuid.uuid4().hex[:8], provenance=[f"sdk:{intent}"])
    def list_resources(self, resource_type: str = "") -> SDKResponse:
        return SDKResponse(success=True, data=[], request_id=uuid.uuid4().hex[:8])
    def to_dict(self) -> dict: return self._config.to_dict()
