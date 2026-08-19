"""Critic role.

Produces critique documents (critique-1.md, critique-2.md). It is a pure
analysis function over a specification; it does not import runtime internals.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class CritiqueReport:
    round: int
    findings: List[str]
    verdict: str  # "APPROVE" or "REVISE"


class Critic:
    """Reviews a specification and emits findings."""

    def critique(self, spec_text: str, round_no: int, prior_findings: List[str] | None = None) -> CritiqueReport:
        findings: List[str] = []
        if not spec_text.strip():
            findings.append("Specification is empty.")
        if "Acceptance Criteria" not in spec_text:
            findings.append("Missing Acceptance Criteria section.")
        if "## Scope" not in spec_text:
            findings.append("Scope is not clearly bounded.")
        verdict = "APPROVE" if not findings else "REVISE"
        return CritiqueReport(round=round_no, findings=findings, verdict=verdict)
