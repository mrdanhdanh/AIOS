"""Extension Contracts (M8 — TASK-045)."""
from aios.extension_contracts.compatibility import (
    ExtensionDependencyResolver,
    is_compatible,
)
from aios.extension_contracts.contracts import (
    CapabilityExport,
    ExtensionContext,
    ExtensionError,
    ExtensionEvidence,
    ExtensionManifest,
    ExtensionSpec,
)
from aios.extension_contracts.evidence import make_error, make_evidence
from aios.extension_contracts.validator import ExtensionValidator
__all__ = [
    "ExtensionSpec",
    "ExtensionManifest",
    "CapabilityExport",
    "ExtensionContext",
    "ExtensionError",
    "ExtensionEvidence",
    "ExtensionValidator",
    "ExtensionDependencyResolver",
    "is_compatible",
    "make_error",
    "make_evidence",
]
