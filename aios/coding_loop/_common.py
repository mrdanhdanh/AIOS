"""Shared helpers for the coding loop subsystem (M21).

Provides deterministic timestamp/hash helpers and the base fail-closed error used
across T145-T154. Kept dependency-free (stdlib only) so every module in the
``aios.coding_loop`` package stays I/O-free and deterministic.

Layering: ``coding_loop`` is an ``unknown`` (infra) layer per the architecture
guard, so it may import stdlib + ``aios.core`` + ``aios.governance`` (unknown).
It must never import ``subprocess``/``os`` execution primitives, provider or
filesystem adapters directly (ARCH-001..004 spirit).
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone


def _now() -> str:
    """UTC ISO-8601 timestamp (deterministic format)."""
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    """sha256 hex digest (T078 integrity hashing)."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# Secret redaction pattern (T040/T113): redact assignment of sensitive values.
_SECRET_RE = re.compile(
    r"(?i)(secret|password|passwd|pwd|token|api[_-]?key|access[_-]?key|private[_-]?key)\s*[:=]\s*\S+"
)


def redact_secret(text: str) -> str:
    """Redact obvious secret assignments so observations never leak (T040/T113)."""
    if not text:
        return text
    return _SECRET_RE.sub(r"\1=***REDACTED***", text)


class CodingLoopError(Exception):
    """Base fail-closed error for the coding loop subsystem (T078)."""
