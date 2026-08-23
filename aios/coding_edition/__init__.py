"""AIOS 2.0 Coding Edition (M26).

Unified coding capability that converges Coder (M19), Sandbox (M20),
Coding Loop (M21), Verification (M22), Governance (M24) and Evaluation (M25)
into a single, contract-driven, evidence-bearing, fail-closed package.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer per the
architecture guard, so it may import stdlib + ``aios.core`` + ``aios.governance``
+ other ``unknown`` packages. It must never import ``subprocess``/``os``
execution primitives, provider or filesystem adapters directly (ARCH-001..004).
"""

from aios.coding_edition._common import CodingEditionError  # noqa: F401
from aios.coding_edition.contract import (
    CodingEditionContract,
    CompletionState,
    COMPLETION_CHAIN,
)
from aios.coding_edition.state_machine import (
    CodingEditionState,
    CodingEditionStateMachine,
    TransitionRecord,
)
from aios.coding_edition.policy import PolicyEngine, PolicyRule, PolicyVerdict, PolicyContext
from aios.coding_edition.risk import RiskEngine, RiskLevel, RiskModel, RiskInput
from aios.coding_edition.approval import ApprovalGate, ApprovalVerdict, ApprovalRequest
from aios.coding_edition.guardrails import Guardrail, GuardrailSet, GuardrailVerdict
from aios.coding_edition.safe_stop import SafeStopController, StopState, Checkpoint
from aios.coding_edition.recovery import RecoveryOrchestrator, RecoveryPlan, Failure, FailureKind
from aios.coding_edition.lineage import ArtifactLineage, LineageNode
from aios.coding_edition.session import CodingSession, SessionState, SessionStep
from aios.coding_edition.session_fork import SessionFork, ForkedSession
from aios.coding_edition.multi_agent import AgentRole, MultiAgentCoordinator, AgentAssignment
from aios.coding_edition.parallel import ParallelCodingScheduler, CodingTask
from aios.coding_edition.impact import ImpactAnalyzer, DependencyEdge
from aios.coding_edition.knowledge_graph import RepoKnowledgeGraph, RepoNode
from aios.coding_edition.doctor import CodingDoctor, Diagnostic, DiagnosticLevel
from aios.coding_edition.health import CodingHealthScore, HealthDimension, HealthReport
from aios.coding_edition.release import ReleaseGate, ReleaseVerdict, ReleaseCandidate
from aios.coding_edition.certification import CodingCertification, Certification
from aios.coding_edition.benchmark import BenchmarkGate, BenchmarkVerdict, BenchmarkResult
from aios.coding_edition.integration import CodingEdition, IntegrationReport
from aios.coding_edition.regression import FullRegression, RegressionReport, ComponentResult

__all__ = [
    "CodingEditionError",
    "CodingEditionContract",
    "CompletionState",
    "COMPLETION_CHAIN",
    "CodingEditionState",
    "CodingEditionStateMachine",
    "TransitionRecord",
    "PolicyEngine",
    "PolicyRule",
    "PolicyVerdict",
    "PolicyContext",
    "RiskEngine",
    "RiskLevel",
    "RiskModel",
    "RiskInput",
    "ApprovalGate",
    "ApprovalVerdict",
    "ApprovalRequest",
    "Guardrail",
    "GuardrailSet",
    "GuardrailVerdict",
    "SafeStopController",
    "StopState",
    "Checkpoint",
    "RecoveryOrchestrator",
    "RecoveryPlan",
    "Failure",
    "FailureKind",
    "ArtifactLineage",
    "LineageNode",
    "CodingSession",
    "SessionState",
    "SessionStep",
    "SessionFork",
    "ForkedSession",
    "AgentRole",
    "MultiAgentCoordinator",
    "AgentAssignment",
    "ParallelCodingScheduler",
    "CodingTask",
    "ImpactAnalyzer",
    "DependencyEdge",
    "RepoKnowledgeGraph",
    "RepoNode",
    "CodingDoctor",
    "Diagnostic",
    "DiagnosticLevel",
    "CodingHealthScore",
    "HealthDimension",
    "HealthReport",
    "ReleaseGate",
    "ReleaseVerdict",
    "ReleaseCandidate",
    "CodingCertification",
    "Certification",
    "BenchmarkGate",
    "BenchmarkVerdict",
    "BenchmarkResult",
    "CodingEdition",
    "IntegrationReport",
    "FullRegression",
    "RegressionReport",
    "ComponentResult",
]
