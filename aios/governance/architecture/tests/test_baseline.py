"""TASK-063 — Architecture 1.0 freeze test matrix + baseline codification.

Covers the full acceptance test matrix from ``docs/detailtask/T063.md``:
agent->subprocess (ARCH-001), agent->provider (ARCH-002), agent->filesystem
(ARCH-003), tool->runtime skip-layer (ARCH-004), correct downward (PASS),
parse error (fail-closed BLOCK), and determinism (same source + version).
"""

import pytest

from aios.governance.architecture import (
    ARCHITECTURE_VERSION,
    ArchitectureError,
    ArchitectureGuard,
    Violation,
    frozen_arch_rules,
    frozen_layer_contract,
    scan_source,
)
from aios.governance.architecture.guard import LAYER_ORDER


# ---------------------------------------------------------------------------
# Test matrix (T063 §7)
# ---------------------------------------------------------------------------
class TestT063Matrix:
    def test_agent_import_subprocess_arch001_fail(self):
        code = "import subprocess\n"
        vs = scan_source(code, module_path="aios/agents/my_agent.py")
        assert any(v.rule == "ARCH-001" for v in vs)

    def test_agent_import_provider_arch002_fail(self):
        code = "from aios.core.providers import OpenAIProvider\n"
        vs = scan_source(code, module_path="aios/agents/spec_writer.py")
        assert any(v.rule == "ARCH-002" for v in vs)

    def test_agent_import_filesystem_arch003_fail(self):
        code = "from aios.runtime.filesystem import read_file\n"
        vs = scan_source(code, module_path="aios/agents/critic.py")
        assert any(v.rule == "ARCH-003" for v in vs)

    def test_tool_import_runtime_arch004_fail(self):
        """tool importing runtime is an upward/skip-layer import -> ARCH-004."""
        code = "from aios.runtime.kernel import RuntimeKernel\n"
        vs = scan_source(code, module_path="aios/tool/python_tool.py")
        assert any(v.rule == "ARCH-004" for v in vs)

    def test_correct_downward_import_passes(self):
        code = "from aios.orchestrator.planner import Planner\n"
        vs = scan_source(code, module_path="aios/agents/coder.py")
        assert vs == [], vs

    def test_parse_error_blocks_fail_closed(self):
        with pytest.raises(ArchitectureError):
            scan_source("def broken(:", module_path="aios/agents/bad.py")

    def test_deterministic_same_source_same_result(self):
        code = "import subprocess\n"
        path = "aios/agents/bad.py"
        a = scan_source(code, module_path=path)
        b = scan_source(code, module_path=path)
        assert [ (v.rule, v.module, v.detail, v.line) for v in a ] == \
               [ (v.rule, v.module, v.detail, v.line) for v in b ]


# ---------------------------------------------------------------------------
# Baseline codification (T063 §2 / ADR-ARCH-1.0)
# ---------------------------------------------------------------------------
class TestBaselineCodification:
    def test_architecture_version_is_1_0(self):
        assert ARCHITECTURE_VERSION == "1.0"

    def test_frozen_layer_contract_matches_guard(self):
        assert frozen_layer_contract() == LAYER_ORDER
        assert frozen_layer_contract() == [
            "api", "agent", "orchestrator", "worker",
            "runtime", "skill", "capability", "tool",
        ]

    def test_frozen_arch_rules_cover_001_to_004(self):
        rules = frozen_arch_rules()
        for r in ("ARCH-001", "ARCH-002", "ARCH-003", "ARCH-004"):
            assert r in rules

    def test_frozen_contract_is_copy_not_alias(self):
        contract = frozen_layer_contract()
        contract.append("mutated")
        # mutating the returned copy must not change the source of truth
        assert frozen_layer_contract() == LAYER_ORDER

    def test_gate_fail_closed_on_violation(self):
        guard = ArchitectureGuard()
        result = guard.check(sources=[("import os\n", "aios/agents/x.py")])
        assert result.passed is False
        assert isinstance(result.violations[0], Violation)
