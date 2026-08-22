"""Independent Harness Integration (M16 — TASK-104..108).

Foundation + Oracle + Behavioral Bridge + Permission/Sandbox Bridge +
Management Console Integration for bringing external/independent harnesses
into AIOS verification while keeping AIOS the authoritative policy owner.
"""

from __future__ import annotations

from .foundation import (
    EvidenceIngestBoundary,
    EvidencePayload,
    FoundationError,
    HarnessRegistry,
    HarnessType,
    IndependentHarnessAdapter,
    IngestResult,
    PolicyAuthority,
)
from .oracle import (
    IndependentVerificationOracle,
    InvariantMapping,
    OracleResult,
)
from .behavioral_bridge import (
    BehavioralConformanceBridge,
    BehavioralConformanceReport,
)
from .permission_sandbox_bridge import (
    PermissionSandboxBridge,
    PermissionSandboxReport,
)
from .console import (
    ConsoleHarnessView,
    ManagementConsoleIntegration,
)

__all__ = [
    "EvidenceIngestBoundary",
    "EvidencePayload",
    "FoundationError",
    "HarnessRegistry",
    "HarnessType",
    "IndependentHarnessAdapter",
    "IngestResult",
    "PolicyAuthority",
    "IndependentVerificationOracle",
    "InvariantMapping",
    "OracleResult",
    "BehavioralConformanceBridge",
    "BehavioralConformanceReport",
    "PermissionSandboxBridge",
    "PermissionSandboxReport",
    "ConsoleHarnessView",
    "ManagementConsoleIntegration",
]
