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
from .baseline import (
    ARCHITECTURE_VERSION,
    FROZEN_ALLOWED_IMPORT_LAYERS,
    FROZEN_ARCH_RULES,
    FROZEN_LAYER_CONTRACT,
    FROZEN_LAYER_KEYWORDS,
    classify,
    frozen_arch_rules,
    frozen_layer_contract,
    is_frozen_layer,
    scan,
)

__all__ = [
    "ARCH_RULES",
    "ARCHITECTURE_VERSION",
    "ArchitectureError",
    "ArchitectureGuard",
    "GateResult",
    "Violation",
    "scan_source",
    "FROZEN_LAYER_CONTRACT",
    "FROZEN_ARCH_RULES",
    "FROZEN_LAYER_KEYWORDS",
    "FROZEN_ALLOWED_IMPORT_LAYERS",
    "frozen_layer_contract",
    "frozen_arch_rules",
    "is_frozen_layer",
    "classify",
    "scan",
]
