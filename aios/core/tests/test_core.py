"""Tests for the aios_core scaffold (M1 bootstrap)."""
from aios.core import (
    CORE_METADATA,
    RuntimeConfig,
    configure_logging,
    healthcheck,
    __version__,
    __milestone__,
)


def test_version_metadata():
    assert __version__ == "0.1.0"
    assert __milestone__ == "M1"
    assert CORE_METADATA["name"] == "aios_core"
    assert CORE_METADATA["runtime_first"] is True


def test_configure_logging_returns_logger():
    logger = configure_logging()
    assert logger.name == "aios"
    assert logger.level == 20  # INFO


def test_runtime_config_defaults():
    cfg = RuntimeConfig()
    assert cfg.environment == "dev"
    assert cfg.offline_first is True
    assert cfg.metadata["version"] == __version__
    assert "metadata" in cfg.as_dict()
    assert cfg.as_dict()["metadata"]["version"] == __version__


def test_healthcheck_deterministic():
    h = healthcheck()
    assert h["status"] == "healthy"
    assert h["version"] == __version__
    # idempotent
    assert healthcheck() == h
