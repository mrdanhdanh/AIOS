"""Architecture Guard (Rule 3).

Enforces the layering ``Agent -> Orchestrator -> Runtime -> Capability -> Tool``
using an AST/import scanner. Agents must not import provider adapters,
filesystem adapters or execution primitives (e.g. ``subprocess``) directly.
Violations fail the architecture gate and BLOCK the task.
"""

from .guard import (
    ARCH_RULES,
    ArchitectureError,
    ArchitectureGuard,
    GateResult,
    Violation,
    scan_source,
)

__all__ = [
    "ARCH_RULES",
    "ArchitectureError",
    "ArchitectureGuard",
    "GateResult",
    "Violation",
    "scan_source",
]
