"""aios_core scaffold — M1 monorepo foundation.

Provides version metadata, structured logging bootstrap, runtime config,
and a deterministic healthcheck. No direct import of os/pathlib/subprocess/
provider (Rule 3 — architecture guard; deterministic-first).
"""
from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Dict

__version__ = "0.1.0"
__milestone__ = "M1"


CORE_METADATA: Dict[str, Any] = {
    "name": "aios_core",
    "version": __version__,
    "milestone": __milestone__,
    "runtime_first": True,
    "plugin_first": True,
    "offline_first": True,
    "harness_verified": True,
    "coding_plane": True,
}


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Bootstrap structured logging for the runtime (stdout handler)."""
    logger = logging.getLogger("aios")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


@dataclass
class RuntimeConfig:
    """Minimal runtime configuration contract (deterministic defaults)."""
    environment: str = "dev"
    log_level: str = "INFO"
    offline_first: bool = True
    metadata: Dict[str, Any] = field(default_factory=lambda: dict(CORE_METADATA))

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def healthcheck() -> Dict[str, Any]:
    """Return a deterministic health snapshot (no external calls)."""
    return {
        "status": "healthy",
        "version": __version__,
        "milestone": __milestone__,
        "logging": "configured",
    }
