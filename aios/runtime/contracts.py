"""Runtime service contracts — typed, versioned interfaces (TASK-004, M1).

Mỗi runtime service (Context / Audit / Artifact / Permission / Policy) phải có
một Contract rõ ràng theo spec TASK-003/004. File này định nghĩa contract ===
các version_range === mà RuntimeKernel tôn trọng khi wire services, và cung
cấp :func:`verify_runtime_contracts` để architecture/regression test có thể
gọi trực tiếp.

Contract versioning không chỉ là annotation — :func:`check_runtime_contracts`
reject provider version không tương thích (major mismatch).
"""

from __future__ import annotations

from aios.core.contracts import Contract, ContractError, check_compatibility

__all__ = [
    "RUNTIME_SERVICE_CONTRACTS",
    "CONTEXT_CONTRACT",
    "AUDIT_CONTRACT",
    "ARTIFACT_CONTRACT",
    "PERMISSION_CONTRACT",
    "POLICY_CONTRACT",
    "verify_runtime_contracts",
    "check_runtime_contracts",
]

CONTEXT_CONTRACT = Contract(
    name="runtime.context",
    version_range=">=1.0.0,<2.0.0",
    description="Six context types + hierarchical store; no global mutable state.",
)

AUDIT_CONTRACT = Contract(
    name="runtime.audit",
    version_range=">=1.0.0,<2.0.0",
    description="Append-only hash-chained audit trail with provenance/context.",
)

ARTIFACT_CONTRACT = Contract(
    name="runtime.artifact",
    version_range=">=1.0.0,<2.0.0",
    description="Content-addressable artifacts with identity/checksum/version.",
)

PERMISSION_CONTRACT = Contract(
    name="runtime.permission",
    version_range=">=1.0.0,<2.0.0",
    description="Permission scopes + broker (wildcard/prefix matching).",
)

POLICY_CONTRACT = Contract(
    name="runtime.policy",
    version_range=">=1.0.0,<2.0.0",
    description="Deterministic policy pre-check; decides before execution (Rule 4).",
)

RUNTIME_SERVICE_CONTRACTS = [
    CONTEXT_CONTRACT,
    AUDIT_CONTRACT,
    ARTIFACT_CONTRACT,
    PERMISSION_CONTRACT,
    POLICY_CONTRACT,
]

# Canonical provider versions currently implemented by this repo.
_RUNTIME_VERSION = "1.0.0"


def verify_runtime_contracts() -> None:
    """Assert that every TASK-004 service satisfies its contract (no-arg fast path)."""
    for c in RUNTIME_SERVICE_CONTRACTS:
        check_compatibility(c, _RUNTIME_VERSION)


def check_runtime_contracts(providers: dict[str, str]) -> None:
    """Check caller-supplied provider versions (raises ContractError on mismatch)."""
    for c in RUNTIME_SERVICE_CONTRACTS:
        ver = providers.get(c.name)
        if ver is None:
            raise ContractError(f"No provider registered for contract '{c.name}'")
        check_compatibility(c, ver)
