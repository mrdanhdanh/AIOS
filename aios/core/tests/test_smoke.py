"""Smoke test: all core modules are importable."""

from __future__ import annotations


def test_import_aios_root():
    import aios
    assert hasattr(aios, "__version__")
    assert hasattr(aios, "__milestone__")


def test_import_core_config():
    from aios.core.config import Config, ConfigError
    cfg = Config()
    assert cfg.log_level == "INFO"


def test_import_core_logging():
    from aios.core.logging import setup_logging, get_logger, JSONFormatter
    assert callable(setup_logging)
    assert callable(get_logger)


def test_import_core_metadata():
    from aios.core.metadata import PackageMetadata, BuildInfo
    meta = PackageMetadata.current()
    assert meta.name == "aios"


def test_import_core_healthcheck():
    from aios.core.healthcheck import HealthCheck, HealthResult, HealthStatus
    hc = HealthCheck()
    result = hc.run()
    assert result.status == HealthStatus.HEALTHY
