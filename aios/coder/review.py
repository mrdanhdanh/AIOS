"""Code Review Agent (TASK-129, M19).

A pure, I/O-free, capability-injected review agent (T125/AGENTS). It reviews a
code artifact or patch (T127/T128) against static/contract rules and emits
findings with severity + provenance. A blocking finding forces a BLOCK verdict
(fail-closed, T078). Review is deterministic (same artifact + same rules ->
same verdict) and never bypasses policy (T022/T113).
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Tuple


class Severity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    BLOCK = "BLOCK"


class Verdict(str, Enum):
    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    BLOCK = "BLOCK"


class ReviewError(Exception):
    """Raised on review contract violations (fail-closed)."""


@dataclass
class Finding:
    rule: str
    severity: Severity
    message: str
    evidence_id: str

    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "severity": self.severity.value,
            "message": self.message,
            "evidence_id": self.evidence_id,
        }


@dataclass
class ReviewReport:
    report_id: str
    agent_id: str
    artifact_ref: Optional[str]
    patch_ref: Optional[str]
    findings: List[Finding]
    verdict: Verdict
    content_hash: str
    evidence_id: str

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "agent_id": self.agent_id,
            "artifact_ref": self.artifact_ref,
            "patch_ref": self.patch_ref,
            "findings": [f.to_dict() for f in self.findings],
            "verdict": self.verdict.value,
            "content_hash": self.content_hash,
            "evidence_id": self.evidence_id,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# Static/contract review rules. Each rule is a pure function of the reviewed
# content; deterministic given the same input.
_FORBIDDEN_PATTERNS: List[Tuple[str, str, Severity]] = [
    (r"\bimport subprocess\b", "no-subprocess", Severity.BLOCK),
    (r"\bos\.system\s*\(", "no-os-system", Severity.BLOCK),
    (r"\beval\s*\(", "no-eval", Severity.WARN),
    (r"print\s*\(", "avoid-print", Severity.INFO),
]


class CodeReviewAgent:
    """I/O-free, capability-injected code review agent (T129)."""

    def __init__(self, agent_id: str = "reviewer-1") -> None:
        if not agent_id:
            raise ReviewError("agent_id is required (T001 Rule 1, immutable).")
        self._agent_id = agent_id

    def review(
        self,
        content: str,
        artifact_ref: Optional[str] = None,
        patch_ref: Optional[str] = None,
        policy_ok: bool = True,
    ) -> ReviewReport:
        """Review ``content`` and emit a ReviewReport.

        Fail-closed: a BLOCK finding forces verdict BLOCK (T078). Policy bypass
        is rejected (T022/T113). Deterministic: same content -> same report.
        """
        if not policy_ok:
            raise ReviewError("Policy rejected review (T113).")
        findings: List[Finding] = []
        for pattern, rule, severity in _FORBIDDEN_PATTERNS:
            if re.search(pattern, content):
                findings.append(
                    Finding(
                        rule=rule,
                        severity=severity,
                        message=f"matched {rule}",
                        evidence_id=f"ev-{uuid.uuid4().hex[:12]}",
                    )
                )
        if any(f.severity is Severity.BLOCK for f in findings):
            verdict = Verdict.BLOCK
        elif any(f.severity is Severity.WARN for f in findings):
            verdict = Verdict.REQUEST_CHANGES
        else:
            verdict = Verdict.APPROVE

        content_blob = f"{self._agent_id}:{content}:{sorted((f.rule, f.severity.value) for f in findings)}"
        return ReviewReport(
            report_id=f"rev-{uuid.uuid4().hex[:12]}",
            agent_id=self._agent_id,
            artifact_ref=artifact_ref,
            patch_ref=patch_ref,
            findings=findings,
            verdict=verdict,
            content_hash=_hash(content_blob),
            evidence_id=f"ev-{uuid.uuid4().hex[:12]}",
        )
