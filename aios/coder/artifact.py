"""Coding Artifact + CodingEvidence (TASK-130, M19).

Standardizes coding artifacts (code/patch/review) produced across the T125->T129
pipeline and records a full provenance chain (T001 Rule 5). Every artifact
carries a ``content_hash`` (T078) and an immutable ``artifact_id`` (T001 Rule 1).
An artifact that fails the integrity gate is never promoted to PASS (fail-closed,
T078). Verification is deterministic (same artifact + same verifier -> same
verdict).
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


class ArtifactKind(str, Enum):
    CODE = "code"
    PATCH = "patch"
    REVIEW = "review"


class ArtifactStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class ArtifactError(Exception):
    """Raised on artifact contract violations (fail-closed, T078 / T001)."""


@dataclass
class EvidenceLink:
    evidence_id: str
    producer: str
    kind: str
    content_hash: str
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "producer": self.producer,
            "kind": self.kind,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp,
        }


@dataclass
class CodingArtifact:
    artifact_id: str
    kind: ArtifactKind
    content: str
    content_hash: str
    producer: str
    evidence_chain: List[EvidenceLink] = field(default_factory=list)
    integrity_verified: bool = False
    policy_ref: Optional[str] = None
    status: ArtifactStatus = ArtifactStatus.PENDING

    def to_dict(self) -> dict:
        return {
            "artifact_id": self.artifact_id,
            "kind": self.kind.value,
            "content": self.content,
            "content_hash": self.content_hash,
            "producer": self.producer,
            "evidence_chain": [e.to_dict() for e in self.evidence_chain],
            "integrity_verified": self.integrity_verified,
            "policy_ref": self.policy_ref,
            "status": self.status.value,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class CodingArtifactRegistry:
    """Registry of coding artifacts (immutable ids, T001 Rule 1)."""

    def __init__(self) -> None:
        self._store: Dict[str, CodingArtifact] = {}

    def create(
        self,
        kind: ArtifactKind,
        content: str,
        producer: str,
        evidence_links: Optional[List[EvidenceLink]] = None,
        policy_ref: Optional[str] = None,
    ) -> CodingArtifact:
        artifact_id = f"ca-{uuid.uuid4().hex[:12]}"
        if artifact_id in self._store:
            raise ArtifactError(f"artifact_id reused: {artifact_id} (T001 Rule 1).")
        artifact = CodingArtifact(
            artifact_id=artifact_id,
            kind=kind,
            content=content,
            content_hash=_hash(content),
            producer=producer,
            evidence_chain=list(evidence_links or []),
            policy_ref=policy_ref,
        )
        self._store[artifact_id] = artifact
        return artifact

    def get(self, artifact_id: str) -> CodingArtifact:
        if artifact_id not in self._store:
            raise ArtifactError(f"unknown artifact_id: {artifact_id} (T001 Rule 1).")
        return self._store[artifact_id]

    def verify(self, artifact_id: str, policy_ok: bool = True) -> CodingArtifact:
        """Integrity gate (T078). Fail-closed: unverified -> REJECTED, never
        promoted to PASS. Deterministic: same artifact + verifier -> same status.
        """
        artifact = self.get(artifact_id)
        if not policy_ok:
            artifact.status = ArtifactStatus.REJECTED
            artifact.integrity_verified = False
            raise ArtifactError("Policy rejected artifact (T113).")
        # Integrity check: recompute hash and confirm evidence chain present.
        if _hash(artifact.content) != artifact.content_hash:
            artifact.status = ArtifactStatus.REJECTED
            artifact.integrity_verified = False
            raise ArtifactError("content_hash mismatch (T078).")
        if not artifact.evidence_chain:
            artifact.status = ArtifactStatus.REJECTED
            artifact.integrity_verified = False
            raise ArtifactError("missing provenance chain (T001 Rule 5).")
        artifact.integrity_verified = True
        artifact.status = ArtifactStatus.VERIFIED
        return artifact
