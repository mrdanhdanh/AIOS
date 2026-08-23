"""Execution subsystem (M20).

Houses the execution contract, sandbox manager, workspace/snapshot manager,
resource/network/command policy, test runner, build/lint runner, output/artifact
collector, verification engine, security/replay harness and execution
evidence/conformance. Every module is I/O-free, deterministic, fail-closed and
carries provenance (T001 Rule 5 / T078).

Layering: ``execution`` is an ``unknown`` (infra) layer per the architecture
guard, so it may import stdlib + ``aios.core`` + ``aios.governance`` (unknown).
It must never import ``subprocess``/``os`` execution primitives, provider or
filesystem adapters directly (ARCH-001..004 spirit).
"""

from aios.execution._common import ExecutionError, _hash, _now
from aios.execution.contract import (
    CapabilityDispatcher,
    ExecutionContract,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionStatus,
)
from aios.execution.sandbox import (
    IsolationLevel,
    SandboxManager,
    SandboxRecord,
    SandboxStatus,
)
from aios.execution.workspace import (
    SnapshotRecord,
    WorkspaceManager,
    WorkspaceRecord,
    WorkspaceStatus,
)
from aios.execution.policy import (
    Decision,
    ExecutionPolicy,
    PolicyDecision,
    PolicyEngine,
    ResourceLimit,
)
from aios.execution.test_runner import (
    TestResult,
    TestRun,
    TestRunner,
    TestVerdict,
)
from aios.execution.build_lint import (
    BuildLintRun,
    BuildLintRunner,
    BuildResult,
    BuildVerdict,
    LintResult,
    LintVerdict,
)
from aios.execution.collector import (
    CollectedArtifact,
    OutputArtifactCollector,
    OutputCapture,
    redact,
)
from aios.execution.verification import (
    VerificationEngine,
    VerificationResult,
    VerifyStatus,
)
from aios.execution.replay import (
    ReplayRun,
    SecurityReplayHarness,
)
from aios.execution.evidence import (
    EvidenceStatus,
    ExecutionEvidence,
    ExecutionEvidenceRegistry,
)

__all__ = [
    "ExecutionError",
    "_hash",
    "_now",
    "CapabilityDispatcher",
    "ExecutionContract",
    "ExecutionRequest",
    "ExecutionResponse",
    "ExecutionStatus",
    "IsolationLevel",
    "SandboxManager",
    "SandboxRecord",
    "SandboxStatus",
    "SnapshotRecord",
    "WorkspaceManager",
    "WorkspaceRecord",
    "WorkspaceStatus",
    "Decision",
    "ExecutionPolicy",
    "PolicyDecision",
    "PolicyEngine",
    "ResourceLimit",
    "TestResult",
    "TestRun",
    "TestRunner",
    "TestVerdict",
    "BuildLintRun",
    "BuildLintRunner",
    "BuildResult",
    "BuildVerdict",
    "LintResult",
    "LintVerdict",
    "CollectedArtifact",
    "OutputArtifactCollector",
    "OutputCapture",
    "redact",
    "VerificationEngine",
    "VerificationResult",
    "VerifyStatus",
    "ReplayRun",
    "SecurityReplayHarness",
    "EvidenceStatus",
    "ExecutionEvidence",
    "ExecutionEvidenceRegistry",
]
