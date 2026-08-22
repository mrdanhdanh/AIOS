"""Visual Evidence — visual regression + UI state contract (TASK-080, M11).

Extends the Harness (T030/T032) with visual evidence: capture UI state
(screenshot / DOM snapshot), define a UI State Contract (valid states +
baseline), run visual regression (diff vs baseline), and bind visual evidence
to the provenance chain (T001 Rule 5). Does NOT replace the harness.

Layering: ``unknown`` (infra) layer — stdlib + ``aios.governance.evidence``
+ ``aios.harness`` + ``aios.replay`` only.
"""

from __future__ import annotations

from .visual import (
    VisualCapture,
    UIStateContract,
    VisualRegression,
    VisualEvidence,
    VisualError,
)

__all__ = [
    "VisualCapture",
    "UIStateContract",
    "VisualRegression",
    "VisualEvidence",
    "VisualError",
]
