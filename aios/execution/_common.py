"""Shared helpers for the execution subsystem (M20).

Provides deterministic timestamp/hash helpers and the base fail-closed error used
across T135-T144. Kept dependency-free (stdlib only) so every module in the
``aios.execution`` package stays I/O-free and deterministic.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone


def _now() -> str:
    """UTC ISO-8601 timestamp (deterministic format)."""
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    """sha256 hex digest (T078 integrity hashing)."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class ExecutionError(Exception):
    """Base fail-closed error for the execution subsystem (T078)."""
