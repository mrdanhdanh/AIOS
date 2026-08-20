"""Workflow contract metadata — versioned interface (TASK-008)."""

from __future__ import annotations

from aios.core.contracts import Contract, check_compatibility

__all__ = ["WORKFLOW_CONTRACT", "check_workflow_contract"]

WORKFLOW_CONTRACT = Contract(
    name="runtime.workflow",
    version_range=">=1.0.0,<2.0.0",
    description="Declarative workflow definition + engine-independent compiler (TASK-008).",
)

_WORKFLOW_VERSION = "1.0.0"


def check_workflow_contract(version: str | None = None) -> None:
    ver = version or _WORKFLOW_VERSION
    check_compatibility(WORKFLOW_CONTRACT, ver)
