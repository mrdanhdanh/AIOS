"""Shared helpers for the aios.adversarial package (M23 — Adversarial Evaluation).

Infra/unknown layer: deterministic-first, fail-closed, provenance-bearing.
No LLM, no I/O, no provider/filesystem imports.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Optional


def _now() -> str:
    """Return a UTC ISO-8601 timestamp (deterministic, monotonic-friendly)."""
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    """Return a stable sha256 hex digest for provenance/integrity."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


_SECRET_RE = re.compile(r"(?i)(secret|token|password|passwd|api[_-]?key|apikey|private[_-]?key)\s*[:=]\s*(\S+)")


def redact_secret(text: str) -> str:
    """Redact secret assignments so provenance never leaks credentials."""
    return _SECRET_RE.sub(lambda m: f"{m.group(1)}: <REDACTED>", text)


class AdversarialError(Exception):
    """Fail-closed base error for the adversarial package.

    Any violation of a deterministic invariant raises this (or a subclass).
    UNKNOWN is never promoted to PASS; the pipeline stops on error.
    """

    def __init__(self, message: str, *, detail: Optional[Any] = None) -> None:
        super().__init__(message)
        self.detail = detail
