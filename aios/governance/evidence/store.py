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
        )
        self._evidence[evidence_id] = ev
        return ev

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

    def list_all(self) -> List[Evidence]:
        return list(self._evidence.values())
