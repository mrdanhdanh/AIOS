"""Plugin isolation tests (TASK-016 16.15).

INV-010: Skill/Plugin must not bypass Core/Runtime boundary.
ARCH-H-001: no private Core imports, no Runtime internals, no direct mutation.
Also covers deterministic-first, orchestrator God Object, and fail-closed in CI.
"""

import pytest

from aios.governance.architecture.scanner import scan_source_extended
from aios.governance.architecture.rules import evaluate_scan_result
from aios.governance.architecture.gate import ArchitectureGate
from aios.governance.architecture.violations import ViolationStatus


def _violations(code, path):
    return evaluate_scan_result(scan_source_extended(code, path))


class TestPluginIsolation:
    def test_skill_imports_core_private(self):
        vs = _violations("from aios.core.container import Container\n", "aios/skill/bad.py")
        assert any(v.rule_id == "ARCH-H-001" for v in vs)

    def test_skill_imports_governance(self):
        vs = _violations("from aios.governance.architecture.guard import scan_source\n", "aios/skill/bad.py")
        assert any(v.rule_id == "ARCH-H-001" for v in vs)

    def test_skill_imports_runtime_policy(self):
        vs = _violations("from aios.runtime.policy import PolicyEngine\n", "aios/skill/bad.py")
        assert any(v.rule_id == "ARCH-H-001" for v in vs)

    def test_skill_allowed_core_contracts(self):
        # skill may import aios.core.contracts (public contract)
        vs = _violations("from aios.core.contracts import Contract\n", "aios/skill/contracts.py")
        assert not any(v.rule_id == "ARCH-H-001" for v in vs)


class TestOrchestratorGodObject:
    def test_orchestrator_direct_tool(self):
        vs = _violations("from aios.tool.adapters import ToolAdapter\n", "aios/orchestrator/planner.py")
        assert any(v.rule_id == "ARCH-G-002" for v in vs)

    def test_orchestrator_direct_provider(self):
        vs = _violations("from aios.runtime.providers import OpenAIProvider\n", "aios/orchestrator/planner.py")
        assert any(v.rule_id == "ARCH-G-002" for v in vs)

    def test_orchestrator_direct_sandbox(self):
        vs = _violations("from aios.skill.sandbox import Sandbox\n", "aios/orchestrator/planner.py")
        assert any(v.rule_id == "ARCH-G-002" for v in vs)


class TestDeterministicPath:
    def test_decision_pipeline_llm_without_rule(self):
        vs = _violations(
            "def decide(req):\n    return llm(req)\n",
            "aios/orchestrator/decision_pipeline.py",
        )
        assert any(v.rule_id == "ARCH-G-001" for v in vs)

    def test_decision_pipeline_with_rule_ok(self):
        vs = _violations(
            "from aios.orchestrator.rule_engine import RuleEngine\n"
            "def decide(req):\n    return llm(req)\n",
            "aios/orchestrator/decision_pipeline.py",
        )
        assert not any(v.rule_id == "ARCH-G-001" for v in vs)


class TestFailClosedGate:
    def test_gate_fails_on_violation(self):
        g = ArchitectureGate()
        res = g.evaluate_sources([
            ("import subprocess\n", "aios/skill/bad.py"),
            ("from aios.runtime.kernel import RuntimeKernel\n", "aios/skill/bad.py"),
        ])
        assert res.status == ViolationStatus.FAIL.value
        assert res.passed is False

    def test_gate_passes_clean(self):
        g = ArchitectureGate()
        res = g.evaluate_sources([
            ("from aios.capability.capability import CapabilityRegistry\n", "aios/skill/contracts.py"),
            ("from aios.orchestrator.planner import Planner\n", "aios/agents/coder.py"),
        ])
        assert res.status == ViolationStatus.PASS.value
        assert res.passed is True
