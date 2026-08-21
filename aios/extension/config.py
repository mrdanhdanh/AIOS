"""Extension configuration schema.

AC-019-08: Configuration supports offline/deterministic mode.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtensionConfig:
    """Configuration for the VS Code extension.

    Versioned and serializable for stable extension behavior.
    """

    version: str = "1.0.0"
    api_base_url: str = "http://localhost:8000"
    ws_url: str = "ws://localhost:8000/api/v1/ws/events"
    timeout_seconds: float = 30.0
    reconnect_attempts: int = 3
    reconnect_delay_seconds: float = 1.0
    offline_mode: bool = False
    mock_backend: bool = False
    log_level: str = "info"
    enabled_commands: list[str] = field(default_factory=lambda: [
        "aios.chat",
        "aios.explain",
        "aios.fixSelection",
        "aios.generateTest",
        "aios.reviewPR",
        "aios.refactor",
        "aios.rename",
        "aios.askWorkspace",
        "aios.chatWithRepository",
    ])

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "api_base_url": self.api_base_url,
            "ws_url": self.ws_url,
            "timeout_seconds": self.timeout_seconds,
            "reconnect_attempts": self.reconnect_attempts,
            "reconnect_delay_seconds": self.reconnect_delay_seconds,
            "offline_mode": self.offline_mode,
            "mock_backend": self.mock_backend,
            "log_level": self.log_level,
            "enabled_commands": self.enabled_commands,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExtensionConfig:
        """Create config from dictionary."""
        return cls(
            version=data.get("version", "1.0.0"),
            api_base_url=data.get("api_base_url", "http://localhost:8000"),
            ws_url=data.get("ws_url", "ws://localhost:8000/api/v1/ws/events"),
            timeout_seconds=data.get("timeout_seconds", 30.0),
            reconnect_attempts=data.get("reconnect_attempts", 3),
            reconnect_delay_seconds=data.get("reconnect_delay_seconds", 1.0),
            offline_mode=data.get("offline_mode", False),
            mock_backend=data.get("mock_backend", False),
            log_level=data.get("log_level", "info"),
            enabled_commands=data.get("enabled_commands", [
                "aios.chat", "aios.explain", "aios.fixSelection",
                "aios.generateTest", "aios.reviewPR", "aios.refactor",
                "aios.rename", "aios.askWorkspace", "aios.chatWithRepository",
            ]),
        )

    def is_command_enabled(self, command_id: str) -> bool:
        """Check if a command is enabled."""
        return command_id in self.enabled_commands

    def enable_command(self, command_id: str) -> None:
        """Enable a command."""
        if command_id not in self.enabled_commands:
            self.enabled_commands.append(command_id)

    def disable_command(self, command_id: str) -> None:
        """Disable a command."""
        if command_id in self.enabled_commands:
            self.enabled_commands.remove(command_id)
