"""Coding loop subsystem (M21).

Houses the autonomous coding loop: state machine (T145), execution observation
(T146), failure classification (T147), diagnostic agent (T148), repair planner
(T149), progress/regression detection (T150), verification gate (T151), context
refresh + patch chain (T152), autonomous safety controller (T153) and the
autonomous coding harness (T154). Every module is I/O-free, deterministic,
fail-closed and carries provenance (T001 Rule 5 / T078).

Layering: ``coding_loop`` is an ``unknown`` (infra) layer per the architecture
guard, so it may import stdlib + ``aios.core`` + ``aios.governance`` (unknown).
It must never import ``subprocess``/``os`` execution primitives, provider or
filesystem adapters directly (ARCH-001..004 spirit).
"""

from aios.coding_loop._common import CodingLoopError, _hash, _now, redact_secret
from aios.coding_loop.state_machine import (
    CodingLoopRecord,
    CodingLoopState,
    CodingLoopStateMachine,
    TransitionEvent,
    TRANSITIONS,
)
from aios.coding_loop.observation import (
    ExecutionObservation,
    Observation,
    ObservationStatus,
)
from aios.coding_loop.classification import (
    CONFIDENCE_THRESHOLD,
    FailureClass,
    FailureClassifier,
    FailureTaxonomy,
)
from aios.coding_loop.diagnostic import DiagnosticAgent, DiagnosticReport
from aios.coding_loop.repair import RepairPlan, RepairPlanner
from aios.coding_loop.progress_detection import (
    ProgressReport,
    ProgressRegressionDetector,
)
from aios.coding_loop.verification_gate import (
    VerificationGate,
    VerificationResult,
    VerifyStatus,
)
from aios.coding_loop.patch_chain import (
    ContextRefreshPatchChain,
    PatchChain,
)
from aios.coding_loop.safety import (
    AutonomousSafetyController,
    SafetyDecision,
)
from aios.coding_loop.harness import (
    AutonomousCodingHarness,
    CodingHarnessRun,
    HarnessStatus,
)

__all__ = [
    "CodingLoopError",
    "_hash",
    "_now",
    "redact_secret",
    "CodingLoopRecord",
    "CodingLoopState",
    "CodingLoopStateMachine",
    "TransitionEvent",
    "TRANSITIONS",
    "ExecutionObservation",
    "Observation",
    "ObservationStatus",
    "CONFIDENCE_THRESHOLD",
    "FailureClass",
    "FailureClassifier",
    "FailureTaxonomy",
    "DiagnosticAgent",
    "DiagnosticReport",
    "RepairPlan",
    "RepairPlanner",
    "ProgressReport",
    "ProgressRegressionDetector",
    "VerificationGate",
    "VerificationResult",
    "VerifyStatus",
    "ContextRefreshPatchChain",
    "PatchChain",
    "AutonomousSafetyController",
    "SafetyDecision",
    "AutonomousCodingHarness",
    "CodingHarnessRun",
    "HarnessStatus",
]
