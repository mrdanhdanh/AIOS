"""Workflow simulation — MockCompiler + deterministic fake execution (TASK-008)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .compiler import CompiledWorkflow, CompilerError, MockCompiler
from .definition import WorkflowDefinition, WorkflowError

__all__ = ["SimulationResult", "SimulatedNodeResult", "simulate", "simulate_definition", "simulate_yaml"]


@dataclass
class SimulatedNodeResult:
    node_id: str
    status: str
    capability: Optional[str] = None
    output: Optional[str] = None
    events: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SimulationResult:
    workflow_name: str
    workflow_version: str
    engine: str
    compiled: CompiledWorkflow
    node_results: List[SimulatedNodeResult] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    llm_calls: int = 0
    tool_calls: int = 0
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_name": self.workflow_name,
            "workflow_version": self.workflow_version,
            "engine": self.engine,
            "success": self.success,
            "error": self.error,
            "llm_calls": self.llm_calls,
            "tool_calls": self.tool_calls,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "node_results": [{"node_id": r.node_id, "status": r.status, "capability": r.capability, "output": r.output, "events": r.events} for r in self.node_results],
            "events": self.events,
            "topo_order": self.compiled.representation.get("topo_order", []),
        }


def _fake_execute_node(node_id: str, capability: Optional[str]) -> SimulatedNodeResult:
    events: List[Dict[str, Any]] = [{"type": "node.started", "node_id": node_id, "capability": capability}]
    output = f"simulated:{node_id}:{capability or 'none'}"
    events.append({"type": "node.completed", "node_id": node_id, "output": output})
    return SimulatedNodeResult(node_id=node_id, status="SUCCEEDED", capability=capability, output=output, events=events)


def simulate_definition(definition: WorkflowDefinition) -> SimulationResult:
    started = datetime.now(timezone.utc).isoformat()
    compiler = MockCompiler()
    try:
        compiled = compiler.compile(definition)
    except (WorkflowError, CompilerError) as exc:
        return SimulationResult(workflow_name=definition.name, workflow_version=definition.version, engine="mock", compiled=CompiledWorkflow(workflow=definition, engine="mock"), success=False, error=str(exc), started_at=started, completed_at=datetime.now(timezone.utc).isoformat())
    topo: List[str] = compiled.representation.get("topo_order", [])
    cap_map: Dict[str, Optional[str]] = {n["id"]: n.get("capability") for n in compiled.representation.get("nodes", [])}
    node_results: List[SimulatedNodeResult] = []
    events: List[Dict[str, Any]] = [{"type": "workflow.started", "workflow": definition.name, "version": definition.version}]
    for nid in topo:
        nr = _fake_execute_node(nid, cap_map.get(nid))
        node_results.append(nr)
        events.extend(nr.events)
    events.append({"type": "workflow.completed", "workflow": definition.name})
    return SimulationResult(workflow_name=definition.name, workflow_version=definition.version, engine="mock", compiled=compiled, node_results=node_results, events=events, llm_calls=0, tool_calls=0, started_at=started, completed_at=datetime.now(timezone.utc).isoformat(), success=True)


def simulate_yaml(yaml_text: str) -> SimulationResult:
    try:
        definition = WorkflowDefinition.from_yaml(yaml_text)
    except WorkflowError as exc:
        placeholder = WorkflowDefinition(name="<invalid>", version="0.0.0", description=str(exc))
        return SimulationResult(workflow_name="<invalid>", workflow_version="0.0.0", engine="mock", compiled=CompiledWorkflow(workflow=placeholder, engine="mock"), success=False, error=str(exc), llm_calls=0, tool_calls=0)
    return simulate_definition(definition)


def simulate(path: str) -> SimulationResult:
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    return simulate_yaml(text)
