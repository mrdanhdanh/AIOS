"""Behavioral Conformance (TASK-089, M13).

Behavior spec + harness + conformance for observable system behavior. Built on
Harness (T030/T032), Evidence (T001 Rule 5) and Conformance (T087).

Layering: ``unknown`` (infra) layer — stdlib + ``aios.harness`` +
``aios.governance.evidence`` + ``aios.conformance`` only. No provider/filesystem/
agent imports.
"""

from aios.behavioral.behavioral import (
    BehaviorConformanceChecker,
    BehaviorConformanceResult,
    BehaviorHarness,
    BehaviorScenario,
    BehaviorSurface,
)

__all__ = [
    "BehaviorSurface",
    "BehaviorScenario",
    "BehaviorHarness",
    "BehaviorConformanceChecker",
    "BehaviorConformanceResult",
]
