"""Tests for distributed module."""
from __future__ import annotations
import pytest
from aios.distributed.contracts import DistributedError, NodeState, RuntimeNode
from aios.distributed.node_manager import NodeManager

class TestDistributed:
    def test_register_node(self):
        mgr = NodeManager()
        n = mgr.register_node("n1", "localhost:8001")
        assert n.name == "n1"
        assert n.is_healthy
    def test_set_state(self):
        mgr = NodeManager()
        n = mgr.register_node("n1")
        mgr.set_node_state(n.node_id, NodeState.OFFLINE)
        assert not n.is_healthy
    def test_get_healthy(self):
        mgr = NodeManager()
        n1 = mgr.register_node("n1")
        n2 = mgr.register_node("n2")
        mgr.set_node_state(n2.node_id, NodeState.FAILED)
        assert len(mgr.get_healthy_nodes()) == 1
    def test_not_found(self):
        mgr = NodeManager()
        with pytest.raises(DistributedError): mgr.get_node("nonexistent")
    def test_list_nodes(self):
        mgr = NodeManager()
        mgr.register_node("a"); mgr.register_node("b")
        assert len(mgr.list_nodes()) == 2
