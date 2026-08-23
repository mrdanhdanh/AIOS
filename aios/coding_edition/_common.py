"""Shared helpers for the aios.coding_edition package (M26 — AIOS 2.0 Coding Edition).

Infra/unknown layer: deterministic-first, fail-closed, provenance-bearing.
No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 spirit).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Optional


def _now() -> str:
    """Return a UTC ISO-8601 timestamp (deterministic, monotonic-friendly)."""
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    """Return a stable sha256 hex digest for provenance/integrity."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class CodingEditionError(Exception):
    """Fail-closed base error for the coding edition package.

    Any violation of a deterministic invariant raises this (or a subclass).
    UNKNOWN is never promoted to PASS; the pipeline stops on error.
    """

    def __init__(self, message: str, *, detail: Optional[str] = None) -> None:
        super().__init__(message)
        self.detail = detail

    def __str__(self) -> str:  # pragma: no cover - trivial
        if self.detail:
            return f"{self.args[0]} ({self.detail})"
        return str(self.args[0])
