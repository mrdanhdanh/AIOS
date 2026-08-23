"""Shared helpers for the M18 context pipeline (T117-T124).

Provides deterministic hashing (T078), secret isolation (T040/T113) and
evidence emission (T001 Rule 5) used by every stage of the pipeline. The
``context`` package is an ``unknown`` (infra) layer: it may import stdlib and
sibling packages but never agent/orchestrator internals.
"""

from __future__ import annotations

from typing import Optional

from aios.governance.evidence.store import EvidenceStore, compute_hash
from aios.verification_integrity.integrity import sha256


# File-name fragments that mark a file as a secret (T040/T113). Such files are
# never read, hashed, indexed or returned by the context pipeline.
SECRET_NAME_FRAGMENTS = (
    ".env",
    ".envrc",
    "credentials",
    "credential",
    "secret",
    "secrets",
    "id_rsa",
    "id_ed25519",
    "id_dsa",
    "id_ecdsa",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    "password",
    "token",
    "private_key",
)


class ContextError(Exception):
    """Base fail-closed error for the context pipeline (T078)."""


class SecretBoundary:
    """Identifies and redacts secrets (T040/T113)."""

    @staticmethod
    def is_secret_path(path: str) -> bool:
        name = path.replace("\\", "/").lower().split("/")[-1]
        return any(frag in name for frag in SECRET_NAME_FRAGMENTS)

    @staticmethod
    def redact(value: str) -> str:
        if not value:
            return value
        return "***REDACTED***"


def emit_evidence(
    store: EvidenceStore,
    *,
    task_id: str,
    run_id: str,
    producer: str,
    type_: str,
    source: str,
    content: str,
    evidence_id: Optional[str] = None,
) -> str:
    """Record an evidence item and return its id (T001 Rule 5)."""
    eid = evidence_id or f"ev-{producer}-{compute_hash(content)[:16]}"
    store.add_evidence(
        evidence_id=eid,
        task_id=task_id,
        run_id=run_id,
        producer=producer,
        type=type_,
        source=source,
        content=content,
    )
    return eid


def stable_hash_pairs(pairs: list[tuple[str, str]]) -> str:
    """Deterministic hash over an ordered list of (key, value) pairs."""
    canonical = "\n".join(f"{k}\t{v}" for k, v in pairs)
    return sha256(canonical)
