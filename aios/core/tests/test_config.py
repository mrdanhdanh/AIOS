"""Tests for :mod:`aios.core.config`."""

from __future__ import annotations

import os

import pytest

from aios.core.config import Config, ConfigError


class TestConfigDefaults:
    """Verify default configuration values."""

    def test_default_log_level(self):
        cfg = Config()
        assert cfg.log_level == "INFO"

    def test_default_log_format(self):
        cfg = Config()
        assert cfg.log_format == "json"

    def test_default_healthcheck_timeout(self):
        cfg = Config()
        assert cfg.healthcheck_timeout == 5.0

    def test_default_dry_run(self):
        cfg = Config()
        assert cfg.dry_run is False


class TestConfigEnvOverride:
    """Verify environment-variable overrides."""

    def test_log_level_override(self, monkeypatch):
        monkeypatch.setenv("AIOS_LOG_LEVEL", "DEBUG")
        cfg = Config()
        assert cfg.log_level == "DEBUG"

    def test_log_format_override(self, monkeypatch):
        monkeypatch.setenv("AIOS_LOG_FORMAT", "text")
        cfg = Config()
        assert cfg.log_format == "text"

    def test_dry_run_override(self, monkeypatch):
        monkeypatch.setenv("AIOS_DRY_RUN", "true")
        cfg = Config()
        assert cfg.dry_run is True


class TestConfigValidation:
    """Verify fail-closed validation on invalid values."""

    def test_invalid_log_level_raises(self, monkeypatch):
        monkeypatch.setenv("AIOS_LOG_LEVEL", "NOT_A_LEVEL")
        with pytest.raises(ConfigError, match="Invalid log level"):
            Config()

    def test_invalid_log_format_raises(self, monkeypatch):
        monkeypatch.setenv("AIOS_LOG_FORMAT", "xml")
        with pytest.raises(ConfigError, match="Invalid log format"):
            Config()

    def test_invalid_timeout_raises(self, monkeypatch):
        monkeypatch.setenv("AIOS_HEALTHCHECK_TIMEOUT", "-1")
        with pytest.raises(ConfigError, match="must be positive"):
            Config()

    def test_invalid_int_env_raises(self, monkeypatch):
        monkeypatch.setenv("AIOS_METADATA_CACHE_TTL", "not_a_number")
        with pytest.raises(ConfigError, match="must be an integer"):
            Config()


class TestConfigHelpers:
    """Verify convenience methods."""

    def test_get_existing_key(self):
        cfg = Config()
        assert cfg.get("log_level") == "INFO"

    def test_get_missing_key_returns_default(self):
        cfg = Config()
        assert cfg.get("nonexistent", "fallback") == "fallback"

    def test_as_dict_returns_expected_keys(self):
        cfg = Config()
        d = cfg.as_dict()
        assert set(d.keys()) == {
            "log_level",
            "log_format",
            "config_dir",
            "healthcheck_timeout",
            "metadata_cache_ttl",
            "dry_run",
        }
