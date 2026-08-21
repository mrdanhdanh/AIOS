"""NodeManager for distributed runtime."""
from __future__ import annotations
from aios.distributed.contracts import DistributedError, NodeState, RuntimeNode

class NodeManager:
    def __init__(self) -> None:
        self._nodes: dict[str, RuntimeNode] = {}
    def register_node(self, name: str, address: str = "", capacity: int = 100) -> RuntimeNode:
        node = RuntimeNode(name=name, address=address, capacity=capacity)
        self._nodes[node.node_id] = node
        return node
    def get_node(self, nid: str) -> RuntimeNode:
        if nid not in self._nodes: raise DistributedError(f"Node {nid!r} not found")
        return self._nodes[nid]
    def list_nodes(self) -> list[RuntimeNode]: return list(self._nodes.values())
    def set_node_state(self, nid: str, state: NodeState) -> RuntimeNode:
        n = self.get_node(nid); n.state = state; return n
    def get_healthy_nodes(self) -> list[RuntimeNode]:
        return [n for n in self._nodes.values() if n.is_healthy]
