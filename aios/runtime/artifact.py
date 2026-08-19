"""Content-addressable artifacts with checksum + version (TASK-004, M1).

An :class:`Artifact` is an immutable blob (config, model output, workflow
definition, evidence payload, ...) addressed by a content ``checksum`` (SHA-256)
and a :class:`~aios.core.version.SemVer` ``version``. The store enforces
integrity on write (checksum must match the bytes) and supports version listing
and latest-version resolution.

This module depends only on the standard library and ``aios.core.version``
(``unknown`` layer, allowed from ``runtime``). It never reaches into
agent/orchestrator layers.
"""

from __future__ import annotations

import hashlib
import threading
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from aios.core.version import SemVer, VersionError


__all__ = ["ArtifactError", "Artifact", "ArtifactStore"]


class ArtifactError(Exception):
    """Raised on artifact validation or storage errors."""


@dataclass
class Artifact:
    """An immutable, content-addressed artifact."""

    artifact_id: str
    name: str
    content_type: str
    version: str
    content: bytes
    checksum: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        name: str,
        content: bytes,
        content_type: str = "application/octet-stream",
        version: str = "0.1.0",
        artifact_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Artifact":
        """Build an artifact, normalizing ``content`` to bytes and validating."""
        if isinstance(content, str):
            data = content.encode("utf-8")
        elif isinstance(content, (bytes, bytearray)):
            data = bytes(content)
        else:
            raise ArtifactError(
                "Artifact content must be str or bytes, got "
                f"{type(content).__name__}"
            )
        try:
            SemVer.parse(version)
        except VersionError as exc:
            raise ArtifactError(f"Invalid artifact version {version!r}: {exc}") from exc
        checksum = hashlib.sha256(data).hexdigest()
        return cls(
            artifact_id=artifact_id or f"art-{uuid.uuid4().hex[:12]}",
            name=name,
            content_type=content_type,
            version=version,
            content=data,
            checksum=checksum,
            metadata=dict(metadata or {}),
        )

    def verify(self) -> bool:
        """Return True iff the stored checksum matches the current bytes."""
        return hashlib.sha256(self.content).hexdigest() == self.checksum

    @property
    def semver(self) -> SemVer:
        return SemVer.parse(self.version)


class ArtifactStore:
    """Thread-safe store for artifacts keyed by id and grouped by name."""

    def __init__(self) -> None:
        self._store: Dict[str, Artifact] = {}
        self._by_name: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.RLock()

    def put(self, artifact: Artifact) -> None:
        """Store an artifact, re-verifying integrity on write."""
        if not isinstance(artifact, Artifact):
            raise ArtifactError("ArtifactStore only holds Artifact")
        if not artifact.verify():
            raise ArtifactError(
                f"Checksum mismatch for artifact {artifact.artifact_id!r} "
                f"(expected {artifact.checksum})"
            )
        with self._lock:
            if artifact.artifact_id in self._store:
                raise ArtifactError(
                    f"Artifact id already exists: {artifact.artifact_id!r}"
                )
            self._store[artifact.artifact_id] = artifact
            if artifact.artifact_id not in self._by_name[artifact.name]:
                self._by_name[artifact.name].append(artifact.artifact_id)

    def get(self, artifact_id: str) -> Artifact:
        with self._lock:
            art = self._store.get(artifact_id)
        if art is None:
            raise ArtifactError(f"Artifact not found: {artifact_id!r}")
        return art

    def exists(self, artifact_id: str) -> bool:
        with self._lock:
            return artifact_id in self._store

    def versions(self, name: str) -> List[Artifact]:
        """Return all artifacts for ``name`` sorted by SemVer ascending."""
        with self._lock:
            ids = list(self._by_name.get(name, []))
        artifacts = [self._store[i] for i in ids]
        return sorted(artifacts, key=lambda a: a.semver)

    def get_latest(self, name: str) -> Optional[Artifact]:
        """Return the highest-version artifact for ``name`` (or None)."""
        vers = self.versions(name)
        return vers[-1] if vers else None

    def delete(self, artifact_id: str) -> None:
        with self._lock:
            art = self._store.pop(artifact_id, None)
            if art is None:
                return
            if artifact_id in self._by_name[art.name]:
                self._by_name[art.name].remove(artifact_id)

    def verify_all(self) -> bool:
        """Return True iff every stored artifact's checksum is valid."""
        with self._lock:
            items = list(self._store.values())
        return all(a.verify() for a in items)

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)
