"""Evidence Store — Rule 5 (provenance chain, fail-closed)."""
import re
from dataclasses import dataclass, field

_HASH_RE = re.compile(r"^sha256:[0-9a-fA-F]{3,}$")


@dataclass
class Evidence:
    evidence_id: str
    task_id: str
    run_id: str
    producer: str
    type: str
    source: str
    content_hash: str
    status: str  # PASS | FAIL | UNKNOWN
    created_at: str = ""
    parent_artifact: str = ""
    environment: str = ""


class EvidenceStore:
    def __init__(self):
        self._ev = {}

    def add(self, ev: Evidence):
        self._ev[ev.evidence_id] = ev

    def get(self, evidence_id):
        return self._ev.get(evidence_id)

    def provenance_chain(self, evidence_id):
        """Evidence -> Run -> Artifact -> Task -> Requirement."""
        ev = self._ev.get(evidence_id)
        if not ev:
            return None
        return {
            "evidence": ev.evidence_id,
            "run": ev.run_id,
            "artifact": ev.parent_artifact,
            "task": ev.task_id,
            "requirement": ev.source,
            "hash": ev.content_hash,
            "status": ev.status,
        }

    def verify(self, evidence_id):
        """Fail-closed: all fields truthy, status must be PASS, hash must be sha256:..., UNKNOWN never passes."""
        chain = self.provenance_chain(evidence_id)
        if not chain:
            return False
        if not all(chain.get(k) for k in ("evidence", "run", "artifact", "task", "requirement", "hash", "status")):
            return False
        # UNKNOWN is never PASS
        if chain["status"] == "UNKNOWN":
            return False
        if chain["status"] != "PASS":
            return False
        # hash must be sha256:... (or n/a is rejected for PASS)
        h = chain["hash"]
        if h in ("n/a", "unknown", "", None):
            return False
        if not _HASH_RE.match(str(h)):
            return False
        return True
