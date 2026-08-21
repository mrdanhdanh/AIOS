"""INV-001..010 invariant enforcement tests (TASK-016 16.10)."""

import pytest

from aios.governance.architecture.scanner import scan_source_extended
from aios.governance.architecture.rules import (
    INVARIANTS,
    evaluate_scan_result,
)
from aios.governance.architecture.violations import ViolationStatus


def _violations(code, path):
    return evaluate_scan_result(scan_source_extended(code, path))


# All ten invariants must be defined canonically.
EXPECTED_INVARIANTS = {
    "INV-001", "INV-002", "INV-003", "INV-004", "INV-005",
    "INV-006", "INV-007", "INV-008", "INV-009", "INV-010",
}


class TestInvariantRegistry:
    def test_all_invariants_present(self):
        assert EXPECTED_INVARIANTS.issubset(set(INVARIANTS.keys()))

    def test_invariant_has_category(self):
        for inv_id, meta in INVARIANTS.items():
            assert "category" in meta and meta["category"]


class TestInvariantEnforcement:
    # INV-002: Agent must not access Tool directly (subprocess / concrete tool)
    def test_inv002_subprocess(self):
        vs = _violations("import subprocess\n", "aios/agents/coder.py")
        assert any(v.invariant_id == "INV-002" for v in vs)

    def test_inv002_concrete_tool(self):
        vs = _violations("from aios.tool.python_tool import PythonTool\n", "aios/agents/coder.py")
        assert any(v.invariant_id == "INV-005" for v in vs)

    # INV-007: dependency must follow layer direction
    def test_inv007_agent_to_tool(self):
        vs = _violations("from aios.tool.python_tool import PythonTool\n", "aios/agents/coder.py")
        assert any(v.invariant_id == "INV-007" for v in vs)

    # INV-010: plugin/skill must not bypass core/runtime boundary
    def test_inv010_skill_subprocess(self):
        vs = _violations("import subprocess\n", "aios/skill/bad.py")
        assert any(v.invariant_id == "INV-010" for v in vs)

    def test_inv010_skill_runtime(self):
        vs = _violations("from aios.runtime.kernel import RuntimeKernel\n", "aios/skill/bad.py")
        assert any(v.invariant_id == "INV-010" for v in vs)

    # INV-004: execution must not bypass policy
    def test_inv004_execution_policy(self):
        vs = _violations(
            "from aios.tool.python_tool import PythonTool\n"
            "def run():\n    return PythonTool().execute()\n",
            "aios/runtime/execution.py",
        )
        # execution.py without policy import triggers policy bypass
        assert any(v.invariant_id == "INV-004" for v in vs)

    # INV-001: orchestrator must not become god object
    def test_inv001_orchestrator_tool(self):
        vs = _violations("from aios.tool.adapters import ToolAdapter\n", "aios/orchestrator/planner.py")
        assert any(v.invariant_id == "INV-001" for v in vs)


class TestFailClosed:
    def test_parse_error_is_fail(self):
        vs = _violations("def broken(:\n", "aios/agents/coder.py")
        assert vs and vs[0].status == ViolationStatus.FAIL.value
