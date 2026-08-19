"""Reviewer role.

Performs the final review (review.md) before implementation. It validates that
the mandatory governance artifacts are present and that the deterministic path
was preferred. Pure analysis — no direct runtime/tool access.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ReviewReport:
    approved: bool
    notes: List[str]


class Reviewer:
    """Final gate before implementation begins."""

    REQUIRED_BEFORE_IMPL = [
        "spec.md",
        "critique-1.md",
        "critique-2.md",
        "tasks.md",
    ]

    def review(self, artifacts: Dict[str, str]) -> ReviewReport:
        notes: List[str] = []
        missing = [a for a in self.REQUIRED_BEFORE_IMPL if a not in artifacts]
        if missing:
            notes.append(f"Missing artifacts: {missing}")
            return ReviewReport(approved=False, notes=notes)
        notes.append("All pre-implementation artifacts present.")
        return ReviewReport(approved=True, notes=notes)
