"""Workflow engine independence tests (TASK-016 16.14).

INV-003: Workflow Definition must not depend directly on engine implementation
(langgraph/jinja2). ARCH-H-002.
"""

import pytest

from aios.governance.architecture.scanner import scan_source_extended
from aios.governance.architecture.rules import evaluate_scan_result


def _violations(code, path):
    return evaluate_scan_result(scan_source_extended(code, path))


class TestWorkflowEngineIndependence:
    def test_workflow_definition_imports_langgraph(self):
        vs = _violations(
            "from langgraph.graph import StateGraph\n",
            "aios/orchestrator/workflow/definition.py",
        )
        assert any(v.rule_id == "ARCH-H-002" for v in vs)

    def test_workflow_validation_imports_langgraph(self):
        vs = _violations(
            "import langgraph\n",
            "aios/orchestrator/workflow/validation.py",
        )
        assert any(v.rule_id == "ARCH-H-002" for v in vs)

    def test_workflow_compiler_may_import_engine(self):
        # The compiler (implementation) is allowed to use the engine.
        vs = _violations(
            "from langgraph.graph import StateGraph\n",
            "aios/orchestrator/workflow/compiler.py",
        )
        assert not any(v.rule_id == "ARCH-H-002" for v in vs)

    def test_workflow_domain_uses_contract_ok(self):
        vs = _violations(
            "from aios.orchestrator.workflow.contracts import WorkflowDefinition\n",
            "aios/orchestrator/workflow/definition.py",
        )
        assert not any(v.rule_id == "ARCH-H-002" for v in vs)
