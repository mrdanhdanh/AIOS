"""aios.core — M1 monorepo scaffold package.

Re-exports the stable foundation used by the runtime, orchestrator and harness.
"""
from .scaffold import (
    CORE_METADATA,
    RuntimeConfig,
    configure_logging,
    healthcheck,
)
from .scaffold import __version__, __milestone__

__all__ = [
    "CORE_METADATA",
    "RuntimeConfig",
    "configure_logging",
    "healthcheck",
    "__version__",
    "__milestone__",
]
