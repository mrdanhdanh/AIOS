"""Worker contracts — shared contract for all workers (TASK-013).

Defines WorkerContract, WorkerRequest, WorkerContext, WorkerResult,
WorkerEvidence and related enums. All four workers (General, Coder,
Doctor, SystemDoctor) share this contract.

Layering: ``worker`` layer — stdlib + ``aios.core`` + ``aios.capability``
+ ``aios.governance`` (unknown) only. Never imports ``runtime``/
``orchestrator``/``agent``/``tool``.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.core.version import SemVer, VersionError

__all__ = [
    "WorkerType",
    "WorkerResultStatus",
    "WorkerContract",
    "WorkerRequest",
    "WorkerContext",
    "WorkerResult",
    "WorkerEvidence",
    "WorkerError",
    "compute_hash",
]

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class WorkerType(str, Enum):
    GENERAL = "general"
    CODER = "coder"
    DOCTOR = "doctor"
    SYSTEM_DOCTOR = "system_doctor"


class WorkerResultStatus(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"
    PARTIAL = "PARTIAL"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_WORKER_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_\-]*$")
_CAP_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_\.\-]*$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class WorkerError(Exception):
    """Raised on worker contract validation or usage errors."""


# ---------------------------------------------------------------------------
# WorkerContract — 10 mandatory fields per T013 §3
# ---------------------------------------------------------------------------

@dataclass
class WorkerContract:
    """Shared contract for all workers.

    Mandatory fields (T013 §3):
        worker_id, worker_type, version, capabilities,
        input_schema, output_schema, lifecycle,
        execution_context, policy_context, evidence_contract
    """

    worker_id: str
    worker_type: WorkerType
    version: str = "1.0.0"
    capabilities: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    lifecycle: Dict[str, Any] = field(default_factory=dict)
    execution_context: Dict[str, Any] = field(default_factory=dict)
    policy_context: Dict[str, Any] = field(default_factory=dict)
    evidence_contract: Dict[str, Any] = field(default_factory=dict)
    # optional
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if isinstance(self.worker_type, str):
            try:
                self.worker_type = WorkerType(self.worker_type)
            except ValueError as exc:
                raise WorkerError(f"invalid worker_type {self.worker_type!r}") from exc

    @classmethod
    def create(
        cls,
        worker_id: str,
        worker_type: WorkerType | str,
        version: str = "1.0.0",
        capabilities: Optional[List[str]] = None,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        lifecycle: Optional[Dict[str, Any]] = None,
        execution_context: Optional[Dict[str, Any]] = None,
        policy_context: Optional[Dict[str, Any]] = None,
        evidence_contract: Optional[Dict[str, Any]] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "WorkerContract":
        if isinstance(worker_type, str):
            try:
                worker_type = WorkerType(worker_type)
            except ValueError as exc:
                raise WorkerError(f"invalid worker_type {worker_type!r}") from exc
        obj = cls(
            worker_id=worker_id,
            worker_type=worker_type,  # type: ignore
            version=version,
            capabilities=list(capabilities or []),
            input_schema=dict(input_schema or {}),
            output_schema=dict(output_schema or {}),
            lifecycle=dict(lifecycle or {}),
            execution_context=dict(execution_context or {}),
            policy_context=dict(policy_context or {}),
            evidence_contract=dict(evidence_contract or {}),
            description=description or "",
            metadata=dict(metadata or {}),
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if not isinstance(self.worker_id, str) or not self.worker_id.strip():
            raise WorkerError("worker_id must be non-empty string")
        if not _WORKER_ID_RE.match(self.worker_id):
            raise WorkerError(f"worker_id {self.worker_id!r} must match {_WORKER_ID_RE.pattern}")
        if not isinstance(self.worker_type, WorkerType):
            raise WorkerError(f"worker_type must be WorkerType, got {self.worker_type!r}")
        try:
            SemVer.parse(self.version)
        except VersionError as exc:
            raise WorkerError(f"Invalid version {self.version!r}: {exc}") from exc
        if not isinstance(self.capabilities, list):
            raise WorkerError("capabilities must be a list")
        for c in self.capabilities:
            if not isinstance(c, str) or not c.strip():
                raise WorkerError(f"capability {c!r} must be non-empty string")
            if not _CAP_ID_RE.match(c):
                raise WorkerError(f"capability {c!r} must match {_CAP_ID_RE.pattern}")
        # input_schema / output_schema must be dict (JSON schema like)
        for name, val in [
            ("input_schema", self.input_schema),
            ("output_schema", self.output_schema),
            ("lifecycle", self.lifecycle),
            ("execution_context", self.execution_context),
            ("policy_context", self.policy_context),
            ("evidence_contract", self.evidence_contract),
        ]:
            if not isinstance(val, dict):
                raise WorkerError(f"{name} must be a mapping")
        if not isinstance(self.description, str):
            raise WorkerError("description must be a string")
        if not isinstance(self.metadata, dict):
            raise WorkerError("metadata must be a mapping")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "worker_type": self.worker_type.value if isinstance(self.worker_type, WorkerType) else str(self.worker_type),
            "version": self.version,
            "capabilities": list(self.capabilities),
            "input_schema": dict(self.input_schema),
            "output_schema": dict(self.output_schema),
            "lifecycle": dict(self.lifecycle),
            "execution_context": dict(self.execution_context),
            "policy_context": dict(self.policy_context),
            "evidence_contract": dict(self.evidence_contract),
            "description": self.description,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkerContract":
        if not isinstance(data, dict):
            raise WorkerError("worker contract data must be a mapping")
        wid = data.get("worker_id")
        wtype = data.get("worker_type")
        if not wid or not isinstance(wid, str) or not wid.strip():
            raise WorkerError("worker_id must be non-empty string")
        if not wtype:
            raise WorkerError("worker_type is required")
        return cls.create(
            worker_id=wid,
            worker_type=wtype,
            version=data.get("version", "1.0.0"),
            capabilities=data.get("capabilities", []),
            input_schema=data.get("input_schema", {}),
            output_schema=data.get("output_schema", {}),
            lifecycle=data.get("lifecycle", {}),
            execution_context=data.get("execution_context", {}),
            policy_context=data.get("policy_context", {}),
            evidence_contract=data.get("evidence_contract", {}),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# WorkerRequest — input to a worker (T013 §4)
# ---------------------------------------------------------------------------

@dataclass
class WorkerRequest:
    """Input to a worker — already orchestrated, not raw user request."""

    task_id: str
    goal_id: Optional[str] = None
    objective: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    policy_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        task_id: str,
        objective: Optional[Dict[str, Any]] = None,
        goal_id: Optional[str] = None,
        allowed_capabilities: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        policy_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "WorkerRequest":
        constraints: Dict[str, Any] = {}
        if allowed_capabilities is not None:
            constraints["allowed_capabilities"] = list(allowed_capabilities)
        obj = cls(
            task_id=task_id,
            goal_id=goal_id,
            objective=dict(objective or {}),
            constraints=constraints,
            context=dict(context or {}),
            policy_context=dict(policy_context or {}),
            metadata=dict(metadata or {}),
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise WorkerError("task_id must be non-empty string")
        if self.goal_id is not None and (not isinstance(self.goal_id, str) or not self.goal_id.strip()):
            raise WorkerError("goal_id must be non-empty string if provided")
        if not isinstance(self.objective, dict):
            raise WorkerError("objective must be a mapping")
        if not isinstance(self.constraints, dict):
            raise WorkerError("constraints must be a mapping")
        if "allowed_capabilities" in self.constraints:
            ac = self.constraints["allowed_capabilities"]
            if not isinstance(ac, list):
                raise WorkerError("allowed_capabilities must be a list")
            for c in ac:
                if not isinstance(c, str) or not c.strip():
                    raise WorkerError(f"allowed_capability {c!r} must be non-empty string")
        if not isinstance(self.context, dict):
            raise WorkerError("context must be a mapping")
        if not isinstance(self.policy_context, dict):
            raise WorkerError("policy_context must be a mapping")

    @property
    def allowed_capabilities(self) -> List[str]:
        return list(self.constraints.get("allowed_capabilities", []))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "goal_id": self.goal_id,
            "objective": dict(self.objective),
            "constraints": dict(self.constraints),
            "context": dict(self.context),
            "policy_context": dict(self.policy_context),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkerRequest":
        if not isinstance(data, dict):
            raise WorkerError("worker request data must be a mapping")
        obj = cls(
            task_id=data.get("task_id", ""),
            goal_id=data.get("goal_id"),
            objective=dict(data.get("objective", {})),
            constraints=dict(data.get("constraints", {})),
            context=dict(data.get("context", {})),
            policy_context=dict(data.get("policy_context", {})),
            metadata=dict(data.get("metadata", {})),
            created_at=data.get("created_at", _now()),
        )
        obj.validate()
        return obj


# ---------------------------------------------------------------------------
# WorkerContext — execution context (T013 §8)
# ---------------------------------------------------------------------------

@dataclass
class WorkerContext:
    """Per-execution context — isolated, not self-expandable."""

    run_id: str
    task_id: str
    worker_id: str
    capability_scope: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        run_id: Optional[str] = None,
        task_id: str = "",
        worker_id: str = "",
        capability_scope: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "WorkerContext":
        obj = cls(
            run_id=run_id or f"run-{uuid.uuid4().hex[:12]}",
            task_id=task_id,
            worker_id=worker_id,
            capability_scope=list(capability_scope or []),
            permissions=list(permissions or []),
            metadata=dict(metadata or {}),
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if not isinstance(self.run_id, str) or not self.run_id.strip():
            raise WorkerError("run_id must be non-empty string")
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise WorkerError("task_id must be non-empty string")
        if not isinstance(self.worker_id, str) or not self.worker_id.strip():
            raise WorkerError("worker_id must be non-empty string")
        if not isinstance(self.capability_scope, list):
            raise WorkerError("capability_scope must be a list")
        for c in self.capability_scope:
            if not isinstance(c, str) or not c.strip():
                raise WorkerError(f"capability_scope entry {c!r} must be non-empty string")
        if not isinstance(self.permissions, list):
            raise WorkerError("permissions must be a list")
        for p in self.permissions:
            if not isinstance(p, str) or not p.strip():
                raise WorkerError(f"permission {p!r} must be non-empty string")

    def can_use_capability(self, capability: str) -> bool:
        return capability in self.capability_scope

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "task_id": self.task_id,
            "worker_id": self.worker_id,
            "capability_scope": list(self.capability_scope),
            "permissions": list(self.permissions),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkerContext":
        if not isinstance(data, dict):
            raise WorkerError("worker context data must be a mapping")
        obj = cls(
            run_id=data.get("run_id", ""),
            task_id=data.get("task_id", ""),
            worker_id=data.get("worker_id", ""),
            capability_scope=list(data.get("capability_scope", [])),
            permissions=list(data.get("permissions", [])),
            metadata=dict(data.get("metadata", {})),
            created_at=data.get("created_at", _now()),
        )
        obj.validate()
        return obj


# ---------------------------------------------------------------------------
# WorkerResult — structured result (T013 §9)
# ---------------------------------------------------------------------------

@dataclass
class WorkerResult:
    """Structured result — never just text."""

    status: WorkerResultStatus
    output: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    execution: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            try:
                self.status = WorkerResultStatus(self.status)
            except ValueError as exc:
                raise WorkerError(f"invalid result status {self.status!r}") from exc

    @classmethod
    def create(
        cls,
        status: WorkerResultStatus | str,
        output: Optional[Dict[str, Any]] = None,
        artifacts: Optional[List[Dict[str, Any]]] = None,
        evidence: Optional[List[Dict[str, Any]]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        execution: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> "WorkerResult":
        if isinstance(status, str):
            try:
                status = WorkerResultStatus(status)
            except ValueError as exc:
                raise WorkerError(f"invalid result status {status!r}") from exc
        obj = cls(
            status=status,  # type: ignore
            output=dict(output or {}),
            artifacts=list(artifacts or []),
            evidence=list(evidence or []),
            metrics=dict(metrics or {}),
            execution=dict(execution or {}),
            error=error,
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if not isinstance(self.status, WorkerResultStatus):
            raise WorkerError(f"status must be WorkerResultStatus, got {self.status!r}")
        if not isinstance(self.output, dict):
            raise WorkerError("output must be a mapping")
        if not isinstance(self.artifacts, list):
            raise WorkerError("artifacts must be a list")
        if not isinstance(self.evidence, list):
            raise WorkerError("evidence must be a list")
        if not isinstance(self.metrics, dict):
            raise WorkerError("metrics must be a mapping")
        if not isinstance(self.execution, dict):
            raise WorkerError("execution must be a mapping")
        # PARTIAL must not be auto-promoted to SUCCEEDED — enforce explicit status
        # (no auto-conversion; caller must handle PARTIAL explicitly)

    @property
    def is_success(self) -> bool:
        return self.status == WorkerResultStatus.SUCCEEDED

    @property
    def is_failure(self) -> bool:
        return self.status == WorkerResultStatus.FAILED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value if isinstance(self.status, WorkerResultStatus) else str(self.status),
            "output": dict(self.output),
            "artifacts": list(self.artifacts),
            "evidence": list(self.evidence),
            "metrics": dict(self.metrics),
            "execution": dict(self.execution),
            "error": self.error,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkerResult":
        if not isinstance(data, dict):
            raise WorkerError("worker result data must be a mapping")
        status = data.get("status")
        if not status:
            raise WorkerError("status is required")
        return cls.create(
            status=status,
            output=dict(data.get("output", {})),
            artifacts=list(data.get("artifacts", [])),
            evidence=list(data.get("evidence", [])),
            metrics=dict(data.get("metrics", {})),
            execution=dict(data.get("execution", {})),
            error=data.get("error"),
        )


# ---------------------------------------------------------------------------
# WorkerEvidence — provenance (T013 §10, Rule 5)
# ---------------------------------------------------------------------------

@dataclass
class WorkerEvidence:
    """Evidence with provenance chain: Evidence → Run → Artifact → Task → Requirement."""

    evidence_id: str
    task_id: str
    run_id: str
    producer: str
    type: str
    source: str
    content_hash: str
    parent_artifact: str = ""
    environment: str = ""
    status: str = "ADMISSIBLE"
    created_at: str = field(default_factory=_now)
    # provenance chain refs
    artifact_id: str = ""
    requirement_id: str = ""
    content: str = ""

    def __post_init__(self) -> None:
        if not self.content_hash and self.content:
            self.content_hash = compute_hash(self.content)
        if not self.content_hash:
            self.content_hash = compute_hash(self.evidence_id)

    @classmethod
    def create(
        cls,
        evidence_id: Optional[str] = None,
        task_id: str = "",
        run_id: str = "",
        producer: str = "",
        type: str = "result",
        source: str = "",
        content: str = "",
        content_hash: Optional[str] = None,
        parent_artifact: str = "",
        environment: str = "",
        status: str = "ADMISSIBLE",
        artifact_id: str = "",
        requirement_id: str = "",
    ) -> "WorkerEvidence":
        eid = evidence_id or f"ev-{uuid.uuid4().hex[:12]}"
        chash = content_hash or (compute_hash(content) if content else compute_hash(eid))
        obj = cls(
            evidence_id=eid,
            task_id=task_id,
            run_id=run_id,
            producer=producer,
            type=type,
            source=source,
            content_hash=chash,
            parent_artifact=parent_artifact,
            environment=environment,
            status=status,
            artifact_id=artifact_id,
            requirement_id=requirement_id,
            content=content,
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        required = [self.evidence_id, self.task_id, self.run_id, self.producer, self.type, self.source, self.content_hash]
        if any(not str(v) for v in required):
            raise WorkerError("WorkerEvidence is missing a mandatory field (evidence_id, task_id, run_id, producer, type, source, content_hash)")
        if self.status not in ("ADMISSIBLE", "UNKNOWN", "REJECTED"):
            raise WorkerError(f"evidence status {self.status!r} must be ADMISSIBLE, UNKNOWN or REJECTED")
        # UNKNOWN never promoted to PASS — enforce at validation
        # (caller must not treat UNKNOWN as PASS)

    @property
    def is_admissible(self) -> bool:
        return self.status == "ADMISSIBLE" and bool(self.content_hash)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "task_id": self.task_id,
            "run_id": self.run_id,
            "producer": self.producer,
            "type": self.type,
            "source": self.source,
            "content_hash": self.content_hash,
            "parent_artifact": self.parent_artifact,
            "environment": self.environment,
            "status": self.status,
            "created_at": self.created_at,
            "artifact_id": self.artifact_id,
            "requirement_id": self.requirement_id,
            "content": self.content,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkerEvidence":
        if not isinstance(data, dict):
            raise WorkerError("evidence data must be a mapping")
        obj = cls(
            evidence_id=data.get("evidence_id", ""),
            task_id=data.get("task_id", ""),
            run_id=data.get("run_id", ""),
            producer=data.get("producer", ""),
            type=data.get("type", "result"),
            source=data.get("source", ""),
            content_hash=data.get("content_hash", ""),
            parent_artifact=data.get("parent_artifact", ""),
            environment=data.get("environment", ""),
            status=data.get("status", "ADMISSIBLE"),
            created_at=data.get("created_at", _now()),
            artifact_id=data.get("artifact_id", ""),
            requirement_id=data.get("requirement_id", ""),
            content=data.get("content", ""),
        )
        obj.validate()
        return obj

    def provenance_chain(self) -> Dict[str, Any]:
        """Return provenance chain dict: Evidence → Run → Artifact → Task → Requirement."""
        return {
            "evidence_id": self.evidence_id,
            "run_id": self.run_id,
            "artifact_id": self.artifact_id or self.parent_artifact,
            "task_id": self.task_id,
            "requirement_id": self.requirement_id,
            "complete": all([self.evidence_id, self.run_id, self.task_id, self.content_hash]),
        }
