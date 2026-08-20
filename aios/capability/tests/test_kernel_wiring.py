"""Kernel wiring tests for capability foundation (TASK-009)."""

from aios.core.container import Container
from aios.runtime.kernel import RuntimeKernel
from aios.capability.capability import CapabilityRegistry
from aios.capability.prompt import PromptRegistry
from aios.capability.catalog import SystemCatalog
from aios.capability.graph import KnowledgeGraph
from aios.capability.contracts import check_capability_contracts


def test_kernel_wires_capability_singletons():
    k = RuntimeKernel()
    assert k.capabilities is k.capabilities  # singleton
    assert k.prompts is k.prompts
    assert k.catalog is k.catalog
    assert k.graph is k.graph
    assert isinstance(k.capabilities, CapabilityRegistry)
    assert isinstance(k.prompts, PromptRegistry)
    assert isinstance(k.catalog, SystemCatalog)
    assert isinstance(k.graph, KnowledgeGraph)


def test_kernel_health_includes_capability_fields():
    k = RuntimeKernel()
    h = k.health()
    assert "capabilities" in h
    assert "prompts" in h
    assert "catalog_entries" in h
    assert "graph_nodes" in h
    assert "graph_edges" in h
    assert h["capabilities"] == 0
    assert h["graph_nodes"] == 0


def test_kernel_capability_isolated_per_container():
    k1 = RuntimeKernel()
    k2 = RuntimeKernel(container=Container())
    k1.capabilities.register(
        __import__("aios.capability.capability", fromlist=["CapabilityContract"]).CapabilityContract.create("isolated_cap")
    )
    assert len(k1.capabilities) == 1
    assert len(k2.capabilities) == 0


def test_capability_contracts_check():
    # Should not raise for 1.0.0
    check_capability_contracts("1.0.0")
    check_capability_contracts()  # default
    import pytest
    from aios.core.contracts import ContractError
    with pytest.raises(ContractError):
        check_capability_contracts("2.0.0")
    with pytest.raises(ContractError):
        check_capability_contracts("0.9.9")


def test_kernel_full_health_after_population():
    from aios.capability.capability import CapabilityContract
    from aios.capability.prompt import PromptContract
    from aios.capability.catalog import CatalogEntry
    from aios.capability.graph import GraphNode, NodeType, GraphEdge, EdgeType

    k = RuntimeKernel()
    # capability
    k.capabilities.register(CapabilityContract.create("cap_health"))
    k.capabilities.register_tool("cap_health", "ToolA")
    # prompt
    k.prompts.register(PromptContract.create("p_health", "Hello {x}"))
    # catalog
    k.catalog.index(CatalogEntry.create(catalog_type="capability", original_id="cap_health", source="test"))
    # graph
    k.graph.add_node(GraphNode.create(node_id="n1", node_type=NodeType.CAPABILITY, source="test"))
    k.graph.add_node(GraphNode.create(node_id="n2", node_type=NodeType.TOOL, source="test"))
    k.graph.add_edge(GraphEdge.create(from_id="n1", to_id="n2", edge_type=EdgeType.IMPLEMENTED_BY, edge_id="e1"))
    h = k.health()
    assert h["capabilities"] == 1
    assert h["prompts"] == 1
    assert h["catalog_entries"] == 1
    assert h["graph_nodes"] == 2
    assert h["graph_edges"] == 1
