"""Capability boundary tests (TASK-016 16.13).

INV-005: Agent/Worker must access Tool via CapabilityContract, never a concrete
Tool implementation. ARCH-E-001.
"""

import pytest

from aios.governance.architecture.scanner import scan_source_extended
from aios.governance.architecture.rules import evaluate_scan_result


def _violations(code, path):
    return evaluate_scan_result(scan_source_extended(code, path))


class TestCapabilityBoundary:
    def test_agent_hardcodes_tool_import(self):
        vs = _violations("from aios.tool.python_tool import PythonTool\n", "aios/agents/coder.py")
        assert any(v.rule_id == "ARCH-E-001" for v in vs)

    def test_agent_hardcodes_tool_call(self):
        vs = _violations(
            "def act():\n    t = PythonTool()\n    return t.run()\n",
            "aios/agents/coder.py",
        )
        assert any(v.rule_id == "ARCH-E-001" for v in vs)

    def test_agent_uses_capability_contract_ok(self):
        vs = _violations(
            "from aios.capability.capability import CapabilityRegistry\n"
            "def act(reg):\n    return reg.invoke('execute_code')\n",
            "aios/agents/coder.py",
        )
        assert not any(v.rule_id == "ARCH-E-001" for v in vs)

    def test_worker_hardcodes_tool(self):
        vs = _violations("from aios.tool.shell_tool import ShellTool\n", "aios/worker/execution.py")
        assert any(v.rule_id == "ARCH-E-001" for v in vs)

    def test_capability_must_not_import_runtime(self):
        vs = _violations("from aios.runtime.kernel import RuntimeKernel\n", "aios/capability/capability.py")
        assert any(v.rule_id == "ARCH-E-002" for v in vs)
