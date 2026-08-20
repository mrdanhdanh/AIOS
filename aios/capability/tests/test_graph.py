"""Tests for Knowledge Graph v1 — AC-009-07/08/09/10."""

import threading
import pytest

from aios.capability.graph import EdgeType, GraphEdge, GraphError, GraphNode, KnowledgeGraph, NodeType


def _node(nid="n1", ntype=NodeType.CAPABILITY, label="label", source="capability-registry"):
    return GraphNode.create(node_id=nid, node_type=ntype, label=label, source=source)


def _edge(f="n1", t="n2", etype=EdgeType.USES, eid=None, source="manual"):
    return GraphEdge.create(from_id=f, to_id=t, edge_type=etype, edge_id=eid, source=source)


# -- Node validation --

def test_node_create_minimal():
    n = _node()
    n.validate()
    assert n.node_id == "n1"


def test_node_invalid_id():
    with pytest.raises(GraphError):
        GraphNode.create(node_id="", node_type=NodeType.CAPABILITY)
    with pytest.raises(GraphError):
        GraphNode.create(node_id="  ", node_type=NodeType.AGENT)


def test_node_invalid_type():
    with pytest.raises(GraphError):
        GraphNode.create(node_id="x", node_type="UNKNOWN_TYPE")


def test_node_invalid_version():
    with pytest.raises(GraphError):
        GraphNode.create(node_id="x", node_type=NodeType.TOOL, version="bad")


def test_node_all_types():
    for nt in NodeType.all():
        n = GraphNode.create(node_id=f"node-{nt.value}", node_type=nt)
        n.validate()


# -- Edge validation --

def test_edge_create_minimal():
    e = _edge()
    e.validate()


def test_edge_self_loop_reject():
    with pytest.raises(GraphError):
        _edge(f="a", t="a")


def test_edge_invalid_type():
    with pytest.raises(GraphError):
        GraphEdge.create(from_id="a", to_id="b", edge_type="UNKNOWN_EDGE")


def test_edge_all_types():
    for et in EdgeType.all():
        e = GraphEdge.create(from_id="a", to_id="b", edge_type=et, edge_id=f"e-{et.value}")
        e.validate()


# -- Graph add_node / get / list / remove --

def test_graph_add_and_get_node():
    g = KnowledgeGraph()
    g.add_node(_node("agent-1", NodeType.AGENT))
    fetched = g.get_node("agent-1")
    assert fetched.node_type == NodeType.AGENT
    assert g.node_count == 1
    assert len(g) == 1


def test_graph_duplicate_node_reject():
    g = KnowledgeGraph()
    g.add_node(_node("dup"))
    with pytest.raises(GraphError):
        g.add_node(_node("dup"))


def test_graph_unknown_node_reject():
    g = KnowledgeGraph()
    with pytest.raises(GraphError):
        g.get_node("ghost")


def test_graph_list_nodes_sorted():
    g = KnowledgeGraph()
    g.add_node(_node("zebra", NodeType.TOOL))
    g.add_node(_node("apple", NodeType.TOOL))
    lst = g.list_nodes()
    assert lst[0].node_id == "apple"
    assert lst[1].node_id == "zebra"


def test_graph_list_nodes_by_type():
    g = KnowledgeGraph()
    g.add_node(_node("a1", NodeType.AGENT))
    g.add_node(_node("c1", NodeType.CAPABILITY))
    assert len(g.list_nodes(NodeType.AGENT)) == 1
    assert len(g.list_nodes("agent")) == 1
    assert len(g.list_nodes(NodeType.CAPABILITY)) == 1


def test_graph_remove_node_with_edges_reject():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    g.add_node(_node("b", NodeType.CAPABILITY))
    g.add_edge(_edge(f="a", t="b", eid="e1"))
    with pytest.raises(GraphError):
        g.remove_node("a")
    # remove edge first → ok
    g.remove_edge("e1")
    g.remove_node("a")
    assert not g.has_node("a")


def test_graph_add_non_node_reject():
    g = KnowledgeGraph()
    with pytest.raises(GraphError):
        g.add_node("not-a-node")  # type: ignore


# -- Graph edges --

