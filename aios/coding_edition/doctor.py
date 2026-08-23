"""TASK-212 — Coding Doctor (M26).

Diagnose a coding session/run for health issues, converging Doctor/Readiness
(T034) and Observability (T021). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from aios.coding_edition._common import CodingEditionError, _hash


class DiagnosticLevel(str, Enum):
    """Severity of a diagnostic (T212)."""

    OK = "OK"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class Diagnostic:
    """A single diagnostic finding (T212)."""

    check: str
    level: DiagnosticLevel
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.check:
            raise CodingEditionError("check name is required.")


class CodingDoctor:
    """Deterministic coding doctor (T212)."""

    def __init__(self, run_id: Optional[str] = None) -> None:
        self._run_id = run_id or f"doc-{uuid.uuid4().hex[:12]}"

    @property
    def run_id(self) -> str:
        return self._run_id

    def diagnose(self, *, steps: int = 0, failures: int = 0, open_issues: int = 0) -> List[Diagnostic]:
        """Run a fixed set of deterministic checks (fail-closed)."""
        diags: List[Diagnostic] = []
        if steps == 0:
            diags.append(Diagnostic("progress", DiagnosticLevel.ERROR, "no steps committed"))
        else:
            diags.append(Diagnostic("progress", DiagnosticLevel.OK, f"{steps} steps"))
        if failures > 0:
            diags.append(Diagnostic("failures", DiagnosticLevel.ERROR, f"{failures} failures"))
        else:
            diags.append(Diagnostic("failures", DiagnosticLevel.OK, "no failures"))
        if open_issues > 3:
            diags.append(Diagnostic("issues", DiagnosticLevel.WARNING, f"{open_issues} open issues"))
        else:
            diags.append(Diagnostic("issues", DiagnosticLevel.OK, f"{open_issues} open issues"))
        return diags

    def is_healthy(self, diags: List[Diagnostic]) -> bool:
        return all(d.level != DiagnosticLevel.ERROR for d in diags)

    def doctor_hash(self, diags: List[Diagnostic]) -> str:
        payload = "|".join(f"{d.check}:{d.level.value}" for d in diags)
        return _hash(f"{self._run_id}|{payload}")
