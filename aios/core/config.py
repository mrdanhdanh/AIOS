"""Centralised, typed configuration with environment-variable overrides.

Config values are loaded from environment variables with the ``AIOS_`` prefix.
Invalid values cause a :class:`ConfigError` at construction time (fail-closed).

Example::

    from aios.core.config import Config

    cfg = Config()          # reads AIOS_* env vars, falls back to defaults
    print(cfg.log_level)    # 'INFO'

Log envelope schema (used by :mod:`aios.core.logging`)::

    {
        "timestamp": "2026-08-19T12:00:00Z",
        "level": "INFO",
        "logger": "aios.core.config",
        "message": "Config loaded",
        "extra": {}
    }
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

__all__ = ["Config", "ConfigError"]

_PREFIX = "AIOS_"

# Valid log levels accepted by the logging module.
_VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class ConfigError(Exception):
    """Raised when a configuration value is invalid."""


def _env(key: str, default: str | None = None) -> str | None:
    """Read an ``AIOS_``-prefixed environment variable."""
    return os.environ.get(f"{_PREFIX}{key}", default)


def _env_int(key: str, default: int = 0) -> int:
    raw = _env(key, str(default))
    try:
        return int(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ConfigError(
            f"Environment variable {_PREFIX}{key} must be an integer, got {raw!r}"
        )


def _env_bool(key: str, default: bool = False) -> bool:
    raw = _env(key, str(default))
    if isinstance(raw, str):
        return raw.lower() in {"1", "true", "yes"}
    return bool(raw)


@dataclass(frozen=True)
class Config:
    """Typed, immutable AIOS configuration.

    Every field can be overridden via an ``AIOS_<FIELD_UPPER>`` environment
    variable.  Invalid values raise :class:`ConfigError` immediately.
    """

    log_level: str = field(default_factory=lambda: _env("LOG_LEVEL", "INFO"))
    log_format: str = field(default_factory=lambda: _env("LOG_FORMAT", "json"))
    config_dir: str = field(default_factory=lambda: _env("CONFIG_DIR", ".aios"))
    healthcheck_timeout: float = field(
        default_factory=lambda: float(_env("HEALTHCHECK_TIMEOUT", "5.0"))
    )
    metadata_cache_ttl: int = field(
        default_factory=lambda: _env_int("METADATA_CACHE_TTL", 300)
    )
    dry_run: bool = field(default_factory=lambda: _env_bool("DRY_RUN", False))

    def __post_init__(self) -> None:  # noqa: D105 (dataclass)
        # Validate log level.
        level = self.log_level.upper()
        if level not in _VALID_LOG_LEVELS:
            raise ConfigError(
                f"Invalid log level {self.log_level!r}; "
                f"expected one of {_VALID_LOG_LEVELS}"
            )
        # Normalise to uppercase.
        object.__setattr__(self, "log_level", level)

        # Validate log format.
        if self.log_format not in {"json", "text"}:
            raise ConfigError(
                f"Invalid log format {self.log_format!r}; expected 'json' or 'text'"
            )

        # Validate timeout.
        if self.healthcheck_timeout <= 0:
            raise ConfigError(
                f"healthcheck_timeout must be positive, got {self.healthcheck_timeout}"
            )

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        """Attribute-style lookup with fallback."""
        return getattr(self, key, default)

    def as_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dictionary."""
        return {
            "log_level": self.log_level,
            "log_format": self.log_format,
            "config_dir": self.config_dir,
            "healthcheck_timeout": self.healthcheck_timeout,
            "metadata_cache_ttl": self.metadata_cache_ttl,
            "dry_run": self.dry_run,
        }