def test_graph_add_edge_and_get():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    g.add_node(_node("b", NodeType.CAPABILITY))
    e = _edge(f="a", t="b", eid="e1")
    g.add_edge(e)
    fetched = g.get_edge("e1")
    assert fetched.from_id == "a"
    assert g.edge_count == 1


def test_graph_edge_missing_node_reject():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    with pytest.raises(GraphError):
        g.add_edge(_edge(f="a", t="missing", eid="e1"))
    with pytest.raises(GraphError):
        g.add_edge(_edge(f="missing", t="a", eid="e2"))


def test_graph_duplicate_edge_id_reject():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    g.add_node(_node("b", NodeType.CAPABILITY))
    g.add_edge(_edge(f="a", t="b", eid="dup"))
    with pytest.raises(GraphError):
        g.add_edge(_edge(f="a", t="b", eid="dup"))


def test_graph_duplicate_triple_reject():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    g.add_node(_node("b", NodeType.CAPABILITY))
    g.add_edge(GraphEdge.create(from_id="a", to_id="b", edge_type=EdgeType.USES, edge_id="e1"))
    with pytest.raises(GraphError):
        g.add_edge(GraphEdge.create(from_id="a", to_id="b", edge_type=EdgeType.USES, edge_id="e2"))
    # different edge_type allowed
    g.add_edge(GraphEdge.create(from_id="a", to_id="b", edge_type=EdgeType.REQUIRES, edge_id="e3"))
    assert g.edge_count == 2


def test_graph_get_edges_filtered():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    g.add_node(_node("b", NodeType.CAPABILITY))
    g.add_node(_node("c", NodeType.TOOL))
    g.add_edge(GraphEdge.create(from_id="a", to_id="b", edge_type=EdgeType.USES, edge_id="e1"))
    g.add_edge(GraphEdge.create(from_id="b", to_id="c", edge_type=EdgeType.IMPLEMENTED_BY, edge_id="e2"))
    assert len(g.get_edges(from_id="a")) == 1
    assert len(g.get_edges(to_id="c")) == 1
    assert len(g.get_edges(edge_type=EdgeType.USES)) == 1
    assert len(g.get_edges(edge_type="USES")) == 1


def test_graph_remove_edge():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    g.add_node(_node("b", NodeType.CAPABILITY))
    g.add_edge(_edge(f="a", t="b", eid="e1"))
    g.remove_edge("e1")
    assert g.edge_count == 0
    with pytest.raises(GraphError):
        g.remove_edge("e1")


def test_graph_add_non_edge_reject():
    g = KnowledgeGraph()
    with pytest.raises(GraphError):
        g.add_edge("not-an-edge")  # type: ignore


# -- AC-009-07: Agent --USES--> Capability --IMPLEMENTED_BY--> Tool --

def test_graph_traversal_agent_capability_tool():
    g = KnowledgeGraph()
    g.add_node(GraphNode.create(node_id="agent-coder", node_type=NodeType.AGENT, label="Coder", source="agent-registry"))
    g.add_node(GraphNode.create(node_id="cap-execute", node_type=NodeType.CAPABILITY, label="execute_code", source="capability-registry"))
    g.add_node(GraphNode.create(node_id="tool-python", node_type=NodeType.TOOL, label="PythonTool", source="tool-registry"))
    g.add_edge(GraphEdge.create(from_id="agent-coder", to_id="cap-execute", edge_type=EdgeType.USES, edge_id="e1"))
    g.add_edge(GraphEdge.create(from_id="cap-execute", to_id="tool-python", edge_type=EdgeType.IMPLEMENTED_BY, edge_id="e2"))
    # neighbors
    nbrs = g.neighbors("agent-coder", direction="out")
    assert len(nbrs) == 1
    assert nbrs[0].node_id == "cap-execute"
    # second hop
    nbrs2 = g.neighbors("cap-execute", direction="out")
    assert any(n.node_id == "tool-python" for n in nbrs2)
    # path
    path = g.find_path("agent-coder", "tool-python")
    assert path == ["agent-coder", "cap-execute", "tool-python"]


