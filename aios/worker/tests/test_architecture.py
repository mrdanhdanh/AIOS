"""Architecture tests for Worker Plane — AC-013-10 (TASK-013)."""

import ast
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKER_DIR = REPO_ROOT / "aios" / "worker"


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


class TestWorkerArchitecture:
    def test_worker_does_not_import_runtime(self):
        violations: list[str] = []
        for p in WORKER_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod.startswith("aios.runtime"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "Worker must not import runtime:\n" + "\n".join(violations)

    def test_worker_does_not_import_orchestrator(self):
        violations: list[str] = []
        for p in WORKER_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod.startswith("aios.orchestrator"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "Worker must not import orchestrator:\n" + "\n".join(violations)

    def test_worker_does_not_import_agents(self):
        violations: list[str] = []
        for p in WORKER_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod.startswith("aios.agents"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "Worker must not import agents:\n" + "\n".join(violations)

    def test_worker_does_not_import_tool_directly(self):
        violations: list[str] = []
        for p in WORKER_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod.startswith("aios.tool"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
                if "aios.runtime.providers" in mod or "aios.runtime.filesystem" in mod:
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "Worker must not import tool directly:\n" + "\n".join(violations)

    def test_worker_does_not_import_subprocess_or_os(self):
        violations: list[str] = []
        for p in WORKER_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod in ("subprocess", "os"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "Worker must not import subprocess/os:\n" + "\n".join(violations)

    def test_worker_does_not_import_providers(self):
        violations: list[str] = []
        for p in WORKER_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if "providers" in mod and "aios.runtime.providers" in mod:
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
                if mod == "providers" or mod.startswith("providers."):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "Worker must not import providers:\n" + "\n".join(violations)

    def test_worker_only_imports_allowed_layers(self):
        from aios.governance.architecture.guard import scan_source

        violations: list[str] = []
        for p in WORKER_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            text = p.read_text(encoding="utf-8")
            vs = scan_source(text, str(p.relative_to(REPO_ROOT)).replace("\\", "/"))
            for v in vs:
                violations.append(f"{v.module}:{v.line} {v.rule} {v.detail}")
        assert violations == [], "Worker architecture violations:\n" + "\n".join(violations)

    def test_worker_guard_classification(self):
        from aios.governance.architecture.guard import classify_module

        assert classify_module("aios/worker/contract.py") == "worker"
        assert classify_module("aios/worker/execution.py") == "worker"
        assert classify_module("aios/worker/workers.py") == "worker"
        assert classify_module("aios/worker/tests/test_contract.py") == "worker"

    def test_worker_forbidden_imports_detected(self):
        from aios.governance.architecture.guard import scan_source

        # Worker importing subprocess should fail
        code = "import subprocess\n"
        violations = scan_source(code, module_path="aios/worker/execution.py")
        assert any(v.rule == "ARCH-001" for v in violations), "Worker subprocess import should be ARCH-001"

        # Worker importing runtime should fail ARCH-004
        code2 = "from aios.runtime.kernel import RuntimeKernel\n"
        violations2 = scan_source(code2, module_path="aios/worker/execution.py")
        assert any(v.rule == "ARCH-004" for v in violations2), "Worker runtime import should be ARCH-004"

        # Worker importing capability should pass
        code3 = "from aios.capability.capability import CapabilityRegistry\n"
        violations3 = scan_source(code3, module_path="aios/worker/execution.py")
        assert violations3 == [], f"Worker capability import should pass, got {violations3}"

    def test_worker_does_not_call_tool_directly(self):
        # Verify no direct Tool class instantiation or tool method calls
        violations: list[str] = []
        for p in WORKER_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            text = p.read_text(encoding="utf-8")
            # Check for direct tool patterns (heuristic)
            if "Tool(" in text and "CapabilityRegistry" not in text:
                # Allow only if it's in a comment or test
                lines = text.split("\n")
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    if "Tool(" in line and "import" not in line and "capability" not in line.lower():
                        # Check if it's actually a tool instantiation
                        if any(t in line for t in ["PythonTool", "DockerTool", "ShellTool", "GitTool"]):
                            violations.append(f"{p.relative_to(REPO_ROOT)}:{i} direct Tool instantiation: {line.strip()}")
        assert violations == [], "Worker must not instantiate Tool directly:\n" + "\n".join(violations)
