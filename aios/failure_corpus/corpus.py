"""Failure-Corpus Improvement Engine (TASK-100, M15).

Canonical corpus contract:

    CorpusEntry
    ├── failure_id
    ├── source: T094 | T099
    ├── symptom
    ├── root_cause
    ├── covered_by_harness: bool
    ├── version
    ├── content_hash
    └── evidence_ref

Safety properties (all fail-closed-gap / no-silent-drop / provenance / deterministic):
* Fail-closed gap — gap (not covered) must be reported, never hidden (T090).
* No silent drop — a failure is never discarded.
* Evidence required — every entry carries provenance (T001 Rule 5).
* Deterministic — same failure + same corpus -> same analysis.
* No parallel corpus system — uses Detect (T094) + Loop (T099) + Coverage (T090).

Integration: imports ``aios.remediation_detect`` (Diagnosis), ``aios.autonomous_harness_loop``
(HarnessLoopRun), ``aios.harness_coverage`` (CoverageMap, Readiness) and
``aios.governance.evidence.store`` (EvidenceStore). No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.autonomous_harness_loop.loop import HarnessLoopRun
from aios.governance.evidence.store import EvidenceStore
from aios.harness_coverage.coverage import CoverageMap
from aios.remediation_detect.detect import Diagnosis
from aios.verification_integrity.integrity import sha256


class FailureSource(str, Enum):
    """Where a failure was collected from."""

    T094 = "T094"  # Detect + Diagnose
    T099 = "T099"  # Autonomous Harness Loop


@dataclass
class CorpusEntry:
    """A single failure recorded in the corpus (versioned + hashed)."""

    failure_id: str
    source: str
    symptom: str
    root_cause: str
    covered_by_harness: bool
    version: int
    content_hash: str
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "source": self.source,
            "symptom": self.symptom,
            "root_cause": self.root_cause,
            "covered_by_harness": self.covered_by_harness,
            "version": self.version,
            "content_hash": self.content_hash,
            "evidence_ref": self.evidence_ref,
        }


class FailureCorpus:
    """Versioned, deduplicated failure corpus (fail-closed gap reporting)."""

    def __init__(self, evidence_store: Optional[EvidenceStore] = None) -> None:
        self._entries: Dict[str, CorpusEntry] = {}  # keyed by content_hash
        self._version = 1
        self._evidence = evidence_store or EvidenceStore()

    @property
    def version(self) -> int:
        return self._version

    def add(
        self,
        source: str,
        symptom: str,
        root_cause: str,
        covered_by_harness: bool,
        evidence_ref: str = "",
    ) -> CorpusEntry:
        """Add a failure; dedupe by content_hash (no silent drop, no duplicate)."""
        content = json.dumps(
            {"source": source, "symptom": symptom, "root_cause": root_cause},
            sort_keys=True,
        )
        h = sha256(content)
        existing = self._entries.get(h)
        if existing is not None:
            # Deterministic: same failure -> same entry (deduplicated).
            return existing
        entry = CorpusEntry(
            failure_id=f"fail-{h[:8]}",
            source=source,
            symptom=symptom,
            root_cause=root_cause,
            covered_by_harness=covered_by_harness,
            version=self._version,
            content_hash=h,
            evidence_ref=evidence_ref,
        )
        self._entries[h] = entry
        return entry

    def entries(self) -> List[CorpusEntry]:
        return list(self._entries.values())

    def gaps(self) -> List[CorpusEntry]:
        """Fail-closed gap: every uncovered failure is reported (T090)."""
        return [e for e in self._entries.values() if not e.covered_by_harness]

    def propose_improvements(self) -> List[str]:
        """Propose harness/detection/remediation improvements for each gap."""
        improvements: List[str] = []
        for e in self.gaps():
            improvements.append(f"improve:harness:{e.failure_id}")
            improvements.append(f"improve:detection:{e.failure_id}")
            improvements.append(f"improve:remediation:{e.failure_id}")
        return improvements

    def analysis_hash(self) -> str:
        """Deterministic hash of the current corpus analysis."""
        payload = {
            "version": self._version,
            "entries": sorted(e.to_dict() for e in self._entries.values()),
            "gaps": sorted(g.failure_id for g in self.gaps()),
            "improvements": sorted(self.propose_improvements()),
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()


class FailureCorpusEngine:
    """Collects failures, runs gap analysis and proposes improvements."""

    def __init__(
        self,
        evidence_store: Optional[EvidenceStore] = None,
        coverage_map: Optional[CoverageMap] = None,
    ) -> None:
        self._corpus = FailureCorpus(evidence_store)
        self._evidence = evidence_store or EvidenceStore()
        self._coverage = coverage_map or CoverageMap()

    # -- collection ----------------------------------------------------------

    def _covered(self, surface: str) -> bool:
        return self._coverage.harnessed(surface)

    def collect_from_diagnosis(self, diagnosis: Diagnosis) -> CorpusEntry:
        """Collect a failure from a Detect+Diagnose result (T094)."""
        symptom = "; ".join(s.description for s in diagnosis.symptoms) or "unknown"
        covered = self._covered(diagnosis.incident_id)
        entry = self._corpus.add(
            FailureSource.T094.value,
            symptom,
            diagnosis.root_cause,
            covered,
            diagnosis.evidence_ref,
        )
        self._record_evidence(entry)
        return entry

    def collect_from_loop(self, run: HarnessLoopRun) -> List[CorpusEntry]:
        """Collect failures from a harness loop run (T099)."""
        collected: List[CorpusEntry] = []
        for dev in run.deviations:
            covered = self._covered(dev)
            entry = self._corpus.add(
                FailureSource.T099.value,
                f"deviation:{dev}",
                "autonomous-loop-deviation",
                covered,
                run.evidence_ref,
            )
            self._record_evidence(entry)
            collected.append(entry)
        return collected

    # -- analysis ------------------------------------------------------------

    def gaps(self) -> List[CorpusEntry]:
        return self._corpus.gaps()

    def propose_improvements(self) -> List[str]:
        return self._corpus.propose_improvements()

    def analysis_hash(self) -> str:
        return self._corpus.analysis_hash()

    # -- evidence ------------------------------------------------------------

    def _record_evidence(self, entry: CorpusEntry) -> str:
        ev_id = entry.evidence_ref or entry.failure_id
        self._evidence.add_evidence(
            evidence_id=ev_id,
            task_id="TASK-100",
            run_id="run-100",
            producer="failure_corpus",
            type="corpus_entry",
            source=entry.failure_id,
            content=json.dumps(entry.to_dict(), sort_keys=True),
        )
        return ev_id

    def provenance_complete(self, entry: CorpusEntry) -> bool:
        """Every entry carries provenance (T001 Rule 5)."""
        return bool(entry.evidence_ref)
