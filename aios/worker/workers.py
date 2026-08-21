"""Concrete workers — General, Coder, Doctor, SystemDoctor (TASK-013).

Each worker shares BaseWorker contract but specializes domain logic.
All capability access goes via ``invoke_capability`` (never Tool/Runtime).

Layering: ``worker`` layer — stdlib + ``aios.core`` + ``aios.capability`` only.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from aios.capability.capability import CapabilityRegistry

from .contract import (
    WorkerContext,
    WorkerContract,
    WorkerRequest,
    WorkerResult,
    WorkerResultStatus,
    WorkerType,
)
from .execution import BaseWorker
from .lifecycle import WorkerLifecycle

__all__ = [
    "GeneralWorker",
    "CoderWorker",
    "DoctorWorker",
    "SystemDoctorWorker",
    "DEFAULT_GENERAL_CONTRACT",
    "DEFAULT_CODER_CONTRACT",
    "DEFAULT_DOCTOR_CONTRACT",
    "DEFAULT_SYSTEM_DOCTOR_CONTRACT",
]


def _now_ms() -> int:
    return int(time.time() * 1000)


# ---------------------------------------------------------------------------
# Default contracts for each worker type
# ---------------------------------------------------------------------------

DEFAULT_GENERAL_CONTRACT = WorkerContract.create(
    worker_id="general-worker",
    worker_type=WorkerType.GENERAL,
    version="1.0.0",
    capabilities=["research", "summarize", "transform", "inspect", "coordinate"],
    input_schema={"type": "object", "properties": {"objective": {"type": "object"}}},
    output_schema={"type": "object", "properties": {"summary": {"type": "string"}}},
    lifecycle={"states": ["REGISTERED", "READY", "ASSIGNED", "RUNNING", "COMPLETING", "COMPLETED"]},
    execution_context={"run_id": "string", "task_id": "string", "capability_scope": "list"},
    policy_context={"permissions": "list"},
    evidence_contract={"required": False, "provenance": "Evidence->Run->Artifact->Task->Requirement"},
    description="General worker for research/summarize/transform/inspect/coordinate",
)

DEFAULT_CODER_CONTRACT = WorkerContract.create(
    worker_id="coder-worker",
    worker_type=WorkerType.CODER,
    version="1.0.0",
    capabilities=["code.read", "code.write", "test.run", "code.analyze", "code.refactor"],
    input_schema={"type": "object", "properties": {"objective": {"type": "object"}}},
    output_schema={"type": "object", "properties": {"summary": {"type": "string"}}},
    lifecycle={"states": ["REGISTERED", "READY", "ASSIGNED", "RUNNING", "COMPLETING", "COMPLETED"]},
    execution_context={"run_id": "string", "task_id": "string", "capability_scope": "list"},
    policy_context={"permissions": "list"},
    evidence_contract={"required": True, "provenance": "Evidence->Run->Artifact->Task->Requirement"},
    description="Coder worker for inspect/edit/run tests/analyze/refactor",
)

DEFAULT_DOCTOR_CONTRACT = WorkerContract.create(
    worker_id="doctor-worker",
    worker_type=WorkerType.DOCTOR,
    version="1.0.0",
    capabilities=["diagnose.task", "inspect.logs", "inspect.artifacts", "analyze.failure"],
    input_schema={"type": "object", "properties": {"failure": {"type": "object"}}},
    output_schema={"type": "object", "properties": {"diagnosis": {"type": "object"}}},
    lifecycle={"states": ["REGISTERED", "READY", "ASSIGNED", "RUNNING", "COMPLETING", "COMPLETED"]},
    execution_context={"run_id": "string", "task_id": "string", "capability_scope": "list"},
    policy_context={"permissions": "list"},
    evidence_contract={"required": True, "provenance": "Evidence->Run->Artifact->Task->Requirement"},
    description="Doctor worker for application/task diagnosis",
)

DEFAULT_SYSTEM_DOCTOR_CONTRACT = WorkerContract.create(
    worker_id="system-doctor-worker",
    worker_type=WorkerType.SYSTEM_DOCTOR,
    version="1.0.0",
    capabilities=["diagnose.runtime", "health.check", "inspect.config", "analyze.architecture"],
    input_schema={"type": "object", "properties": {"health": {"type": "object"}}},
    output_schema={"type": "object", "properties": {"diagnosis": {"type": "object"}}},
    lifecycle={"states": ["REGISTERED", "READY", "ASSIGNED", "RUNNING", "COMPLETING", "COMPLETED"]},
    execution_context={"run_id": "string", "task_id": "string", "capability_scope": "list"},
    policy_context={"permissions": "list"},
    evidence_contract={"required": True, "provenance": "Evidence->Run->Artifact->Task->Requirement"},
    description="System doctor for runtime/service/dependency health",
)


# ---------------------------------------------------------------------------
# GeneralWorker
# ---------------------------------------------------------------------------

class GeneralWorker(BaseWorker):
    """General worker — research/summarize/transform/inspect/coordinate."""

    def __init__(
        self,
        contract: Optional[WorkerContract] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        permission_checker: Optional[Any] = None,
        lifecycle: Optional[WorkerLifecycle] = None,
    ) -> None:
        super().__init__(
            contract=contract or DEFAULT_GENERAL_CONTRACT,
            capability_registry=capability_registry,
            permission_checker=permission_checker,
            lifecycle=lifecycle,
        )

    def _do_work(self, request: WorkerRequest, context: WorkerContext) -> WorkerResult:
        objective = request.objective or {}
        description = objective.get("description", "") or objective.get("task", "") or "general task"
        # Determine which capability to use based on objective
        desc_lower = description.lower()
        chosen_cap = "inspect"
        if "research" in desc_lower:
            chosen_cap = "research"
        elif "summar" in desc_lower:
            chosen_cap = "summarize"
        elif "transform" in desc_lower:
            chosen_cap = "transform"
        elif "coordinate" in desc_lower:
            chosen_cap = "coordinate"
        # Ensure chosen is in scope; fallback to first available
        if chosen_cap not in context.capability_scope:
            # Use first in scope that is also in contract
            for c in context.capability_scope:
                if c in self.capabilities:
                    chosen_cap = c
                    break
        # Invoke via capability (never Tool)
        invocation = self.invoke_capability(chosen_cap, context, payload={"objective": objective})
        # Create evidence
        evidence = self.create_evidence(
            task_id=request.task_id,
            run_id=context.run_id,
            content=f"general:{chosen_cap}:{description}",
            evidence_type="result",
            source=f"worker:{self.worker_id}",
        )
        return WorkerResult.create(
            status=WorkerResultStatus.SUCCEEDED,
            output={"summary": f"General task completed via {chosen_cap}: {description}", "capability": chosen_cap, "invocation": invocation},
            artifacts=[{"artifact_id": f"artifact-{context.run_id}", "type": "general_output"}],
            evidence=[evidence.to_dict()],
            metrics={"duration_ms": 10},
            execution={"run_id": context.run_id, "task_id": request.task_id, "worker_id": self.worker_id},
        )


# ---------------------------------------------------------------------------
# CoderWorker
# ---------------------------------------------------------------------------

class CoderWorker(BaseWorker):
    """Coder worker — inspect/edit/run tests/analyze/refactor via capability."""

    def __init__(
        self,
        contract: Optional[WorkerContract] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        permission_checker: Optional[Any] = None,
        lifecycle: Optional[WorkerLifecycle] = None,
    ) -> None:
        super().__init__(
            contract=contract or DEFAULT_CODER_CONTRACT,
            capability_registry=capability_registry,
            permission_checker=permission_checker,
            lifecycle=lifecycle,
        )

    def _do_work(self, request: WorkerRequest, context: WorkerContext) -> WorkerResult:
        objective = request.objective or {}
        description = objective.get("description", "") or objective.get("task", "") or "coding task"
        desc_lower = description.lower()

        # Simulate coder flow: read -> write -> test (via capabilities)
        steps: List[Dict[str, Any]] = []
        # Always try code.read first if in scope
        if "code.read" in context.capability_scope:
            inv = self.invoke_capability("code.read", context, payload={"objective": objective})
            steps.append(inv)
        # If description suggests edit/write
        if any(k in desc_lower for k in ("fix", "edit", "write", "refactor", "implement")):
            if "code.write" in context.capability_scope:
                inv = self.invoke_capability("code.write", context, payload={"objective": objective})
                steps.append(inv)
            elif "code.refactor" in context.capability_scope:
                inv = self.invoke_capability("code.refactor", context, payload={"objective": objective})
                steps.append(inv)
        # If test-related
        if any(k in desc_lower for k in ("test", "failing", "pytest")):
            if "test.run" in context.capability_scope:
                inv = self.invoke_capability("test.run", context, payload={"objective": objective})
                steps.append(inv)
        # If analyze
        if "analyz" in desc_lower and "code.analyze" in context.capability_scope:
            inv = self.invoke_capability("code.analyze", context, payload={"objective": objective})
            steps.append(inv)

        # If no steps were invoked (e.g., scope limited), invoke first available
        if not steps:
            for cap in context.capability_scope:
                if cap in self.capabilities:
                    inv = self.invoke_capability(cap, context, payload={"objective": objective})
                    steps.append(inv)
                    break

        evidence = self.create_evidence(
            task_id=request.task_id,
            run_id=context.run_id,
            content=f"coder:{description}:steps={len(steps)}",
            evidence_type="result",
            source=f"worker:{self.worker_id}",
        )
        return WorkerResult.create(
            status=WorkerResultStatus.SUCCEEDED,
            output={"summary": f"Coding task completed: {description}", "steps": steps},
            artifacts=[{"artifact_id": f"artifact-{context.run_id}", "type": "code_change", "steps": len(steps)}],
            evidence=[evidence.to_dict()],
            metrics={"duration_ms": 20},
            execution={"run_id": context.run_id, "task_id": request.task_id, "worker_id": self.worker_id},
        )


# ---------------------------------------------------------------------------
# DoctorWorker
# ---------------------------------------------------------------------------

class DoctorWorker(BaseWorker):
    """Doctor worker — diagnose task failure, inspect logs/artifacts, recommend recovery."""

    def __init__(
        self,
        contract: Optional[WorkerContract] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        permission_checker: Optional[Any] = None,
        lifecycle: Optional[WorkerLifecycle] = None,
    ) -> None:
        super().__init__(
            contract=contract or DEFAULT_DOCTOR_CONTRACT,
            capability_registry=capability_registry,
            permission_checker=permission_checker,
            lifecycle=lifecycle,
        )

    def _do_work(self, request: WorkerRequest, context: WorkerContext) -> WorkerResult:
        objective = request.objective or {}
        failure = objective.get("failure", {}) or request.metadata.get("failure", {}) or {}
        error_text = failure.get("error", "") or objective.get("description", "") or "unknown failure"
        error_lower = error_text.lower()

        # Inspect via capabilities
        inspections: List[Dict[str, Any]] = []
        if "inspect.logs" in context.capability_scope:
            inv = self.invoke_capability("inspect.logs", context, payload={"failure": failure})
            inspections.append(inv)
        if "inspect.artifacts" in context.capability_scope:
            inv = self.invoke_capability("inspect.artifacts", context, payload={"failure": failure})
            inspections.append(inv)
        if "analyze.failure" in context.capability_scope:
            inv = self.invoke_capability("analyze.failure", context, payload={"failure": failure})
            inspections.append(inv)
        if "diagnose.task" in context.capability_scope and not inspections:
            inv = self.invoke_capability("diagnose.task", context, payload={"failure": failure})
            inspections.append(inv)
        if not inspections:
            # Fallback to first available
            for cap in context.capability_scope:
                if cap in self.capabilities:
                    inv = self.invoke_capability(cap, context, payload={"failure": failure})
                    inspections.append(inv)
                    break

        # Classify failure
        category = "LOGICAL"
        confidence = 0.7
        recommendation: List[str] = []
        if "timeout" in error_lower or "transient" in error_lower:
            category = "TRANSIENT"
            confidence = 0.85
            recommendation = ["retry with backoff"]
        elif "dependency" in error_lower or "import" in error_lower or "module" in error_lower or "no module" in error_lower:
            category = "DEPENDENCY_ERROR"
            confidence = 0.8
            recommendation = ["update dependency", "check imports"]
        elif "test" in error_lower or "assertion" in error_lower:
            category = "TEST_FAILURE"
            confidence = 0.9
            recommendation = ["fix failing test", "inspect test output"]
        elif "permission" in error_lower or "denied" in error_lower:
            category = "POLICY_ERROR"
            confidence = 0.85
            recommendation = ["check permissions", "request access"]
        elif "resource" in error_lower or "memory" in error_lower or "cpu" in error_lower:
            category = "RESOURCE_ERROR"
            confidence = 0.8
            recommendation = ["increase resources", "check resource pool"]

        diagnosis = {
            "category": category,
            "confidence": confidence,
            "error": error_text,
            "recommendation": recommendation,
            "inspections": len(inspections),
            "note": "Doctor only diagnoses; remediation via Orchestrator/New Task",
        }

        evidence = self.create_evidence(
            task_id=request.task_id,
            run_id=context.run_id,
            content=f"doctor:{category}:{error_text}",
            evidence_type="diagnosis",
            source=f"worker:{self.worker_id}",
        )
        return WorkerResult.create(
            status=WorkerResultStatus.SUCCEEDED,
            output={"summary": f"Diagnosis: {category}", "diagnosis": diagnosis, "inspections": inspections},
            artifacts=[{"artifact_id": f"artifact-{context.run_id}", "type": "diagnosis"}],
            evidence=[evidence.to_dict()],
            metrics={"duration_ms": 15},
            execution={"run_id": context.run_id, "task_id": request.task_id, "worker_id": self.worker_id},
        )


# ---------------------------------------------------------------------------
# SystemDoctorWorker
# ---------------------------------------------------------------------------

class SystemDoctorWorker(BaseWorker):
    """System doctor — runtime/service/dependency health, config, architecture."""

    def __init__(
        self,
        contract: Optional[WorkerContract] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        permission_checker: Optional[Any] = None,
        lifecycle: Optional[WorkerLifecycle] = None,
    ) -> None:
        super().__init__(
            contract=contract or DEFAULT_SYSTEM_DOCTOR_CONTRACT,
            capability_registry=capability_registry,
            permission_checker=permission_checker,
            lifecycle=lifecycle,
        )

    def _do_work(self, request: WorkerRequest, context: WorkerContext) -> WorkerResult:
        objective = request.objective or {}
        description = objective.get("description", "") or objective.get("health", "") or "system health check"
        desc_lower = description.lower() if isinstance(description, str) else ""

        checks: List[Dict[str, Any]] = []
        if "health.check" in context.capability_scope:
            inv = self.invoke_capability("health.check", context, payload={"objective": objective})
            checks.append(inv)
        if "diagnose.runtime" in context.capability_scope:
            inv = self.invoke_capability("diagnose.runtime", context, payload={"objective": objective})
            checks.append(inv)
        if "inspect.config" in context.capability_scope and ("config" in desc_lower or "configuration" in desc_lower):
            inv = self.invoke_capability("inspect.config", context, payload={"objective": objective})
            checks.append(inv)
        if "analyze.architecture" in context.capability_scope and ("architecture" in desc_lower or "violation" in desc_lower):
            inv = self.invoke_capability("analyze.architecture", context, payload={"objective": objective})
            checks.append(inv)
        if not checks:
            for cap in context.capability_scope:
                if cap in self.capabilities:
                    inv = self.invoke_capability(cap, context, payload={"objective": objective})
                    checks.append(inv)
                    break

        # Determine severity/status
        severity = "LOW"
        status = "HEALTHY"
        findings: List[Dict[str, Any]] = []
        recommendations: List[str] = []
        if "unhealthy" in desc_lower or "degraded" in desc_lower or "failure" in desc_lower:
            severity = "HIGH"
            status = "DEGRADED"
            findings = [{"service": "capability_router", "state": "UNHEALTHY", "detail": description}]
            recommendations = ["restart capability service", "check runtime health"]
        elif "violation" in desc_lower:
            severity = "MEDIUM"
            status = "DEGRADED"
            findings = [{"service": "architecture_guard", "state": "VIOLATION", "detail": description}]
            recommendations = ["fix architecture violation", "review imports"]
        elif "not ready" in desc_lower or "unavailable" in desc_lower:
            severity = "MEDIUM"
            status = "NOT_READY"
            findings = [{"service": "runtime", "state": "NOT_READY", "detail": description}]
            recommendations = ["check readiness probes", "wait for dependencies"]

        diagnosis = {
            "severity": severity,
            "status": status,
            "findings": findings,
            "recommendations": recommendations,
            "checks": len(checks),
            "note": "SystemDoctor only proposes remediation; execution via Runtime/Policy/Orchestrator",
        }

        evidence = self.create_evidence(
            task_id=request.task_id,
            run_id=context.run_id,
            content=f"system_doctor:{status}:{description}",
            evidence_type="diagnosis",
            source=f"worker:{self.worker_id}",
        )
        return WorkerResult.create(
            status=WorkerResultStatus.SUCCEEDED,
            output={"summary": f"System diagnosis: {status}", "diagnosis": diagnosis, "checks": checks},
            artifacts=[{"artifact_id": f"artifact-{context.run_id}", "type": "system_diagnosis"}],
            evidence=[evidence.to_dict()],
            metrics={"duration_ms": 15},
            execution={"run_id": context.run_id, "task_id": request.task_id, "worker_id": self.worker_id},
        )
