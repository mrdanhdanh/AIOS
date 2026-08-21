"""Skill contracts — versioned interfaces (TASK-015, M2).

Defines SkillContract, SkillDependency, SkillStatus, SkillPersistentState,
SkillTransition and validation. All Skill metadata is validated here so
registry, resolver and manager can fail-closed on invalid contracts.

Layering: ``skill`` layer — stdlib + ``aios.core`` only.
Never imports ``runtime`` / ``agent`` / ``orchestrator`` / ``capability`` / ``tool``.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.core.contracts import Contract, check_compatibility
from aios.core.version import SemVer, VersionError

__all__ = [
    "SKILL_CONTRACT",
    "SkillStatus",
    "SkillTransition",
    "SkillDependency",
    "SkillContract",
    "SkillPersistentState",
    "SkillError",
    "check_skill_contracts",
    "VALID_TRANSITIONS",
]

# ---------------------------------------------------------------------------
# Contracts
# ---------------------------------------------------------------------------

SKILL_CONTRACT = Contract(
    name="skill.registry",
    version_range=">=1.0.0,<2.0.0",
    description="Skill registry — lifecycle + dependency + sandbox (TASK-015).",
)

_SKILL_VERSION = "1.0.0"


def check_skill_contracts(version: str | None = None) -> None:
    """Verify skill contract against ``version`` (or 1.0.0)."""
    ver = version or _SKILL_VERSION
    check_compatibility(SKILL_CONTRACT, ver)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SkillStatus(str, Enum):
    """Lifecycle statuses for a Skill."""

    PENDING = "pending"
    RESOLVED = "resolved"
    VALIDATED = "validated"
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNLOADED = "unloaded"
    FAILED = "failed"
    BLOCKED = "blocked"

    @classmethod
    def all(cls) -> List["SkillStatus"]:
        return list(cls)


class SkillTransition(str, Enum):
    """Canonical lifecycle transitions."""

    RESOLVE = "resolve"
    VALIDATE = "validate"
    INSTALL = "install"
    ENABLE = "enable"
    DISABLE = "disable"
    UNLOAD = "unload"
    RELOAD = "reload"
    UPGRADE = "upgrade"
    ROLLBACK = "rollback"
    REMOVE = "remove"


# Valid transitions per spec §2.2 — deterministic, fail-closed.
# Key: current status, Value: set of allowed target statuses.
VALID_TRANSITIONS: Dict[SkillStatus, set] = {
    SkillStatus.PENDING: {SkillStatus.RESOLVED, SkillStatus.VALIDATED, SkillStatus.INSTALLED, SkillStatus.FAILED, SkillStatus.BLOCKED},
    SkillStatus.RESOLVED: {SkillStatus.VALIDATED, SkillStatus.FAILED, SkillStatus.BLOCKED},
    SkillStatus.VALIDATED: {SkillStatus.INSTALLED, SkillStatus.FAILED, SkillStatus.BLOCKED},
    SkillStatus.INSTALLED: {SkillStatus.ENABLED, SkillStatus.DISABLED, SkillStatus.FAILED, SkillStatus.BLOCKED},
    SkillStatus.ENABLED: {SkillStatus.DISABLED, SkillStatus.UNLOADED, SkillStatus.FAILED, SkillStatus.BLOCKED, SkillStatus.ENABLED},  # ENABLED→ENABLED for upgrade
    SkillStatus.DISABLED: {SkillStatus.ENABLED, SkillStatus.UNLOADED, SkillStatus.FAILED, SkillStatus.BLOCKED},
    SkillStatus.UNLOADED: {SkillStatus.ENABLED, SkillStatus.INSTALLED, SkillStatus.DISABLED, SkillStatus.FAILED, SkillStatus.BLOCKED},
    SkillStatus.FAILED: {SkillStatus.DISABLED, SkillStatus.ENABLED, SkillStatus.INSTALLED, SkillStatus.BLOCKED, SkillStatus.FAILED},
    SkillStatus.BLOCKED: {SkillStatus.DISABLED, SkillStatus.FAILED, SkillStatus.PENDING},
}

# Transition name → (from_statuses, to_status) for validation
TRANSITION_MAP: Dict[SkillTransition, tuple] = {
    SkillTransition.RESOLVE: ({SkillStatus.PENDING}, SkillStatus.RESOLVED),
    SkillTransition.VALIDATE: ({SkillStatus.PENDING, SkillStatus.RESOLVED, SkillStatus.INSTALLED, SkillStatus.ENABLED, SkillStatus.DISABLED, SkillStatus.UNLOADED, SkillStatus.FAILED}, SkillStatus.VALIDATED),
    SkillTransition.INSTALL: ({SkillStatus.PENDING, SkillStatus.VALIDATED, SkillStatus.RESOLVED, SkillStatus.FAILED}, SkillStatus.INSTALLED),
    SkillTransition.ENABLE: ({SkillStatus.INSTALLED, SkillStatus.DISABLED, SkillStatus.UNLOADED, SkillStatus.FAILED}, SkillStatus.ENABLED),
    SkillTransition.DISABLE: ({SkillStatus.ENABLED}, SkillStatus.DISABLED),
    SkillTransition.UNLOAD: ({SkillStatus.ENABLED, SkillStatus.DISABLED}, SkillStatus.UNLOADED),
    SkillTransition.RELOAD: ({SkillStatus.UNLOADED, SkillStatus.DISABLED, SkillStatus.FAILED}, SkillStatus.ENABLED),
    SkillTransition.UPGRADE: ({SkillStatus.ENABLED, SkillStatus.INSTALLED, SkillStatus.DISABLED}, SkillStatus.ENABLED),
    SkillTransition.ROLLBACK: ({SkillStatus.FAILED, SkillStatus.ENABLED, SkillStatus.BLOCKED}, SkillStatus.ENABLED),
    SkillTransition.REMOVE: ({SkillStatus.DISABLED, SkillStatus.UNLOADED, SkillStatus.FAILED, SkillStatus.BLOCKED, SkillStatus.INSTALLED}, SkillStatus.PENDING),
}


# ---------------------------------------------------------------------------
# Validation vocabularies
# ---------------------------------------------------------------------------

_SKILL_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_\-\.]*$")
_CAP_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_\.\-]*$")
_ENTRYPOINT_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_\.]*:[a-zA-Z_][a-zA-Z0-9_]*$|^[a-zA-Z_][a-zA-Z0-9_\./]*\.py$|^[a-zA-Z0-9_\-\./]+$")

ALLOWED_PERMISSIONS = {
    "filesystem.read",
    "filesystem.write",
    "process.execute",
    "network.read",
    "network.write",
    "capability:invoke",
    "tool:invoke",
    "memory:read",
    "memory:write",
    "skill:invoke",
    "skill:manage",
}

ALLOWED_RUNTIMES = {
    "python3.11",
    "python3.10",
    "python3.9",
    "python",
    "node18",
    "node20",
    "docker",
    "shell",
    "generic",
}


class SkillError(Exception):
    """Raised on skill validation or lifecycle errors."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _compute_checksum(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# SkillDependency
