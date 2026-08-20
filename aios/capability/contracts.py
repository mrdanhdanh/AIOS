"""Capability foundation contracts — versioned interfaces (TASK-009, M1).

Four contracts: capability registry, prompt registry, system catalog, knowledge graph.
Each is a narrow ``aios.core.contracts.Contract`` so callers can verify
compatibility via :func:`check_capability_contracts` / :func:`check_compatibility`.

Layering: ``capability`` layer — stdlib + ``aios.core`` only.
"""

from __future__ import annotations

from aios.core.contracts import Contract, check_compatibility

__all__ = [
    "CAPABILITY_CONTRACT",
    "PROMPT_CONTRACT",
    "CATALOG_CONTRACT",
    "GRAPH_CONTRACT",
    "check_capability_contracts",
]

CAPABILITY_CONTRACT = Contract(
    name="capability.registry",
    version_range=">=1.0.0,<2.0.0",
    description="Capability registry — first-class metadata + tool mappings (TASK-009).",
)

PROMPT_CONTRACT = Contract(
    name="capability.prompt",
    version_range=">=1.0.0,<2.0.0",
    description="Prompt registry — versioned templates with deterministic rendering (TASK-009).",
)

CATALOG_CONTRACT = Contract(
    name="capability.catalog",
    version_range=">=1.0.0,<2.0.0",
    description="System catalog — indexed search over registry metadata (TASK-009).",
)

GRAPH_CONTRACT = Contract(
    name="capability.graph",
    version_range=">=1.0.0,<2.0.0",
    description="Knowledge graph v1 — in-memory manual relationship graph (TASK-009).",
)

_CAPABILITY_VERSION = "1.0.0"


def check_capability_contracts(version: str | None = None) -> None:
    """Verify all four capability contracts against ``version`` (or 1.0.0)."""
    ver = version or _CAPABILITY_VERSION
    for c in (CAPABILITY_CONTRACT, PROMPT_CONTRACT, CATALOG_CONTRACT, GRAPH_CONTRACT):
        check_compatibility(c, ver)
