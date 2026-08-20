"""AIOS Capability foundation (TASK-009, M1).

Capability-First: agents see capabilities; tools are implementations behind them.

Components:
    capability  — CapabilityContract + CapabilityRegistry (multi-tool mapping)
    prompt      — PromptContract + PromptRegistry (versioned deterministic templates)
    catalog     — SystemCatalog (indexed search over registry metadata)
    graph       — KnowledgeGraph v1 (in-memory manual relationship graph)

Layering: ``capability`` layer — only imports ``tool`` / ``unknown`` / ``aios.core``.
Do not import ``runtime`` / ``agent`` / ``orchestrator`` from here.
"""

from .capability import CapabilityContract, CapabilityError, CapabilityRegistry
from .catalog import CatalogEntry, CatalogError, SystemCatalog
from .contracts import (
    CAPABILITY_CONTRACT,
    CATALOG_CONTRACT,
    GRAPH_CONTRACT,
    PROMPT_CONTRACT,
    check_capability_contracts,
)
from .graph import (
    EdgeType,
    GraphEdge,
    GraphError,
    GraphNode,
    KnowledgeGraph,
    NodeType,
)
from .prompt import PromptContract, PromptError, PromptRegistry

__all__ = [
    # capability
    "CapabilityError",
    "CapabilityContract",
    "CapabilityRegistry",
    # prompt
    "PromptError",
    "PromptContract",
    "PromptRegistry",
    # catalog
    "CatalogError",
    "CatalogEntry",
    "SystemCatalog",
    # graph
    "GraphError",
    "NodeType",
    "EdgeType",
    "GraphNode",
    "GraphEdge",
    "KnowledgeGraph",
    # contracts
    "CAPABILITY_CONTRACT",
    "PROMPT_CONTRACT",
    "CATALOG_CONTRACT",
    "GRAPH_CONTRACT",
    "check_capability_contracts",
]