# ---------------------------------------------------------------------------

@dataclass
class SkillDependency:
    """A dependency declaration for a Skill."""

    skill_id: str
    version_constraint: str = ">=1.0.0"

    def validate(self) -> None:
        if not isinstance(self.skill_id, str) or not self.skill_id.strip():
            raise SkillError("dependency skill_id must be non-empty string")
        if not _SKILL_ID_RE.match(self.skill_id):
            raise SkillError(f"dependency skill_id {self.skill_id!r} must match {_SKILL_ID_RE.pattern}")
        if not isinstance(self.version_constraint, str) or not self.version_constraint.strip():
            raise SkillError("version_constraint must be non-empty string")
        # Validate constraint syntax — support >=, ==, ~=, <, >, <=, !=, ^, ~
        # We accept comma-separated constraints like ">=1.2.0,<2.0.0" or ">=1.2" or "~=2.0"
        constraint = self.version_constraint.strip()
        # Simple validation: try to parse as semver range or single constraint
        # Allow: ">=1.2.0", "==1.0.0", "~=2.0", ">=1.2.0,<2.0.0", "^1.2.3", "~1.2.3"
        parts = [p.strip() for p in constraint.split(",")]
        for part in parts:
            if not part:
                raise SkillError(f"empty version constraint part in {constraint!r}")
            # Extract operator and version
            m = re.match(r"^(>=|<=|==|!=|~=|\^|~|>|<|=)?\s*(.+)$", part)
            if not m:
                raise SkillError(f"invalid version constraint {part!r}")
            op, ver = m.group(1) or "==", m.group(2).strip()
            # Normalize ~= and ^ and ~ to semver
            # For ~=2.0, we treat as >=2.0,<3.0 ; for ^1.2.3 as >=1.2.3,<2.0.0
            # But for validation, just check ver is semver-like
            # Allow short versions like "1.2" → normalize to "1.2.0"
            ver_parts = ver.split(".")
            if len(ver_parts) == 2:
                ver = f"{ver}.0"
            elif len(ver_parts) == 1:
                ver = f"{ver}.0.0"
            try:
                SemVer.parse(ver)
            except VersionError as exc:
                raise SkillError(f"Invalid version in constraint {part!r}: {exc}") from exc

    def is_satisfied_by(self, version: str) -> bool:
        """Check if ``version`` satisfies this dependency constraint."""
        try:
            v = SemVer.parse(version)
        except VersionError:
            return False
        constraint = self.version_constraint.strip()
        parts = [p.strip() for p in constraint.split(",")]
        for part in parts:
            m = re.match(r"^(>=|<=|==|!=|~=|\^|~|>|<|=)?\s*(.+)$", part)
            if not m:
                return False
            op, ver_str = m.group(1) or "==", m.group(2).strip()
            ver_parts = ver_str.split(".")
            if len(ver_parts) == 2:
                ver_str = f"{ver_str}.0"
            elif len(ver_parts) == 1:
                ver_str = f"{ver_str}.0.0"
            try:
                cv = SemVer.parse(ver_str)
            except VersionError:
                return False
            # Evaluate
            if op in ("==", "=", ""):
                if not (v == cv):
                    return False
            elif op == "!=":
                if not (v != cv):
                    return False
            elif op == ">=":
                if not (v >= cv):
                    return False
            elif op == "<=":
                if not (v <= cv):
                    return False
            elif op == ">":
                if not (v > cv):
                    return False
            elif op == "<":
                if not (v < cv):
                    return False
            elif op == "~=":
                # Compatible release: ~=2.0 means >=2.0,<3.0 ; ~=1.4.2 means >=1.4.2,<1.5.0
                # Simplified: major must match, minor >=
                orig_parts = ver_str.split(".")
                # Use original ver_str before normalization? Use cv
                # For ~=X.Y → >=X.Y,<X+1.0 ; for ~=X.Y.Z → >=X.Y.Z,<X.Y+1.0
                # We need original constraint version string
                raw_ver = m.group(2).strip()
                raw_parts = raw_ver.split(".")
                if len(raw_parts) == 2:
                    # ~=2.0 → >=2.0,<3.0
                    if not (v >= cv and v.major == cv.major):
                        return False
                elif len(raw_parts) >= 3:
                    # ~=1.4.2 → >=1.4.2,<1.5.0
                    if not (v >= cv and v.major == cv.major and v.minor == cv.minor):
                        return False
                else:
                    if not (v >= cv):
                        return False
            elif op == "^":
                # ^1.2.3 → >=1.2.3,<2.0.0 ; ^0.2.3 → >=0.2.3,<0.3.0
                if cv.major != 0:
                    if not (v >= cv and v.major == cv.major):
                        return False
                elif cv.minor != 0:
                    if not (v >= cv and v.major == 0 and v.minor == cv.minor):
                        return False
                else:
                    if not (v >= cv and v.major == 0 and v.minor == 0 and v.patch == cv.patch):
                        return False
            elif op == "~":
                # ~1.2.3 → >=1.2.3,<1.3.0
                if not (v >= cv and v.major == cv.major and v.minor == cv.minor):
                    return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {"skill_id": self.skill_id, "version_constraint": self.version_constraint}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillDependency":
        if not isinstance(data, dict):
            raise SkillError("dependency data must be mapping")
        obj = cls(skill_id=data.get("skill_id", ""), version_constraint=data.get("version_constraint", ">=1.0.0"))
        obj.validate()
        return obj


