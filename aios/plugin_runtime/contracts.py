"""Plugin runtime contracts."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class PluginState(Enum):
    REGISTERED = "registered"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"

@dataclass
class PluginSpec:
    plugin_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    version: str = "1.0.0"
    state: PluginState = PluginState.REGISTERED
    capabilities: list = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {"plugin_id": self.plugin_id, "name": self.name, "state": self.state.value}
