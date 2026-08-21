"""Layer dependency validation tests (TASK-016 16.9).

Covers allowed/denied import matrix and reverse dependencies via both the
per-file scanner and the dependency graph.
"""

import pytest

from aios.governance.architecture.guard import (
    ALLOWED_IMPORT_LAYERS,
    LAYER_ORDER,
    classify_module,
)
from aios.governance.architecture.scanner import scan_source_extended
from aios.governance.architecture.rules import (
    evaluate_scan_result,
    evaluate_graph,
)
from aios.governance.architecture.graph import DependencyGraph


# ---------------------------------------------------------------------------
# Allowed matrix
# ---------------------------------------------------------------------------
class TestAllowedMatrix:
    @pytest.mark.parametrize(
        "code,path,allowed",
        [
            ("from aios.orchestrator.planner import Planner\n", "aios/agents/coder.py", True),
            ("from aios.agents.coder import Coder\n", "aios/orchestrator/planner.py", False),
            ("from aios.capability.capability import CapabilityRegistry\n", "aios/skill/contracts.py", True),
            ("from aios.runtime.kernel import RuntimeKernel\n", "aios/skill/bad.py", False),
            ("from aios.tool.python_tool import PythonTool\n", "aios/capability/capability.py", False),
            ("import json\n", "aios/agent/x.py", True),
        ],
    )
    def test_matrix(self, code, path, allowed):
        vs = evaluate_scan_result(scan_source_extended(code, path))
        arch004 = [v for v in vs if v.rule_id == "ARCH-004"]
        if allowed:
            assert not arch004, f"expected allowed but got {arch004}"
        else:
            assert arch004, "expected ARCH-004 denial"


# ---------------------------------------------------------------------------
# Reverse dependency (ARCH-C)
# ---------------------------------------------------------------------------
class TestReverseDependency:
    def test_tool_imports_agent_reverse(self):
        g = DependencyGraph()
        g.add_edge("aios/tool/python_tool.py", "aios/agents/coder.py")
        rev = g.find_reverse_dependencies()
        assert any("python_tool" in s and "coder" in d for s, d, _ in rev)

    def test_capability_imports_agent_reverse(self):
        g = DependencyGraph()
        g.add_edge("aios/capability/capability.py", "aios/agents/coder.py")
        rev = g.find_reverse_dependencies()
        assert rev

    def test_valid_edge_not_reverse(self):
        g = DependencyGraph()
        g.add_edge("aios/agents/coder.py", "aios/orchestrator/planner.py")
        assert not g.find_reverse_dependencies()

    def test_reverse_detected_in_graph_eval(self):
        g = DependencyGraph()
        g.add_edge("aios/tool/python_tool.py", "aios/agents/coder.py")
        vs = evaluate_graph(g)
        assert any(v.rule_id == "ARCH-C-001" for v in vs)


# ---------------------------------------------------------------------------
# Layer ordering consistency
# ---------------------------------------------------------------------------
class TestLayerOrdering:
    def test_skill_in_layer_order(self):
        assert "skill" in LAYER_ORDER

    def test_skill_allowed_subset(self):
        allowed = ALLOWED_IMPORT_LAYERS["skill"]
        assert "capability" in allowed
        assert "runtime" not in allowed
        assert "tool" not in allowed

    def test_unknown_allows_everything(self):
        for layer in LAYER_ORDER:
            assert layer in ALLOWED_IMPORT_LAYERS["unknown"]
