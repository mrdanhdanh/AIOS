"""Output + Artifact Collector (TASK-141, M20).

Collects stdout/stderr/log output and artifacts from test/build/lint runs
(T139/T140) into provenance-bearing artifacts. Every output/artifact carries a
``content_hash`` (T078) and provenance (T001 Rule 5). Secret isolation: secrets
are redacted (T040/T113). Fail-closed: output that cannot be hashed is rejected.

Layering: ``execution`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from aios.execution._common import ExecutionError, _hash

# Lightweight secret redaction (T040/T113). Mirrors aios.security.secrets.redact_message.
_SECRET_TOKENS = ("password", "token", "secret", "api_key", "apikey", "authorization")


def redact(text: str) -> str:
    """Return a redacted copy of ``text`` if it looks secret-bearing (T040/T113)."""
    low = text.lower()
    for tok in _SECRET_TOKENS:
        if tok in low:
            return "[REDACTED]"
    return text


@dataclass
class OutputCapture:
    """A single captured output stream with integrity hash (T141)."""

    kind: str  # stdout | stderr | log
    content: str
    content_hash: str

    def __post_init__(self) -> None:
        if not self.content_hash:
            raise ExecutionError("OutputCapture requires content_hash (T078).")


@dataclass
class CollectedArtifact:
    """Collected outputs + artifacts from a run (T141)."""

    run_ref: str
    outputs: List[OutputCapture] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)  # artifact refs (T130)
    collector_id: str = field(default_factory=lambda: f"col-{uuid.uuid4().hex[:12]}")
    policy_ref: Optional[str] = None
    evidence_ref: str = field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:12]}")

    def __post_init__(self) -> None:
        if not self.run_ref:
            raise ExecutionError("run_ref required (T139/T140).")
        if not self.collector_id:
            raise ExecutionError("collector_id required (T001 Rule 1, immutable).")

    def content_hash(self) -> str:
        # Fail-closed: an artifact with nothing collected has no integrity hash.
        if not self.outputs and not self.artifacts:
            return ""
        parts = [f"{o.kind}:{o.content_hash}" for o in self.outputs]
        parts += [f"a:{a}" for a in self.artifacts]
        return _hash("|".join(parts))


class OutputArtifactCollector:
    """Collects run output/artifacts with secret isolation (T141)."""

    def __init__(self, policy_ref: Optional[str] = None) -> None:
        self._policy_ref = policy_ref

    def capture_output(self, run_ref: str, kind: str, content: str) -> OutputCapture:
        # Fail-closed: cannot hash empty output (T078).
        if not content:
            raise ExecutionError("Cannot hash empty output (fail-closed, T078).")
        # Redact before storing so secrets never leak (T040/T113).
        safe = redact(content)
        return OutputCapture(kind=kind, content=safe, content_hash=_hash(safe))

    def collect(
        self,
        run_ref: str,
        outputs: List[OutputCapture],
        artifact_refs: Tuple[str, ...] = (),
    ) -> CollectedArtifact:
        return CollectedArtifact(
            run_ref=run_ref,
            outputs=list(outputs),
            artifacts=list(artifact_refs),
            policy_ref=self._policy_ref,
        )

    def provenance(self, art: CollectedArtifact) -> dict:
        return {
            "collector_id": art.collector_id,
            "run_ref": art.run_ref,
            "policy_ref": art.policy_ref,
            "evidence_ref": art.evidence_ref,
            "output_count": len(art.outputs),
            "artifact_count": len(art.artifacts),
            "content_hash": art.content_hash(),
        }
