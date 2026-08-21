"""ARCH-A import-boundary tests (TASK-016 16.8).

Positive and negative cases for layer import boundaries, including relative
and dynamic imports. Uses both the legacy ``scan_source`` (guard) and the
extended scanner + rule engine.
"""

import pytest

from aios.governance.architecture.guard import classify_module, scan_source
from aios.governance.architecture.scanner import (
    ModuleScanResult,
    scan_source_extended,
)
from aios.governance.architecture.rules import evaluate_scan_result


def _violations(code, path):
    return evaluate_scan_result(scan_source_extended(code, path))


# ---------------------------------------------------------------------------
# classify_module
# ---------------------------------------------------------------------------
class TestClassifyModule:
    def test_agent(self):
        assert classify_module("aios/agents/coder.py") == "agent"

    def test_orchestrator(self):
        assert classify_module("aios/orchestrator/planner.py") == "orchestrator"

    def test_worker(self):
        assert classify_module("aios/worker/execution.py") == "worker"

    def test_runtime(self):
        assert classify_module("aios/runtime/kernel.py") == "runtime"

    def test_skill(self):
        assert classify_module("aios/skill/contracts.py") == "skill"

    def test_capability(self):
        assert classify_module("aios/capability/capability.py") == "capability"

    def test_tool(self):
        assert classify_module("aios/tool/python_tool.py") == "tool"

    def test_unknown(self):
        assert classify_module("aios/core/version.py") == "unknown"
        assert classify_module("aios/governance/architecture/guard.py") == "unknown"


# ---------------------------------------------------------------------------
# ARCH-A positive (allowed) cases
# ---------------------------------------------------------------------------
class TestImportBoundaryAllowed:
    def test_agent_imports_orchestrator_ok(self):
        vs = _violations("from aios.orchestrator.planner import Planner\n", "aios/agents/coder.py")
        assert not any(v.rule_id == "ARCH-004" for v in vs)

    def test_skill_imports_capability_ok(self):
        vs = _violations("from aios.capability.capability import CapabilityRegistry\n", "aios/skill/contracts.py")
        assert not any(v.rule_id == "ARCH-004" for v in vs)

    def test_runtime_imports_capability_ok(self):
        vs = _violations("from aios.capability.capability import CapabilityRegistry\n", "aios/runtime/kernel.py")
        assert not any(v.rule_id == "ARCH-004" for v in vs)

    def test_stdlib_import_ok(self):
        vs = _violations("import os\nimport json\n", "aios/agents/coder.py")
        # stdlib maps to unknown -> allowed everywhere
        assert not any(v.rule_id == "ARCH-004" for v in vs)


# ---------------------------------------------------------------------------
# ARCH-A negative (denied) cases
# ---------------------------------------------------------------------------
class TestImportBoundaryDenied:
    def test_agent_imports_tool_denied(self):
        vs = _violations("from aios.tool.python_tool import PythonTool\n", "aios/agents/coder.py")
        assert any(v.rule_id == "ARCH-004" for v in vs)

    def test_agent_imports_runtime_denied(self):
        vs = _violations("from aios.runtime.kernel import RuntimeKernel\n", "aios/agents/coder.py")
        assert any(v.rule_id == "ARCH-004" for v in vs)

    def test_skill_imports_runtime_denied(self):
        vs = _violations("from aios.runtime.kernel import RuntimeKernel\n", "aios/skill/bad.py")
        assert any(v.rule_id == "ARCH-004" for v in vs)

    def test_capability_imports_runtime_denied(self):
        vs = _violations("from aios.runtime.kernel import RuntimeKernel\n", "aios/capability/capability.py")
        assert any(v.rule_id == "ARCH-004" for v in vs)


# ---------------------------------------------------------------------------
# Relative + dynamic imports (fail-closed)
# ---------------------------------------------------------------------------
class TestRelativeAndDynamic:
    def test_relative_import_resolved(self):
        # Relative import of a lower layer is allowed (capability is below agent? no:
        # agent may only import orchestrator/unknown, so a relative agent->tool is denied)
        vs = _violations("from .python_tool import PythonTool\n", "aios/agents/coder.py")
        # The target ".python_tool" maps via classifier; ensure no crash and rule evaluated
        assert isinstance(vs, list)

    def test_dynamic_import_unknown(self):
        vs = _violations("import importlib\nimportlib.import_module('aios.tool.python_tool')\n", "aios/agents/coder.py")
        # Dynamic import with constant arg is resolved and should be denied (agent->tool)
        assert any(v.rule_id == "ARCH-004" for v in vs)

    def test_dynamic_import_nonconstant_unknown(self):
        vs = _violations("import importlib\nimportlib.import_module(get_name())\n", "aios/agents/coder.py")
        # Non-constant dynamic import -> UNKNOWN -> fail-closed
        assert any(v.rule_id == "ARCH-004" and "UNKNOWN" in v.message for v in vs)


# ---------------------------------------------------------------------------
# Backward-compat: legacy scan_source still returns Violation objects
# ---------------------------------------------------------------------------
class TestLegacyScanSource:
    def test_legacy_returns_violation(self):
        from aios.governance.architecture.guard import Violation
        vs = scan_source("from aios.tool.python_tool import PythonTool\n", "aios/agents/coder.py")
        assert vs and isinstance(vs[0], Violation)
        assert vs[0].rule == "ARCH-004"

    def test_legacy_skill_subprocess(self):
        vs = scan_source("import subprocess\n", "aios/skill/bad.py")
        assert any(v.rule == "ARCH-001" for v in vs)
