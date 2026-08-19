"""TASK-002 implementation artifact — aios_core scaffold (re-exported from aios.core).

This file is the task-folder copy of the M1 monorepo scaffold. It intentionally
does NOT import os/pathlib/subprocess/provider directly (Rule 3 — architecture guard).
"""
from aios.core import (
    CORE_METADATA,
    RuntimeConfig,
    configure_logging,
    healthcheck,
    __version__,
    __milestone__,
)

__all__ = [
    "CORE_METADATA",
    "RuntimeConfig",
    "configure_logging",
    "healthcheck",
    "__version__",
    "__milestone__",
]
