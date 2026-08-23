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
]
