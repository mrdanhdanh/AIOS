"""TASK-181 — Governance Ledger + Provenance Graph (M24).

Append-only ledger with hash-chain integrity plus a provenance graph builder.
Tamper detection via recomputed entry hashes (Rule 5 provenance).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.quality_gate._common import QualityGateError, _hash


@dataclass(frozen=True)
class LedgerEntry:
    entry_id: str
    subject: str
    action: str
    prev_hash: str
    entry_hash: str

    def __post_init__(self) -> None:
        if not self.entry_id:
            raise QualityGateError("entry_id must be non-empty")
        if not self.subject:
            raise QualityGateError("subject must be non-empty")
        if not self.entry_hash:
            raise QualityGateError("entry_hash must be non-empty (provenance)")


@dataclass(frozen=True)
class LedgerReport:
    report_id: str
    entries: tuple
    tampered: tuple


@dataclass(frozen=True)
class ProvenanceEdge:
    edge_id: str
    source: str
    target: str


class GovernanceLedger:
    """Append-only ledger with hash-chain integrity + provenance graph."""

    def record(self, subject: str, action: str, prev_hash: str = "GENESIS") -> LedgerEntry:
        if not subject:
            raise QualityGateError("subject must be non-empty")
        if not action:
            raise QualityGateError("action must be non-empty")
        entry_id = _hash(f"{subject}|{action}|{prev_hash}")
        entry_hash = _hash(f"{entry_id}|{prev_hash}")
        return LedgerEntry(entry_id=entry_id, subject=subject, action=action, prev_hash=prev_hash, entry_hash=entry_hash)

    def verify(self, entries: List[LedgerEntry]) -> LedgerReport:
        if entries is None:
            raise QualityGateError("entries must be provided")
        tampered: List[str] = []
        for e in entries:
            if not isinstance(e, LedgerEntry):
                raise QualityGateError("each entry must be a LedgerEntry")
            expected = _hash(f"{e.entry_id}|{e.prev_hash}")
            if expected != e.entry_hash:
                tampered.append(e.entry_id)
        report_id = _hash(f"{len(entries)}|{','.join(sorted(tampered))}")
        return LedgerReport(report_id=report_id, entries=tuple(entries), tampered=tuple(tampered))


class ProvenanceGraph:
    """Build a provenance graph from entries (edges subject->action)."""

    def build(self, entries: List[LedgerEntry]) -> List[ProvenanceEdge]:
        if entries is None:
            raise QualityGateError("entries must be provided")
        edges: List[ProvenanceEdge] = []
        for e in entries:
            if not isinstance(e, LedgerEntry):
                raise QualityGateError("each entry must be a LedgerEntry")
            edge_id = _hash(f"{e.subject}|{e.action}")
            edges.append(ProvenanceEdge(edge_id=edge_id, source=e.subject, target=e.action))
        return edges
