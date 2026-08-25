"""Evidence store and provenance chain (Rule 5)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


class EvidenceError(Exception):
    """Raised when an evidence invariant is violated."""


@dataclass
class Requirement:
    requirement_id: str
    title: str
    source: str = ""  # e.g. master spec section


@dataclass
class TaskRecord:
    task_id: str
    requirement_id: str


@dataclass
class Artifact:
    artifact_id: str
    task_id: str
    requirement_id: str
    kind: str = "implementation"


@dataclass
class Run:
    run_id: str
    artifact_id: str
    task_id: str
    command: str = ""


@dataclass
class Evidence:
    """A single piece of evidence supporting a PASS decision.

    Mirrors the required schema from the master specification (Rule 5).
    TASK-234 adds ``requirement_id`` (coverage tracking), ``freshness``
    (ISO-TTL; expired -> STALE) and ``coverage`` (requirement -> evidence map).
    """

    evidence_id: str
    task_id: str
    run_id: str
    producer: str
    type: str
    source: str
    content_hash: str
    created_at: str = ""
    parent_artifact: str = ""
    environment: str = ""
    status: str = "ADMISSIBLE"
    requirement_id: str = ""
    freshness: str = ""  # ISO timestamp TTL; empty = no expiry
    coverage: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = [
            self.evidence_id,
            self.task_id,
            self.run_id,
            self.producer,
            self.type,
            self.source,
            self.content_hash,
        ]
        if any(not str(v) for v in required):
            raise EvidenceError("Evidence is missing a mandatory field.")

    def is_stale(self, now: Optional[str] = None) -> bool:
        """True when ``freshness`` is set and has passed (TASK-234)."""
        if not self.freshness:
            return False
        try:
            expiry = datetime.fromisoformat(self.freshness)
            ref = datetime.fromisoformat(now) if now else datetime.now(timezone.utc)
            return ref > expiry
        except ValueError:
            return False


@dataclass
class ProvenanceChain:
    evidence: Evidence
    run: Optional[Run]
    artifact: Optional[Artifact]
    task: Optional[TaskRecord]
    requirement: Optional[Requirement]
    complete: bool = False


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class EvidenceStore:
    """Stores evidence and resolves provenance chains."""

    def __init__(self) -> None:
        self._evidence: Dict[str, Evidence] = {}
        self._runs: Dict[str, Run] = {}
        self._artifacts: Dict[str, Artifact] = {}
        self._tasks: Dict[str, TaskRecord] = {}
        self._requirements: Dict[str, Requirement] = {}
        self._coverage: Dict[str, List[str]] = {}  # TASK-234: requirement -> evidence_ids

    # ----- registries ------------------------------------------------- #
    def add_requirement(self, req: Requirement) -> Requirement:
        self._requirements[req.requirement_id] = req
        return req

    def add_task_record(self, rec: TaskRecord) -> TaskRecord:
        self._tasks[rec.task_id] = rec
        return rec

    def add_artifact(self, art: Artifact) -> Artifact:
        self._artifacts[art.artifact_id] = art
        return art

    def add_run(self, run: Run) -> Run:
        self._runs[run.run_id] = run
        return run

    # ----- evidence ---------------------------------------------------- #
    def add_evidence(
        self,
        evidence_id: str,
        task_id: str,
        run_id: str,
        producer: str,
        type: str,
        source: str,
        content: str = "",
        content_hash: Optional[str] = None,
        parent_artifact: str = "",
        environment: str = "",
        status: str = "ADMISSIBLE",
        created_at: str = "",
        requirement_id: str = "",
        freshness: str = "",
        coverage: Optional[Dict[str, str]] = None,
    ) -> Evidence:
        chash = content_hash or compute_hash(content or evidence_id)
        ev = Evidence(
            evidence_id=evidence_id,
            task_id=task_id,
            run_id=run_id,
            producer=producer,
            type=type,
            source=source,
            content_hash=chash,
            created_at=created_at or _now(),
            parent_artifact=parent_artifact,
            environment=environment,
            status=status,
            requirement_id=requirement_id,
            freshness=freshness,
            coverage=coverage or {},
        )
        self._evidence[evidence_id] = ev
        # TASK-234: maintain requirement -> evidence coverage map.
        if requirement_id:
            self._coverage.setdefault(requirement_id, []).append(evidence_id)
        return ev

    @property
    def coverage_map(self) -> Dict[str, List[str]]:
        """Requirement -> list of evidence IDs (TASK-234)."""
        return {k: list(v) for k, v in self._coverage.items()}

    def is_requirement_covered(self, requirement_id: str) -> bool:
        """True when at least one non-stale evidence exists for the requirement."""
        for ev_id in self._coverage.get(requirement_id, []):
            ev = self._evidence.get(ev_id)
            if ev is not None and not ev.is_stale():
                return True
        return False

    def get(self, evidence_id: str) -> Evidence:
        if evidence_id not in self._evidence:
            raise EvidenceError(f"Evidence '{evidence_id}' not found.")
        return self._evidence[evidence_id]

    # ----- provenance -------------------------------------------------- #
    def get_provenance_chain(self, evidence_id: str) -> ProvenanceChain:
        """Resolve the full chain: Evidence -> Run -> Artifact -> Task -> Requirement."""
        ev = self.get(evidence_id)
        run = self._runs.get(ev.run_id)
        artifact = self._artifacts.get(ev.parent_artifact) if ev.parent_artifact else (
            self._artifacts.get(run.artifact_id) if run else None
        )
        task = self._tasks.get(ev.task_id)
        requirement = (
            self._requirements.get(task.requirement_id) if task else None
        )
        complete = all([ev, run, artifact, task, requirement])
        return ProvenanceChain(
            evidence=ev,
            run=run,
            artifact=artifact,
            task=task,
            requirement=requirement,
            complete=complete,
        )

    def is_admissible(self, evidence_id: str) -> bool:
        """An evidence is admissible only with a complete provenance chain."""
        return self.get_provenance_chain(evidence_id).complete

    # ----- TASK-235: Evidence Quality & Integrity ---------------------- #
    def detect_conflicts(self) -> List[tuple]:
        """Return pairs of evidence IDs that conflict on the same requirement.

        A conflict = two admissible evidence for the same requirement whose
        ``type``/``status`` disagree (e.g. one PASS, one FAIL). UNKNOWN/STALE
        are excluded (they cannot overturn a valid verdict).
        """
        conflicts: List[tuple] = []
        by_req: Dict[str, List[Evidence]] = {}
        for ev in self._evidence.values():
            if ev.requirement_id and not ev.is_stale():
                by_req.setdefault(ev.requirement_id, []).append(ev)
        for req, evs in by_req.items():
            for i in range(len(evs)):
                for j in range(i + 1, len(evs)):
                    a, b = evs[i], evs[j]
                    if a.status != b.status and {a.status, b.status} & {"ADMISSIBLE", "PASS", "FAIL"}:
                        conflicts.append((a.evidence_id, b.evidence_id))
        return conflicts

    def replay(self, run_id: str) -> List[Evidence]:
        """Reconstruct the evidence produced by a given run (TASK-235)."""
        return [ev for ev in self._evidence.values() if ev.run_id == run_id]

    def quality_score(
        self,
        evidence_id: str,
        producer_trust: Optional[Dict[str, float]] = None,
    ) -> float:
        """Quality score in [0,1] = producer_trust × freshness × verification.

        producer_trust defaults to 0.8 when unknown; freshness=0 if stale;
        verification=1 when status is ADMISSIBLE/PASS else 0.5.
        """
        ev = self.get(evidence_id)
        trust = (producer_trust or {}).get(ev.producer, 0.8)
        fresh = 0.0 if ev.is_stale() else 1.0
        verified = 1.0 if ev.status in ("ADMISSIBLE", "PASS") else 0.5
        return round(trust * fresh * verified, 4)

    def is_valid_for_evaluation(self, evidence_id: str) -> bool:
        """TASK-235: evaluation only accepts valid evidence.

        Rejects UNKNOWN status, STALE freshness, and any evidence that is part
        of a detected conflict.
        """
        ev = self.get(evidence_id)
        if ev.status == "UNKNOWN":
            return False
        if ev.is_stale():
            return False
        conflicts = self.detect_conflicts()
        if any(evidence_id in pair for pair in conflicts):
            return False
        return True

    def list_all(self) -> List[Evidence]:
        return list(self._evidence.values())


def record_execution_evidence(
    store: "EvidenceStore",
    workflow_name: str,
    workflow_version: str,
    plan: Any,
    report: Any,
    source_file: str,
    *,
    simulated: bool = False,
) -> List[str]:
    """Record a complete provenance chain for an execution (TASK-222 / TASK-229).

    Registers Requirement -> TaskRecord -> Artifact -> Run -> Evidence (one per
    step) so :meth:`EvidenceStore.get_provenance_chain` returns ``complete``.
    When ``simulated=True`` (TASK-229), ``report`` may be ``None``: the same
    unified ``ExecutionPlan`` contract is used and Evidence is emitted with
    type ``SIMULATED`` (no OS execution, 0 LLM calls). Returns evidence IDs.
    """
    requirement_id = "req-execute"
    task_id = "TASK-EXEC-CLI"
    store.add_requirement(Requirement(requirement_id, f"execute {workflow_name}"))
    store.add_task_record(TaskRecord(task_id, requirement_id))
    artifact_id = f"artifact-{workflow_name}-{workflow_version}"
    store.add_artifact(Artifact(artifact_id, task_id, requirement_id, kind="execution"))
    run_id = f"run-sim-{workflow_name}" if simulated else f"run-{report.execution_id}"
    store.add_run(
        Run(run_id, artifact_id, task_id, command=f"aiagent execute --simulate {source_file}")
        if simulated
        else Run(run_id, artifact_id, task_id, command=f"aiagent execute {source_file}")
    )

    # TASK-234: freshness TTL (1h) so evidence can be flagged STALE on expiry.
    from datetime import timedelta

    freshness = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    evidence_ids: List[str] = []
    if simulated:
        # No report: emit one SIMULATED evidence per plan step.
        for step in plan.steps:
            content = str(step.metadata.get("command", step.action))
            ev = Evidence(
                evidence_id=f"ev-sim-{workflow_name}-{step.step_id}",
                task_id=task_id,
                run_id=run_id,
                producer="Simulator",
                type="SIMULATED",
                source=step.step_id,
                content_hash=compute_hash(content),
            )
            store.add_evidence(
                evidence_id=ev.evidence_id,
                task_id=ev.task_id,
                run_id=ev.run_id,
                producer=ev.producer,
                type=ev.type,
                source=ev.source,
                content_hash=ev.content_hash,
                requirement_id=requirement_id,
                freshness=freshness,
                coverage={requirement_id: ev.evidence_id},
            )
            evidence_ids.append(ev.evidence_id)
        return evidence_ids

    for step_id, sr in report.results.items():
        content = str(sr.output) if sr.output is not None else (sr.error or "")
        ev = Evidence(
            evidence_id=f"ev-{report.execution_id}-{step_id}",
            task_id=task_id,
            run_id=run_id,
            producer="RealToolHandler",
            type="step_output",
            source=step_id,
            content_hash=compute_hash(content),
        )
        store.add_evidence(
            evidence_id=ev.evidence_id,
            task_id=ev.task_id,
            run_id=ev.run_id,
            producer=ev.producer,
            type=ev.type,
            source=ev.source,
            content_hash=ev.content_hash,
            requirement_id=requirement_id,
            freshness=freshness,
            coverage={requirement_id: ev.evidence_id},
        )
        evidence_ids.append(ev.evidence_id)
    return evidence_ids
