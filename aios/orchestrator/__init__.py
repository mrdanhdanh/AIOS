"""AIOS Orchestrator v1 — Decision Pipeline + Operational Orchestration (TASK-010, TASK-012, M2).

Control plane that turns an unstructured request into a validated
ExecutionPlan for the Runtime. Deterministic-first: LLM is only a fallback
when RuleEngine=INSUFFICIENT and WorkflowMatcher=NO_MATCH.

Operational Orchestration (TASK-012) adds Goal Manager, Task Queue,
Permission Broker and Failure Recovery atop the Decision Pipeline.

Layering: ``orchestrator`` layer — may import ``runtime``, ``capability``,
``tool``, ``unknown`` (never ``agent``). Pure Python, no LLM on fast path.

Components:
    normalizer        — Request → NormalizedRequest
    rule_engine       — deterministic rules → SUFFICIENT | INSUFFICIENT
    workflow_matcher  — WorkflowLibrary → MATCHED | NO_MATCH
    planner           — LLM fallback → ExecutionPlan (validated)
    execution_plan    — artifact between Orchestrator and Runtime
    decision_pipeline — orchestration + evidence chain
    goal_manager      — Goal lifecycle + persistence
    task_queue        — logical queue (dependency/priority, not Scheduler)
    permission_broker — aggregate → Policy/Permission delegate
    failure_recovery  — classify + bounded retry + policy-gated fallback

Backward compat: ``aios.governance.deterministic.pipeline.DeterministicControlPath``
re-exports / delegates to this package so existing M1 tests keep passing.
"""

from .decision_pipeline import DecisionEvidence, DecisionPipeline, DecisionResult
from .execution_plan import ExecutionPlan, ExecutionPlanError, PlanEdge, PlanNode
from .failure_recovery import (
    FailureCategory,
    FailureClassifier,
    FailureRecovery,
    FailureRecoveryError,
    RecoveryRecord,
    RecoveryStrategy,
    RetryPolicy,
)
from .goal_manager import Goal, GoalError, GoalManager, GoalStatus
from .normalizer import NormalizedRequest, Normalizer
from .permission_broker import (
    OrchestratorPermissionBroker,
    OrchestratorPermissionBrokerError,
    OrchestratorPermissionDecision,
    PermissionRequestRecord,
)
from .planner import Planner, PlannerError, PlannerRequest, PlannerResponse
from .rule_engine import RuleDecision, RuleEngine
from .task_queue import Task, TaskPriority, TaskQueue, TaskQueueError, TaskStatus
from .workflow_matcher import WorkflowLibrary, WorkflowMatch, WorkflowMatcher

__all__ = [
    "NormalizedRequest",
    "Normalizer",
    "RuleDecision",
    "RuleEngine",
    "WorkflowLibrary",
    "WorkflowMatch",
    "WorkflowMatcher",
    "PlannerRequest",
    "PlannerResponse",
    "Planner",
    "PlannerError",
    "PlanNode",
    "PlanEdge",
    "ExecutionPlan",
    "ExecutionPlanError",
    "DecisionPipeline",
    "DecisionResult",
    "DecisionEvidence",
    "GoalStatus",
    "Goal",
    "GoalError",
    "GoalManager",
    "TaskStatus",
    "TaskPriority",
    "Task",
    "TaskQueueError",
    "TaskQueue",
    "OrchestratorPermissionDecision",
    "PermissionRequestRecord",
    "OrchestratorPermissionBroker",
    "OrchestratorPermissionBrokerError",
    "FailureCategory",
    "RecoveryStrategy",
    "FailureClassifier",
    "RetryPolicy",
    "RecoveryRecord",
    "FailureRecovery",
    "FailureRecoveryError",
]
