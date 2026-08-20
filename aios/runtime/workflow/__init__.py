"""Workflow package — declarative contract + engine-independent compiler (TASK-008)."""

from .contracts import WORKFLOW_CONTRACT, check_workflow_contract
from .definition import ALLOWED_PERMISSIONS, ALLOWED_NODE_TYPES, WORKFLOW_CONTRACT_VERSION, WorkflowDefinition, WorkflowEdge, WorkflowError, WorkflowNode, WorkflowResource
from .validation import validate_definition
from .compiler import CompiledWorkflow, CompilerError, LangGraphCompiler, MockCompiler, WorkflowCompiler
from .simulation import SimulationResult, SimulatedNodeResult, simulate, simulate_definition, simulate_yaml

__all__ = [
    "WORKFLOW_CONTRACT",
    "check_workflow_contract",
    "WORKFLOW_CONTRACT_VERSION",
    "ALLOWED_PERMISSIONS",
    "ALLOWED_NODE_TYPES",
    "WorkflowDefinition",
    "WorkflowNode",
    "WorkflowEdge",
    "WorkflowResource",
    "WorkflowError",
    "validate_definition",
    "CompiledWorkflow",
    "CompilerError",
    "WorkflowCompiler",
    "MockCompiler",
    "LangGraphCompiler",
    "SimulationResult",
    "SimulatedNodeResult",
    "simulate",
    "simulate_definition",
    "simulate_yaml",
]
