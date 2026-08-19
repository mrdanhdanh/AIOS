"""Structured logging setup for AIOS.

Provides :func:`setup_logging` to configure the root logger with a JSON
formatter and a per-module :func:`get_logger` factory.

Log envelope fields:
    ``timestamp`` · ``level`` · ``logger`` · ``message`` · ``extra``
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .config import Config

__all__ = ["setup_logging", "get_logger", "JSONFormatter"]


class JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON line.

    Envelope::

        {
            "timestamp": "2026-08-19T12:00:00Z",
            "level": "INFO",
            "logger": "aios.core.config",
            "message": "Config loaded",
            "extra": {"key": "value"}
        }
    """

    def format(self, record: logging.LogRecord) -> str:  # noqa: D102
        envelope: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "extra": getattr(record, "extra", {}),
        }
        return json.dumps(envelope, ensure_ascii=False, default=str)


class TextFormatter(logging.Formatter):
    """Human-readable ``LEVEL logger: message`` format for development."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D102
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"{ts} | {record.levelname:<8} | {record.name} | {record.getMessage()}"


def setup_logging(config: Optional[Config] = None) -> Config:
    """Configure the root logger from a :class:`Config`.

    * Sets the root logger level to ``config.log_level``.
    * Attaches a :class:`JSONFormatter` (or :class:`TextFormatter`) to
      ``sys.stderr``.

    Returns the (possibly default) :class:`Config` used.
    """
    if config is None:
        config = Config()

    root = logging.getLogger()
    root.setLevel(getattr(logging, config.log_level))

    # Remove existing handlers to avoid duplicate output.
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stderr)
    if config.log_format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(TextFormatter())
    root.addHandler(handler)

    return config


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``aios`` namespace."""
    return logging.getLogger(f"aios.{name}" if not name.startswith("aios.") else name)
