"""TASK-160 — Security Verifier (M22).

Deterministic security gate: any finding at blocking severity (high/critical)
fails the verification. Fail-closed: a scan with no provenance (empty id) is
rejected; blocking findings -> INSUFFICIENT (never promoted).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from aios.verification._common import VerificationError, _hash, _now

BLOCKING_SEVERITIES = frozenset({"high", "critical"})


@dataclass(frozen=True)
class SecurityScan:
    scan_id: str
    findings: tuple = field(default_factory=tuple)  # tuples of (id, severity)

    def __post_init__(self) -> None:
        if not self.scan_id:
            raise VerificationError("scan_id must be non-empty")


@dataclass(frozen=True)
class SecurityReport:
    report_id: str
    scan_ref: str
    blocking_findings: tuple
    status: str  # PASS | INSUFFICIENT


class SecurityVerifier:
    """Gate a security scan on blocking-severity findings."""

    def verify(self, scan: SecurityScan) -> SecurityReport:
        if not isinstance(scan, SecurityScan):
            raise VerificationError("scan must be a SecurityScan")
        if not scan.scan_id:
            raise VerificationError("scan_id must be non-empty (provenance)")

        blocking: List[Tuple[str, str]] = []
        for finding in scan.findings:
            fid, severity = finding[0], str(finding[1]).lower()
            if severity in BLOCKING_SEVERITIES:
                blocking.append((fid, severity))

        status = "INSUFFICIENT" if blocking else "PASS"
        report_id = _hash(f"{scan.scan_id}|{len(blocking)}")
        return SecurityReport(
            report_id=report_id,
            scan_ref=scan.scan_id,
            blocking_findings=tuple(blocking),
            status=status,
        )
