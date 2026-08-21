"""Architecture tests for orchestrator — AC-010-09 (TASK-010)."""

import ast
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
ORCH_DIR = REPO_ROOT / "aios" / "orchestrator"


def _imports_of(path: pathlib.Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.append(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.append(node.module)
    return out


class TestOrchestratorArchitecture:
    def test_orchestrator_does_not_import_agents(self):
        violations: list[str] = []
        for p in ORCH_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod.startswith("aios.agents"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "\n".join(violations)

    def test_orchestrator_does_not_import_tool_directly(self):
        # Orchestrator may import runtime/capability, but not concrete tool adapters
        violations: list[str] = []
        for p in ORCH_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if "aios.runtime.providers" in mod or "aios.runtime.filesystem" in mod:
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
                if mod.startswith("aios.tool"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "\n".join(violations)

    def test_planner_does_not_execute_tool(self):
        # Planner should not import subprocess/os/tool execution
        violations: list[str] = []
        for p in ORCH_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            text = p.read_text(encoding="utf-8")
            for mod in _imports_of(p):
                if mod in ("subprocess", "os") and "planner" in p.name:
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "\n".join(violations)

    def test_orchestrator_only_imports_allowed_layers(self):
        # Orchestrator layer may import runtime/capability/tool/unknown per guard
        from aios.governance.architecture.guard import scan_source

        violations: list[str] = []
        for p in ORCH_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            text = p.read_text(encoding="utf-8")
            # Use guard to check layering
            vs = scan_source(text, str(p.relative_to(REPO_ROOT)).replace("\\", "/"))
            for v in vs:
                if v.rule == "ARCH-004":
                    violations.append(f"{v.module}:{v.line} {v.detail}")
        assert violations == [], "\n".join(violations)