# ---------------------------------------------------------------------------
# SkillContract
# ---------------------------------------------------------------------------

@dataclass
class SkillContract:
    """Skill manifest / contract per TASK-015 §2.1."""

    skill_id: str
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    dependencies: List[SkillDependency] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)
    runtime: str = "python3.11"
    entrypoint: str = ""
    checksum: str = ""
    status: SkillStatus | str = SkillStatus.PENDING
    enabled: bool = False
    install_source: str = ""
    install_location: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        skill_id: str,
        name: str = "",
        version: str = "1.0.0",
        description: str = "",
        author: str = "",
        dependencies: Optional[List[SkillDependency | Dict[str, Any]]] = None,
        deps: Optional[List[str]] = None,
        required_capabilities: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        resources: Optional[Dict[str, Any]] = None,
        runtime: str = "python3.11",
        entrypoint: str = "",
        checksum: str = "",
        status: SkillStatus | str = SkillStatus.PENDING,
        enabled: bool = False,
        install_source: str = "",
        install_location: str = "",
        configuration: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "SkillContract":
        # Normalize dependencies. ``dependencies`` accepts full objects/dicts/
        # strings; ``deps`` is a convenience alias accepting plain skill_id
        # strings.
        resolved_deps: List[SkillDependency] = []
        for d in (dependencies or []):
            if isinstance(d, SkillDependency):
                resolved_deps.append(d)
            elif isinstance(d, dict):
                resolved_deps.append(SkillDependency.from_dict(d))
            elif isinstance(d, str):
                resolved_deps.append(SkillDependency(skill_id=d))
            else:
                raise SkillError(f"invalid dependency {d!r}")
        for d in (deps or []):
            if isinstance(d, str):
                resolved_deps.append(SkillDependency(skill_id=d))
            else:
                raise SkillError(f"invalid dependency {d!r}")
        # Normalize status
        if isinstance(status, str):
            try:
                status = SkillStatus(status)
            except ValueError as exc:
                raise SkillError(f"Unknown status {status!r}") from exc
        obj = cls(
            skill_id=skill_id,
            name=name or skill_id,
            version=version,
            description=description or "",
            author=author or "",
            dependencies=resolved_deps,
            required_capabilities=list(required_capabilities or []),
            permissions=list(permissions or []),
            resources=dict(resources or {}),
            runtime=runtime,
            entrypoint=entrypoint or "",
            checksum=checksum or "",
            status=status,
            enabled=enabled,
            install_source=install_source or "",
            install_location=install_location or "",
            configuration=dict(configuration or {}),
            metadata=dict(metadata or {}),
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if not isinstance(self.skill_id, str) or not self.skill_id.strip():
            raise SkillError("skill_id must be non-empty string")
        if not _SKILL_ID_RE.match(self.skill_id):
            raise SkillError(f"skill_id {self.skill_id!r} must match {_SKILL_ID_RE.pattern}")
        if not isinstance(self.name, str) or not self.name.strip():
            raise SkillError("name must be non-empty string")
        try:
            SemVer.parse(self.version)
        except VersionError as exc:
            raise SkillError(f"Invalid version {self.version!r}: {exc}") from exc
        if not isinstance(self.description, str):
            raise SkillError("description must be string")
        if not isinstance(self.author, str):
            raise SkillError("author must be string")
        if not isinstance(self.dependencies, list):
            raise SkillError("dependencies must be list")
        for dep in self.dependencies:
            if not isinstance(dep, SkillDependency):
                raise SkillError(f"dependency must be SkillDependency, got {type(dep).__name__}")
            dep.validate()
        if not isinstance(self.required_capabilities, list):
            raise SkillError("required_capabilities must be list")
        for cap in self.required_capabilities:
            if not isinstance(cap, str) or not cap.strip():
                raise SkillError(f"capability {cap!r} must be non-empty string")
            if not _CAP_ID_RE.match(cap):
                raise SkillError(f"capability {cap!r} must match {_CAP_ID_RE.pattern}")
        if not isinstance(self.permissions, list):
            raise SkillError("permissions must be list")
        for p in self.permissions:
            if not isinstance(p, str) or not p.strip():
                raise SkillError(f"permission {p!r} must be non-empty string")
            if p not in ALLOWED_PERMISSIONS:
                raise SkillError(f"permission {p!r} not in allowed {sorted(ALLOWED_PERMISSIONS)}")
        if not isinstance(self.resources, dict):
            raise SkillError("resources must be mapping")
        if self.resources:
            cpu = self.resources.get("cpu")
            mem = self.resources.get("memory_mb") or self.resources.get("memory")
            if cpu is not None:
                if not isinstance(cpu, int) or cpu <= 0:
                    raise SkillError(f"resources.cpu must be positive int, got {cpu!r}")
            if mem is not None:
                if isinstance(mem, str):
                    if not re.match(r"^\d+(KB|MB|GB)$", mem):
                        # Also allow int
                        raise SkillError(f"resources.memory must be int or <int><KB|MB|GB>, got {mem!r}")
                elif isinstance(mem, int):
                    if mem <= 0:
                        raise SkillError(f"resources.memory_mb must be positive int, got {mem!r}")
                else:
                    raise SkillError(f"resources.memory must be int or string, got {type(mem).__name__}")
        if not isinstance(self.runtime, str) or not self.runtime.strip():
            raise SkillError("runtime must be non-empty string")
        # Runtime validation — allow any non-empty, but warn if not in allowed
        # For strictness, we allow any but check if in allowed set or generic
        if self.runtime not in ALLOWED_RUNTIMES and self.runtime not in {"python", "generic"}:
            # Allow custom runtimes but must be non-empty string
            pass
        if not isinstance(self.entrypoint, str):
            raise SkillError("entrypoint must be string")
        if self.entrypoint and not _ENTRYPOINT_RE.match(self.entrypoint):
            # Allow empty, but if provided must look like entrypoint
            # Be lenient: any non-empty string with / or : or .py is ok
            if "/" not in self.entrypoint and ":" not in self.entrypoint and "." not in self.entrypoint:
                raise SkillError(f"entrypoint {self.entrypoint!r} looks invalid")
        if not isinstance(self.checksum, str):
            raise SkillError("checksum must be string")
        if self.checksum and not re.match(r"^[a-fA-F0-9]{64}$", self.checksum):
            # Allow sha256 hex only; if provided must be 64 hex chars
            raise SkillError(f"checksum {self.checksum!r} must be sha256 hex (64 chars)")
        if isinstance(self.status, str):
            try:
                self.status = SkillStatus(self.status)
            except ValueError as exc:
                raise SkillError(f"Unknown status {self.status!r}") from exc
        if not isinstance(self.status, SkillStatus):
            raise SkillError(f"status must be SkillStatus, got {type(self.status).__name__}")
        if not isinstance(self.enabled, bool):
            raise SkillError("enabled must be bool")
        if not isinstance(self.install_source, str):
            raise SkillError("install_source must be string")
        if not isinstance(self.install_location, str):
            raise SkillError("install_location must be string")
        if not isinstance(self.configuration, dict):
            raise SkillError("configuration must be mapping")
        if not isinstance(self.metadata, dict):
            raise SkillError("metadata must be mapping")

    def compute_checksum(self) -> str:
        """Compute checksum from canonical content (id+version+entrypoint)."""
        payload = json.dumps(
            {
                "skill_id": self.skill_id,
                "version": self.version,
                "entrypoint": self.entrypoint,
                "dependencies": [d.to_dict() for d in self.dependencies],
                "required_capabilities": sorted(self.required_capabilities),
            },
            sort_keys=True,
        )
        return _compute_checksum(payload)

    def verify_checksum(self) -> bool:
        """Verify stored checksum matches computed (if checksum present)."""
        if not self.checksum:
            return False
        return self.checksum == self.compute_checksum()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "required_capabilities": list(self.required_capabilities),
            "permissions": list(self.permissions),
            "resources": dict(self.resources),
            "runtime": self.runtime,
            "entrypoint": self.entrypoint,
            "checksum": self.checksum,
            "status": self.status.value if isinstance(self.status, SkillStatus) else str(self.status),
            "enabled": self.enabled,
            "install_source": self.install_source,
            "install_location": self.install_location,
            "configuration": dict(self.configuration),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillContract":
        if not isinstance(data, dict):
            raise SkillError("skill contract data must be mapping")
        deps = []
        for d in data.get("dependencies", []):
            if isinstance(d, dict):
                deps.append(SkillDependency.from_dict(d))
            elif isinstance(d, SkillDependency):
                deps.append(d)
        status = data.get("status", "pending")
        if isinstance(status, str):
            try:
                status = SkillStatus(status)
            except ValueError:
                status = SkillStatus.PENDING
        return cls.create(
            skill_id=data.get("skill_id", ""),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            dependencies=deps,
            required_capabilities=data.get("required_capabilities", []),
            permissions=data.get("permissions", []),
            resources=data.get("resources", {}),
            runtime=data.get("runtime", "python3.11"),
            entrypoint=data.get("entrypoint", ""),
            checksum=data.get("checksum", ""),
            status=status,
            enabled=bool(data.get("enabled", False)),
            install_source=data.get("install_source", ""),
            install_location=data.get("install_location", ""),
            configuration=data.get("configuration", {}),
            metadata=data.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# SkillPersistentState
# ---------------------------------------------------------------------------

@dataclass
class SkillPersistentState:
    """Persistent state that survives restart per TASK-015 §5."""

    skill_id: str
    version: str = "1.0.0"
    status: SkillStatus | str = SkillStatus.PENDING
    enabled: bool = False
    dependencies: List[Dict[str, Any]] = field(default_factory=list)
    checksum: str = ""
    install_source: str = ""
    install_location: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)
    last_transition: str = ""
    last_health: str = "unknown"
    previous_certified_version: str = ""
    updated_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            try:
                self.status = SkillStatus(self.status)
            except ValueError:
                self.status = SkillStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "status": self.status.value if isinstance(self.status, SkillStatus) else str(self.status),
            "enabled": self.enabled,
            "dependencies": list(self.dependencies),
            "checksum": self.checksum,
            "install_source": self.install_source,
            "install_location": self.install_location,
            "configuration": dict(self.configuration),
            "last_transition": self.last_transition,
            "last_health": self.last_health,
            "previous_certified_version": self.previous_certified_version,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillPersistentState":
        status = data.get("status", "pending")
        if isinstance(status, str):
            try:
                status = SkillStatus(status)
            except ValueError:
                status = SkillStatus.PENDING
        return cls(
            skill_id=data.get("skill_id", ""),
            version=data.get("version", "1.0.0"),
            status=status,
            enabled=bool(data.get("enabled", False)),
            dependencies=list(data.get("dependencies", [])),
            checksum=data.get("checksum", ""),
            install_source=data.get("install_source", ""),
            install_location=data.get("install_location", ""),
            configuration=dict(data.get("configuration", {})),
            last_transition=data.get("last_transition", ""),
            last_health=data.get("last_health", "unknown"),
            previous_certified_version=data.get("previous_certified_version", ""),
            updated_at=data.get("updated_at", _now()),
        )

    @classmethod
    def from_contract(cls, contract: SkillContract, last_transition: str = "", last_health: str = "unknown", previous_certified_version: str = "") -> "SkillPersistentState":
        return cls(
            skill_id=contract.skill_id,
            version=contract.version,
            status=contract.status,
            enabled=contract.enabled,
            dependencies=[d.to_dict() for d in contract.dependencies],
            checksum=contract.checksum,
            install_source=contract.install_source,
            install_location=contract.install_location,
            configuration=dict(contract.configuration),
            last_transition=last_transition,
            last_health=last_health,
            previous_certified_version=previous_certified_version,
            updated_at=_now(),
        )
