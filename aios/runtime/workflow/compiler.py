"""Workflow Compiler — engine-independent abstraction (TASK-008)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .definition import WorkflowDefinition

__all__ = ["CompilerError", "CompiledWorkflow", "WorkflowCompiler", "MockCompiler", "LangGraphCompiler"]


class CompilerError(Exception):
    pass


@dataclass
class CompiledWorkflow:
    workflow: WorkflowDefinition
    engine: str
    representation: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.workflow.name

    @property
    def version(self) -> str:
        return self.workflow.version

    def to_dict(self) -> Dict[str, Any]:
        return {"workflow": self.workflow.to_dict(), "engine": self.engine, "representation": self.representation, "metadata": dict(self.metadata)}


class WorkflowCompiler(ABC):
    engine: str = "base"

    @abstractmethod
    def compile(self, definition: WorkflowDefinition) -> CompiledWorkflow:
        pass


class MockCompiler(WorkflowCompiler):
    engine = "mock"

    def compile(self, definition: WorkflowDefinition) -> CompiledWorkflow:
        definition.validate()
        nodes = definition.nodes
        edges = definition.edges
        indeg: Dict[str, int] = {n.id: 0 for n in nodes}
        adj: Dict[str, List[str]] = {n.id: [] for n in nodes}
        for e in edges:
            adj[e.from_id].append(e.to_id)
            indeg[e.to_id] += 1
        queue: List[str] = sorted([nid for nid, d in indeg.items() if d == 0])
        topo: List[str] = []
        while queue:
            queue.sort()
            u = queue.pop(0)
            topo.append(u)
            for v in sorted(adj[u]):
                indeg[v] -= 1
                if indeg[v] == 0:
                    queue.append(v)
            queue.sort()
        if len(topo) != len(nodes):
            raise CompilerError("cycle detected — cannot order nodes")
        exec_nodes = []
        for nid in topo:
            node = next(n for n in nodes if n.id == nid)
            exec_nodes.append({"id": node.id, "type": node.type, "capability": node.capability, "status": "PENDING"})
        representation: Dict[str, Any] = {
            "engine": "mock",
            "nodes": exec_nodes,
            "edges": [e.to_dict() for e in edges],
            "topo_order": topo,
            "retries": definition.retries,
            "timeout": definition.timeout,
            "resources": definition.resources.to_dict() if definition.resources else None,
            "permissions": list(definition.permissions),
        }
        return CompiledWorkflow(workflow=definition, engine=self.engine, representation=representation, metadata={"compiler": "MockCompiler", "contract_version": definition.contract_version})


class LangGraphCompiler(WorkflowCompiler):
    engine = "langgraph"

    def compile(self, definition: WorkflowDefinition) -> CompiledWorkflow:
        definition.validate()
        langgraph_version: Optional[str] = None
        langgraph_available = False
        try:
            import langgraph  # type: ignore[import-not-found]

            langgraph_available = True
            langgraph_version = getattr(langgraph, "__version__", "unknown")
        except ImportError:
            langgraph_available = False
        representation: Dict[str, Any] = {
            "engine": "langgraph",
            "langgraph_available": langgraph_available,
            "nodes": [{"id": n.id, "type": n.type, "capability": n.capability} for n in definition.nodes],
            "edges": [e.to_dict() for e in definition.edges],
            "retries": definition.retries,
            "timeout": definition.timeout,
            "resources": definition.resources.to_dict() if definition.resources else None,
            "permissions": list(definition.permissions),
        }
        metadata: Dict[str, Any] = {"compiler": "LangGraphCompiler", "contract_version": definition.contract_version}
        if langgraph_version is not None:
            metadata["langgraph_version"] = langgraph_version
        metadata["langgraph_available"] = langgraph_available
        return CompiledWorkflow(workflow=definition, engine=self.engine, representation=representation, metadata=metadata)
