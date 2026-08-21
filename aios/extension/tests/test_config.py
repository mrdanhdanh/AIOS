"""Tests for extension configuration."""

from __future__ import annotations

import pytest

from aios.extension.config import ExtensionConfig


class TestExtensionConfig:
    def test_default(self) -> None:
        cfg = ExtensionConfig()
        assert cfg.version == "1.0.0"
        assert cfg.offline_mode is False
        assert cfg.mock_backend is False

    def test_to_dict(self) -> None:
        cfg = ExtensionConfig()
        d = cfg.to_dict()
        assert d["version"] == "1.0.0"
        assert "enabled_commands" in d

    def test_from_dict(self) -> None:
        data = {"version": "2.0.0", "offline_mode": True}
        cfg = ExtensionConfig.from_dict(data)
        assert cfg.version == "2.0.0"
        assert cfg.offline_mode is True

    def test_from_dict_defaults(self) -> None:
        cfg = ExtensionConfig.from_dict({})
        assert cfg.version == "1.0.0"
        assert cfg.api_base_url == "http://localhost:8000"

    def test_is_command_enabled(self) -> None:
        cfg = ExtensionConfig()
        assert cfg.is_command_enabled("aios.chat") is True
        assert cfg.is_command_enabled("aios.nonexistent") is False

    def test_enable_command(self) -> None:
        cfg = ExtensionConfig()
        cfg.enable_command("custom.cmd")
        assert cfg.is_command_enabled("custom.cmd") is True

    def test_enable_command_dedup(self) -> None:
        cfg = ExtensionConfig()
        cfg.enable_command("aios.chat")
        assert cfg.enabled_commands.count("aios.chat") == 1

    def test_disable_command(self) -> None:
        cfg = ExtensionConfig()
        cfg.disable_command("aios.chat")
        assert cfg.is_command_enabled("aios.chat") is False

    def test_roundtrip(self) -> None:
        cfg = ExtensionConfig(offline_mode=True)
        d = cfg.to_dict()
        cfg2 = ExtensionConfig.from_dict(d)
        assert cfg2.offline_mode is True
