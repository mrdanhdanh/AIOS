"""AIOS Task Governance System (TASK-001).

The governance system turns the 7 general rules from the master specification
into a self-verifying control plane implemented as automated gates:

* Rule 1  Task Registry            (:mod:`aios.governance.task_registry`)
* Rule 2  Dependency Graph         (:mod:`aios.governance.dependency`)
* Rule 3  Architecture Guard       (:mod:`aios.governance.architecture`)
* Rule 4  Deterministic Control    (:mod:`aios.governance.deterministic`)
* Rule 5  Evidence Store           (:mod:`aios.governance.evidence`)
* Rule 6  Task State Machine       (:mod:`aios.governance.lifecycle`)
* Rule 7  Regression Gate          (:mod:`aios.governance.regression`)

The :mod:`aios.governance.gates` module converges all seven rules into a single
unified task gate: a task may reach ``DONE`` only when every component gate
passes.
"""

from .task_registry import TaskRegistry, Task, TaskStatus, RegistryError
from .dependency import DependencyGraph
from .lifecycle import TaskLifecycle, LifecycleError
from .evidence import EvidenceStore, Evidence
from .architecture import ArchitectureGuard
from .deterministic import DeterministicControlPath, ValidationError
from .regression import RegressionRunner
from .gates import UnifiedTaskGate, GateResult, GateComponent

__all__ = [
    "TaskRegistry",
    "Task",
    "TaskStatus",
    "RegistryError",
    "DependencyGraph",
    "TaskLifecycle",
    "LifecycleError",
    "EvidenceStore",
    "Evidence",
    "ArchitectureGuard",
    "DeterministicControlPath",
    "ValidationError",
    "RegressionRunner",
    "UnifiedTaskGate",
    "GateResult",
    "GateComponent",
]
