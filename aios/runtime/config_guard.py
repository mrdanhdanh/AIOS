"""Config validation guard — fail-closed startup (TASK-065 hardening).

Refuses to start the runtime with an invalid configuration. Builds on
:class:`aios.core.config.Config` (which already validates at construction) and
adds production-hardening checks (bounds, non-empty paths, sane limits). Raises
:class:`ConfigError`/ :class:`ConfigValidationError` on any violation —
fail-closed, never silent.

Layering: runtime layer — imports ``aios.core.config`` (unknown) only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

from aios.core.config import Config

__all__ = [
    "ConfigValidationError",
    "ConfigGuard",
    "validate_config",
    "require_valid_config",
]


class ConfigValidationError(Exception):
    """Raised when configuration fails the hardening validation (fail-closed)."""


# Production bounds for hardening checks.
_MAX_HEALTHCHECK_TIMEOUT = 300.0
_MIN_METADATA_CACHE_TTL = 0
_MAX_METADATA_CACHE_TTL = 86400 * 7
_VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def validate_config(config: Config) -> List[str]:
    """Return a list of validation error messages (empty == valid)."""
    errors: List[str] = []
    if not isinstance(config, Config):
        errors.append("config must be an instance of aios.core.config.Config")
        return errors
    # healthcheck_timeout bounds
    if not (0 < config.healthcheck_timeout <= _MAX_HEALTHCHECK_TIMEOUT):
        errors.append(
            f"healthcheck_timeout must be in (0, {_MAX_HEALTHCHECK_TIMEOUT}], "
            f"got {config.healthcheck_timeout}"
        )
    # metadata_cache_ttl bounds
    if not (_MIN_METADATA_CACHE_TTL <= config.metadata_cache_ttl <= _MAX_METADATA_CACHE_TTL):
        errors.append(
            f"metadata_cache_ttl must be in "
            f"[{_MIN_METADATA_CACHE_TTL}, {_MAX_METADATA_CACHE_TTL}], "
            f"got {config.metadata_cache_ttl}"
        )
    # config_dir must be non-empty
    if not config.config_dir or not str(config.config_dir).strip():
        errors.append("config_dir must be a non-empty string")
    # log_level already validated by Config; re-assert defensively
    if config.log_level not in _VALID_LOG_LEVELS:
        errors.append(f"invalid log_level: {config.log_level!r}")
    return errors


def require_valid_config(config: Config) -> Config:
    """Fail-closed: raise :class:`ConfigValidationError` if invalid.

    Returns the config unchanged when valid. This is the entry point the
    runtime kernel calls before starting — refuse to start on invalid config.
    """
    errors = validate_config(config)
    if errors:
        raise ConfigValidationError("; ".join(errors))
    return config


@dataclass
class ConfigGuard:
    """Holds a config and refuses to start when invalid (fail-closed)."""

    config: Config
    on_invalid: Optional[Callable[[List[str]], None]] = None

    def validate(self) -> List[str]:
        return validate_config(self.config)

    def start(self) -> Config:
        """Refuse to start with invalid config — raise typed error."""
        errors = validate_config(self.config)
        if errors:
            if self.on_invalid is not None:
                self.on_invalid(errors)
            raise ConfigValidationError("; ".join(errors))
        return self.config
