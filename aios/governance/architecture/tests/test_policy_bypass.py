"""Policy bypass detection tests (TASK-016 16.12).

ARCH-F: execution path must go Policy -> Permission -> Execution; an Agent/
Worker/Skill that directly executes a Tool without a Policy import is a bypass.
"""

import pytest

from aios.governance.architecture.scanner import scan_source_extended
from aios.governance.architecture.rules import evaluate_scan_result


def _violations(code, path):
    return evaluate_scan_result(scan_source_extended(code, path))


class TestPolicyBypass:
    def test_agent_tool_execute_without_policy(self):
        vs = _violations(
            "from aios.tool.python_tool import PythonTool\n"
            "def act():\n    return PythonTool().execute('x')\n",
            "aios/agents/coder.py",
        )
        assert any(v.rule_id == "ARCH-F-001" for v in vs)

    def test_agent_tool_execute_with_policy_ok(self):
        vs = _violations(
            "from aios.tool.python_tool import PythonTool\n"
            "from aios.runtime.policy import PolicyEngine\n"
            "def act():\n    return PythonTool().execute('x')\n",
            "aios/agents/coder.py",
        )
        # Policy import present => no ARCH-F-001 for the agent layer
        assert not any(v.rule_id == "ARCH-F-001" for v in vs)

    def test_skill_tool_execute_without_policy(self):
        vs = _violations(
            "from aios.tool.python_tool import PythonTool\n"
            "def run():\n    return PythonTool().execute('x')\n",
            "aios/skill/bad.py",
        )
        assert any(v.rule_id == "ARCH-F-001" for v in vs)

    def test_execution_module_without_policy(self):
        vs = _violations(
            "from aios.tool.python_tool import PythonTool\n"
            "def execute():\n    return PythonTool().execute('x')\n",
            "aios/runtime/execution.py",
        )
        assert any(v.rule_id == "ARCH-F-001" for v in vs)

    def test_execution_module_with_policy_ok(self):
        vs = _violations(
            "from aios.runtime.policy import PolicyEngine\n"
            "from aios.tool.python_tool import PythonTool\n"
            "def execute():\n    return PythonTool().execute('x')\n",
            "aios/runtime/execution.py",
        )
        assert not any(v.rule_id == "ARCH-F-001" for v in vs)
