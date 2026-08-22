"""Verification Integrity — fail-closed integrity gate (TASK-078, M11).

Integrity layer over Harness verification (T030) / evaluation (T032) and
Evidence (T001 Rule 5). It does NOT replace the harness; it adds an
integrity + fail-closed verdict gate on top of existing evidence/verdicts.

Layering: ``unknown`` (infra) layer — stdlib + ``aios.governance.evidence``
+ ``aios.harness`` only. No provider/filesystem/agent imports.
"""

from __future__ import annotations

from .integrity import (
    IntegrityReport,
    IntegrityChecker,
    IntegrityError,
    VerifierLock,
)

__all__ = [
    "IntegrityReport",
    "IntegrityChecker",
    "IntegrityError",
    "VerifierLock",
]
