"""Tests for fail-closed config validation (TASK-065 hardening)."""

import pytest

from aios.core.config import Config
from aios.runtime.config_guard import (
    ConfigGuard,
    ConfigValidationError,
    require_valid_config,
    validate_config,
)


def test_valid_config_passes():
    cfg = Config()
    assert require_valid_config(cfg) is cfg
    assert validate_config(cfg) == []


def test_invalid_healthcheck_timeout():
    cfg = Config(healthcheck_timeout=999.0)
    with pytest.raises(ConfigValidationError):
        require_valid_config(cfg)


def test_invalid_metadata_ttl():
    cfg = Config(metadata_cache_ttl=10**9)
    with pytest.raises(ConfigValidationError):
        require_valid_config(cfg)


def test_invalid_config_dir():
    cfg = Config(config_dir="")
    with pytest.raises(ConfigValidationError):
        require_valid_config(cfg)


def test_config_guard_start_refuses():
    cfg = Config(healthcheck_timeout=999.0)
    guard = ConfigGuard(config=cfg)
    with pytest.raises(ConfigValidationError):
        guard.start()


def test_config_guard_on_invalid_callback():
    called = []
    cfg = Config(healthcheck_timeout=999.0)
    guard = ConfigGuard(config=cfg, on_invalid=lambda errs: called.append(errs))
    with pytest.raises(ConfigValidationError):
        guard.start()
    assert called
