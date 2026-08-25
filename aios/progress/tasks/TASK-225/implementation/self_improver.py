"""Self-Improver agent (TASK-225).

Pure, I/O-free, capability-injected agent that reflects on AIOS's own operation
(EvidenceStore + regression signals) and PROPOSES internal improvement tasks.
It never writes to the aios/ tree directly; it emits a proposal that the
CoordinatorAgent drives through the governance pipeline.

Per Rule 3 (Architecture Guard, ARCH-001..004) it MUST NOT import execution
primitives (subprocess), provider adapters or filesystem adapters directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Protocol


class EvidenceLike(Protocol):
    evidence_id: str
    task_id: str
    producer: str
    type: str
    status: str  # PASS | FAIL | UNKNOWN


class RegistryLike(Protocol):
    def get_task(self, task_id: str): ...
    def list_tasks(self) -> List: ...


@dataclass
class ImprovementProposal:
    title: str
    rationale: str
    target_module: str
    proposed_spec: str
    confidence: float
    source_signals: List[str] = field(default_factory=list)


@dataclass
class SelfImproverResult:
    analyzed_tasks: int = 0
    proposals: List[ImprovementProposal] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "analyzed_tasks": self.analyzed_tasks,
            "proposals": [vars(p) for p in self.proposals],
            "notes": self.notes,
        }


_FAIL_PENALTY = 1.0
_UNKNOWN_PENALTY = 0.5
_MIN_CONFIDENCE = 0.6


class SelfImproverAgent:
    """Proposes internal AIOS improvements from evidence/regression signals."""

    def __init__(self, evidence_store, registry, coordinator=None):
        self._evidence = evidence_store
        self._registry = registry
        self._coordinator = coordinator

    def analyze(self, min_confidence: float = _MIN_CONFIDENCE) -> SelfImproverResult:
        result = SelfImproverResult()
        records = self._collect_records()
        result.analyzed_tasks = len({getattr(r, "task_id", "?") for r in records})

        by_producer: dict = {}
        for r in records:
            status = getattr(r, "status", "UNKNOWN")
            if status in ("FAIL", "UNKNOWN"):
                pen = _FAIL_PENALTY if status == "FAIL" else _UNKNOWN_PENALTY
                key = getattr(r, "producer", "unknown")
                by_producer.setdefault(key, {"score": 0.0, "signals": []})
                by_producer[key]["score"] += pen
                by_producer[key]["signals"].append(f"{r.evidence_id}:{r.status}")

        for producer, info in by_producer.items():
            confidence = min(1.0, info["score"] / 3.0)
            if confidence < min_confidence:
                result.notes.append(
                    f"producer {producer} below threshold ({confidence:.2f})"
                )
                continue
            spec = self._draft_spec(producer, info["signals"])
            result.proposals.append(
                ImprovementProposal(
                    title=f"Self-improve: harden {producer}",
                    rationale=(
                        f"Evidence shows recurring {producer} failures "
                        f"(score={info['score']:.1f})."
                    ),
                    target_module=producer,
                    proposed_spec=spec,
                    confidence=confidence,
                    source_signals=info["signals"][:5],
                )
            )
        return result

    def _collect_records(self) -> List:
        store = self._evidence
        if hasattr(store, "list_all"):
            return list(store.list_all())
        if isinstance(store, (list, tuple)):
            return list(store)
        if hasattr(store, "all"):
            return list(store.all())
        return []

    def _draft_spec(self, producer: str, signals: List[str]) -> str:
        joined = "\n".join(f"- {s}" for s in signals[:5])
        return (
            f"# Self-Improvement Spec \u2014 {producer}\n\n"
            f"## Problem\nRecurring governance/evidence signals from "
            f"`{producer}`:\n{joined}\n\n"
            f"## Objective\nReduce recurrence via deterministic hardening "
            f"(fail-closed, provenance-bearing).\n\n"
            f"## Acceptance Criteria\n"
            f"1. Root-cause analysis recorded with evidence links.\n"
            f"2. Fix passes UnifiedTaskGate.\n"
            f"3. Regression covers the failing path.\n"
        )

    def propose_next(self, min_confidence: float = _MIN_CONFIDENCE):
        """Return the highest-confidence proposal, or None (fail-closed)."""
        result = self.analyze(min_confidence=min_confidence)
        if not result.proposals:
            return None
        return max(result.proposals, key=lambda p: p.confidence)