def test_graph_neighbors_directions():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    g.add_node(_node("b", NodeType.CAPABILITY))
    g.add_node(_node("c", NodeType.TOOL))
    g.add_edge(GraphEdge.create(from_id="a", to_id="b", edge_type=EdgeType.USES, edge_id="e1"))
    g.add_edge(GraphEdge.create(from_id="b", to_id="c", edge_type=EdgeType.IMPLEMENTED_BY, edge_id="e2"))
    # out from b → c
    assert [n.node_id for n in g.neighbors("b", direction="out")] == ["c"]
    # in to b → a
    assert [n.node_id for n in g.neighbors("b", direction="in")] == ["a"]
    # both from b → a,c sorted
    both = [n.node_id for n in g.neighbors("b", direction="both")]
    assert both == ["a", "c"]


def test_graph_neighbors_invalid_direction():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    with pytest.raises(GraphError):
        g.neighbors("a", direction="sideways")


def test_graph_find_path_unreachable():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    g.add_node(_node("b", NodeType.TOOL))
    assert g.find_path("a", "b") is None


def test_graph_find_path_self():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    assert g.find_path("a", "a") == ["a"]


def test_graph_find_path_deterministic():
    g = KnowledgeGraph()
    for nid in ["a", "b", "c", "d"]:
        g.add_node(GraphNode.create(node_id=nid, node_type=NodeType.CAPABILITY))
    # a -> b, a -> c, b -> d, c -> d ; shortest is a->b->d or a->c->d ; BFS deterministic picks b first (sorted)
    g.add_edge(GraphEdge.create(from_id="a", to_id="b", edge_type=EdgeType.USES, edge_id="e1"))
    g.add_edge(GraphEdge.create(from_id="a", to_id="c", edge_type=EdgeType.USES, edge_id="e2"))
    g.add_edge(GraphEdge.create(from_id="b", to_id="d", edge_type=EdgeType.USES, edge_id="e3"))
    g.add_edge(GraphEdge.create(from_id="c", to_id="d", edge_type=EdgeType.USES, edge_id="e4"))
    path1 = g.find_path("a", "d")
    path2 = g.find_path("a", "d")
    assert path1 == path2
    assert path1 == ["a", "b", "d"]  # b < c deterministically


# -- AC-009-08 boundary: in-memory, manual --

def test_graph_is_in_memory_manual():
    g = KnowledgeGraph()
    # no persistence methods
    assert not hasattr(g, "save_to_sqlite")
    assert not hasattr(g, "auto_build")
    # manual population only
    g.add_node(_node("manual-test", NodeType.SKILL))
    assert g.has_node("manual-test")


# -- AC-009-09 provenance --

def test_graph_provenance_retained():
    n = GraphNode.create(node_id="prov-node", node_type=NodeType.CAPABILITY, source="capability-registry", provenance={"run_id": "r1"})
    assert n.source == "capability-registry"
    assert n.provenance["run_id"] == "r1"
    e = GraphEdge.create(from_id="a", to_id="b", edge_type=EdgeType.USES, edge_id="e-prov", source="manual", provenance={"producer": "test"})
    assert e.source == "manual"
    assert e.provenance["producer"] == "test"


def test_graph_node_to_dict():
    n = _node("dict-node", NodeType.PROMPT)
    d = n.to_dict()
    assert d["node_id"] == "dict-node"
    assert d["node_type"] == "prompt"


def test_graph_edge_to_dict():
    e = _edge(f="x", t="y", eid="dict-edge")
    d = e.to_dict()
    assert d["edge_id"] == "dict-edge"


# -- Thread safety --

def test_graph_thread_safety_concurrent_nodes():
    g = KnowledgeGraph()
    errors = []

    def worker(idx: int):
        try:
            g.add_node(GraphNode.create(node_id=f"n-{idx}", node_type=NodeType.TOOL))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert g.node_count == 20


def test_graph_clear():
    g = KnowledgeGraph()
    g.add_node(_node("a", NodeType.AGENT))
    g.add_node(_node("b", NodeType.CAPABILITY))
    g.add_edge(_edge(f="a", t="b", eid="e1"))
    g.clear()
    assert g.node_count == 0
    assert g.edge_count == 0
