"""Architecture tests for Tool + Capability Layer — AC-014-09 (TASK-014)."""

import ast
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
TOOL_DIR = REPO_ROOT / "aios" / "tool"
RUNTIME_ROUTER = REPO_ROOT / "aios" / "runtime" / "capability_router.py"
WORKER_DIR = REPO_ROOT / "aios" / "worker"
AGENTS_DIR = REPO_ROOT / "aios" / "agents"


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


class TestToolLayering:
    """Tool must not import runtime / agent / orchestrator / capability (AC-014-09)."""

    def test_tool_does_not_import_runtime_agent_orchestrator(self):
        violations: list[str] = []
        for p in TOOL_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod.startswith("aios.runtime") or mod.startswith("aios.agents") or mod.startswith("aios.orchestrator") or mod.startswith("aios.capability"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
                if mod.startswith("aios.worker"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "Tool layer violation:\n" + "\n".join(violations)

    def test_tool_only_core_and_stdlib(self):
        violations: list[str] = []
        for p in TOOL_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod.startswith("aios.runtime") or mod.startswith("aios.agents") or mod.startswith("aios.orchestrator"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "\n".join(violations)

    def test_tool_does_not_import_subprocess(self):
        violations: list[str] = []
        for p in TOOL_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod in ("subprocess", "os") and "adapters" in p.name:
                    # adapters should not import subprocess/os for execution
                    text = p.read_text(encoding="utf-8")
                    if "subprocess" in text or "os.system" in text:
                        violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod} and uses it")
        # Check no actual subprocess import (not just docstring mention)
        for p in TOOL_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            imports = _imports_of(p)
            if "subprocess" in imports:
                violations.append(f"{p.relative_to(REPO_ROOT)} imports subprocess")
        assert violations == [], "\n".join(violations)


class TestRouterLayering:
    """Router is at runtime layer — may import tool/capability, not agent/orchestrator."""

    def test_router_does_not_import_agent_orchestrator(self):
        violations: list[str] = []
        for mod in _imports_of(RUNTIME_ROUTER):
            if mod.startswith("aios.agents") or mod.startswith("aios.orchestrator"):
                violations.append(f"capability_router.py imports {mod}")
        assert violations == [], "\n".join(violations)

    def test_router_may_import_tool_and_capability(self):
        # Router SHOULD import tool and capability — that's its job
        imports = _imports_of(RUNTIME_ROUTER)
        assert any("aios.tool" in m for m in imports), "Router should import aios.tool"
        # Capability import is optional (via try), but should be present
        text = RUNTIME_ROUTER.read_text(encoding="utf-8")
        assert "ToolRegistry" in text
        assert "CapabilityRequest" in text

    def test_router_does_not_execute_tool(self):
        text = RUNTIME_ROUTER.read_text(encoding="utf-8")
        # Router should not directly execute tools
        assert "adapter.execute" not in text
        # Router should not import subprocess
        assert "subprocess" not in text


class TestWorkerIsolation:
    """Worker/Agent must not import Tool directly (AC-014-09)."""

    def test_worker_does_not_import_tool(self):
        violations: list[str] = []
        for p in WORKER_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod.startswith("aios.tool"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "Worker must not import aios.tool directly:\n" + "\n".join(violations)

    def test_agents_do_not_import_tool(self):
        violations: list[str] = []
        for p in AGENTS_DIR.rglob("*.py"):
            for mod in _imports_of(p):
                if mod.startswith("aios.tool"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "\n".join(violations)

    def test_worker_does_not_import_subprocess(self):
        violations: list[str] = []
        for p in WORKER_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod in ("subprocess",):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "\n".join(violations)


class TestCapabilityRouterNotGodObject:
    """Router should be resolver only, not executor or God Object."""

    def test_router_is_resolver_not_executor(self):
        text = RUNTIME_ROUTER.read_text(encoding="utf-8")
        # Router should have resolve method, not execute
        assert "def resolve" in text
        # Should not have execute that runs tool
        assert "def execute" not in text or "adapter" not in text

    def test_router_does_not_import_execution(self):
        imports = _imports_of(RUNTIME_ROUTER)
        for mod in imports:
            assert "aios.runtime.execution" not in mod, f"Router should not import execution: {mod}"

    def test_tool_does_not_import_orchestrator(self):
        for p in TOOL_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                assert not mod.startswith("aios.orchestrator"), f"{p} imports {mod}"


class TestArchitectureGuard:
    """Verify guard still passes for new layers."""

    def test_guard_passes_for_tool_and_router(self):
        from aios.governance.architecture.guard import scan_source

        violations: list[str] = []
        for p in TOOL_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            text = p.read_text(encoding="utf-8")
            vs = scan_source(text, str(p.relative_to(REPO_ROOT)).replace("\\", "/"))
            for v in vs:
                if v.rule == "ARCH-004":
                    violations.append(f"{v.module}:{v.line} {v.detail}")
        assert violations == [], "\n".join(violations)

        # Router
        text = RUNTIME_ROUTER.read_text(encoding="utf-8")
        vs = scan_source(text, "aios/runtime/capability_router.py")
        arch_violations = [v for v in vs if v.rule == "ARCH-004"]
        assert arch_violations == [], f"Router ARCH-004 violations: {arch_violations}"
