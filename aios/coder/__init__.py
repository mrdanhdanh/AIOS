"""Coder subsystem (M19).

Houses the coder-agent contract, state machine, planner, code-generation
runtime, patch engine, review agent, artifact/evidence, conformance harness,
autonomy/permission integration, prompt architecture and file-safety boundary.

Layering: ``coder`` is an ``unknown`` (infra) layer per the architecture guard,
so it may import stdlib + ``aios.core`` + ``aios.governance`` (unknown) +
``aios.capability``. It must never import ``subprocess``/``os`` execution
primitives, provider or filesystem adapters directly (ARCH-001..004 spirit).
"""

from aios.coder.contract import (
    CoderAgentContract,
    CoderAgentStateMachine,
    CodingTaskState,
    TransitionRecord,
)
from aios.coder.planner import (
    CodingPlan,
    CodingPlanner,
    CodingStep,
    PlanStatus,
    PlanVerifier,
    PlanVerifyError,
)
from aios.coder.generation import (
    CapabilityDispatcher,
    CodeGenerationRuntime,
    GeneratedArtifact,
    GenerationError,
    GenerationRun,
    GenerationStatus,
)
from aios.coder.patch import (
    PatchEngine,
    PatchError,
    PatchRun,
    PatchStatus,
)
from aios.coder.review import (
    CodeReviewAgent,
    Finding,
    ReviewError,
    ReviewReport,
    Severity,
    Verdict,
)
from aios.coder.artifact import (
    ArtifactError,
    ArtifactKind,
    ArtifactStatus,
    CodingArtifact,
    CodingArtifactRegistry,
    EvidenceLink,
)
from aios.coder.conformance import (
    CoderConformanceHarness,
    ConformanceError,
    ConformanceResult,
    ConformanceStatus,
    SecurityStatus,
)
from aios.coder.autonomy import (
    AutonomyLevel,
    AutonomyPermissionBroker,
    PermissionDecision,
    PermissionError_ as CoderPermissionError,
)

__all__ = [
    "CoderAgentContract",
    "CoderAgentStateMachine",
    "CodingTaskState",
    "TransitionRecord",
    "CodingPlan",
    "CodingPlanner",
    "CodingStep",
    "PlanStatus",
    "PlanVerifier",
    "PlanVerifyError",
    "CapabilityDispatcher",
    "CodeGenerationRuntime",
    "GeneratedArtifact",
    "GenerationError",
    "GenerationRun",
    "GenerationStatus",
    "PatchEngine",
    "PatchError",
    "PatchRun",
    "PatchStatus",
    "CodeReviewAgent",
    "Finding",
    "ReviewError",
    "ReviewReport",
    "Severity",
    "Verdict",
    "ArtifactError",
    "ArtifactKind",
    "ArtifactStatus",
    "CodingArtifact",
    "CodingArtifactRegistry",
    "EvidenceLink",
    "CoderConformanceHarness",
    "ConformanceError",
    "ConformanceResult",
    "ConformanceStatus",
    "SecurityStatus",
    "AutonomyLevel",
    "AutonomyPermissionBroker",
    "PermissionDecision",
    "CoderPermissionError",
]
