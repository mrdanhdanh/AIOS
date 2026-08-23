"""Repository Scanner (TASK-117, M18).

Walks a repository, collects artifact metadata (path/size/type/content_hash,
T078), detects changes against a previous scan, and enforces a secret boundary
(T040/T113). Deterministic: same repo state -> same ScanResult. Fail-closed: a
file that cannot be hashed is rejected (T078). Every scan carries provenance
(T001 Rule 5).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from aios.governance.evidence.store import EvidenceStore

from .common import ContextError, SecretBoundary, emit_evidence, sha256


__all__ = ["ScanError", "ScannedFile", "ChangeSet", "ScanResult", "RepositoryScanner"]


class ScanError(ContextError):
    """Raised when a scan invariant is violated (fail-closed, T078)."""


@dataclass
class ScannedFile:
    path: str
    size: int
    file_type: str
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "size": self.size,
            "file_type": self.file_type,
            "content_hash": self.content_hash,
        }


@dataclass
class ChangeSet:
    new: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"new": self.new, "modified": self.modified, "deleted": self.deleted}


@dataclass
class ScanResult:
    repo_ref: str
    files: list[ScannedFile]
    scan_id: str
    changed_files: ChangeSet
    policy_ref: str
    evidence_ref: str
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_ref": self.repo_ref,
            "files": [f.to_dict() for f in self.files],
            "scan_id": self.scan_id,
            "changed_files": self.changed_files.to_dict(),
            "policy_ref": self.policy_ref,
            "evidence_ref": self.evidence_ref,
            "content_hash": self.content_hash,
        }


# Default ignore patterns (gitignore-style, simplified).
DEFAULT_IGNORE = (
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    "build",
    "dist",
    ".mypy_cache",
    ".ruff_cache",
    ".eggs",
    "*.pyc",
    "*.pyo",
)


def _default_reader(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


class RepositoryScanner:
    """File walk + artifact metadata + change detection + policy boundary."""

    def __init__(
        self,
        *,
        evidence_store: Optional[EvidenceStore] = None,
        run_id: str = "run-context",
        task_id: str = "TASK-117",
        producer: str = "context.scanner",
        file_reader: Optional[Callable[[str], bytes]] = None,
        ignore: tuple[str, ...] = DEFAULT_IGNORE,
    ) -> None:
        self._store = evidence_store or EvidenceStore()
        self._run_id = run_id
        self._task_id = task_id
        self._producer = producer
        self._reader = file_reader or _default_reader
        self._ignore = ignore

    # -- helpers -------------------------------------------------------- #
    def _is_ignored(self, name: str) -> bool:
        if name in self._ignore:
            return True
        return any(name.endswith(ext.lstrip("*")) for ext in self._ignore if ext.startswith("*"))

    @staticmethod
    def _file_type(path: str) -> str:
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        return ext or "txt"

    def _hash_file(self, path: str) -> str:
        try:
            data = self._reader(path)
        except OSError as exc:
            raise ScanError(f"cannot read file '{path}': {exc}") from exc
        return sha256(data)

    # -- scan ----------------------------------------------------------- #
    def scan(self, repo_path: str, *, policy_ref: str = "pol-context-scan") -> ScanResult:
        repo_path = os.path.abspath(repo_path)
        if not os.path.isdir(repo_path):
            raise ScanError(f"repo path is not a directory: {repo_path}")
        files: list[ScannedFile] = []
        for root, dirs, names in os.walk(repo_path):
            # Prune ignored directories in-place.
            dirs[:] = [d for d in dirs if d not in self._ignore]
            for name in sorted(names):
                full = os.path.join(root, name)
                rel = os.path.relpath(full, repo_path).replace(os.sep, "/")
                if self._is_ignored(name):
                    continue
                # Secret isolation: never read/hash/leak secret files (T040).
                if SecretBoundary.is_secret_path(rel):
                    continue
                if not os.path.isfile(full):
                    continue
                size = os.path.getsize(full)
                ftype = self._file_type(full)
                content_hash = self._hash_file(full)
                files.append(
                    ScannedFile(path=rel, size=size, file_type=ftype, content_hash=content_hash)
                )
        files.sort(key=lambda f: f.path)
        canonical = "\n".join(f"{f.path}\t{f.content_hash}" for f in files)
        overall = sha256(canonical)
        scan_id = f"scan-{overall[:16]}"  # deterministic + immutable per repo state
        evidence_ref = emit_evidence(
            self._store,
            task_id=self._task_id,
            run_id=self._run_id,
            producer=self._producer,
            type_="scan",
            source=repo_path,
            content=canonical,
        )
        return ScanResult(
            repo_ref=repo_path,
            files=files,
            scan_id=scan_id,
            changed_files=ChangeSet(),
            policy_ref=policy_ref,
            evidence_ref=evidence_ref,
            content_hash=overall,
        )

    def diff(self, previous: ScanResult, current: ScanResult) -> ChangeSet:
        """Detect new/modified/deleted files between two scans (deterministic)."""
        prev = {f.path: f.content_hash for f in previous.files}
        cur = {f.path: f.content_hash for f in current.files}
        new = sorted(p for p in cur if p not in prev)
        deleted = sorted(p for p in prev if p not in cur)
        modified = sorted(p for p in cur if p in prev and cur[p] != prev[p])
        return ChangeSet(new=new, modified=modified, deleted=deleted)
