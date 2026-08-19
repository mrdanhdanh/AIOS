"""Package metadata and build info for runtime self-description.

:func:`PackageMetadata.current` returns a snapshot of the current build
including version, name, Python version, and an optional commit hash.
"""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass, field
from typing import Optional

__all__ = ["PackageMetadata", "BuildInfo"]


@dataclass(frozen=True)
class BuildInfo:
    """Immutable build-time information."""

    commit_hash: str = "unknown"
    build_id: str = "local"
    build_timestamp: str = ""


@dataclass(frozen=True)
class PackageMetadata:
    """Structured package metadata.

    Fields mirror the values in ``pyproject.toml`` and the runtime
    environment so that evidence records can link a run to a specific
    version.
    """

    name: str
    version: str
    python_version: str
    description: str = ""
    commit_hash: str = "unknown"
    build_info: BuildInfo = field(default_factory=BuildInfo)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------
    @classmethod
    def current(cls) -> PackageMetadata:
        """Return metadata for the installed ``aios`` package.

        Reads version from the package-level ``__version__`` attribute.
        Falls back to ``"0.0.0-dev"`` if the attribute is missing.
        """
        # Lazy import to avoid circular dependency at module level.
        try:
            from aios import __version__  # type: ignore[attr-defined]
        except ImportError:
            __version__ = "0.0.0-dev"  # type: ignore[assignment]

        try:
            from aios import __milestone__  # type: ignore[attr-defined]
        except ImportError:
            __milestone__ = "unknown"  # type: ignore[assignment]

        desc = (
            "Runtime-First, Plugin-First, Offline-First "
            "AI Operating System"
        )

        return cls(
            name="aios",
            version=str(__version__),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            description=desc,
            commit_hash=_read_commit_hash(),
            build_info=BuildInfo(
                commit_hash=_read_commit_hash(),
                build_id="local",
            ),
        )

    # ------------------------------------------------------------------
    def as_dict(self) -> dict:
        """Serialise to a plain dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "python_version": self.python_version,
            "description": self.description,
            "commit_hash": self.commit_hash,
            "build_info": {
                "commit_hash": self.build_info.commit_hash,
                "build_id": self.build_info.build_id,
                "build_timestamp": self.build_info.build_timestamp,
            },
        }


def _read_commit_hash() -> str:
    """Best-effort read of the current git HEAD commit hash."""
    import os
    from pathlib import Path

    git_head = Path(os.getcwd()) / ".git" / "HEAD"
    if not git_head.exists():
        return "unknown"
    try:
        raw = git_head.read_text().strip()
        if raw.startswith("ref: "):
            # Detached HEAD or symbolic ref — resolve the ref file.
            ref_path = Path(os.getcwd()) / ".git" / raw[5:]
            if ref_path.exists():
                return ref_path.read_text().strip()[:12]
        return raw[:12]
    except Exception:
        return "unknown"
