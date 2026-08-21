"""Architecture tests for Skill — AC-015-04/05 (TASK-015)."""

import ast
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SKILL_DIR = REPO_ROOT / "aios" / "skill"


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


class TestSkillLayering:
    """Skill contracts/registry/resolver must not import runtime/agent/orchestrator."""

    def test_skill_contracts_no_runtime(self):
        violations = []
        for p in SKILL_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            if p.name in ("manager.py", "sandbox.py"):
                continue  # manager/sandbox are runtime-level, allowed to use runtime
            for mod in _imports_of(p):
                if mod.startswith("aios.runtime") or mod.startswith("aios.agents") or mod.startswith("aios.orchestrator"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "Skill layer violation:\n" + "\n".join(violations)

    def test_skill_no_subprocess(self):
        violations = []
        for p in SKILL_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod in ("subprocess", "os") and "manager" not in p.name and "sandbox" not in p.name:
                    # Only manager/sandbox may use threading, but not subprocess
                    if mod == "subprocess":
                        violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        # Check actual subprocess import (not just string)
        for p in SKILL_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            text = p.read_text(encoding="utf-8")
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        if a.name == "subprocess":
                            violations.append(f"{p.relative_to(REPO_ROOT)} imports subprocess")
                elif isinstance(node, ast.ImportFrom):
                    if node.module == "subprocess":
                        violations.append(f"{p.relative_to(REPO_ROOT)} imports subprocess")
        assert violations == [], "\n".join(violations)

    def test_skill_no_provider_import(self):
        violations = []
        for p in SKILL_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if "aios.runtime.providers" in mod or "aios.core.providers" in mod:
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "\n".join(violations)

    def test_skill_manager_no_direct_runtime_import(self):
        """Manager uses duck typing, not direct runtime imports."""
        p = SKILL_DIR / "manager.py"
        text = p.read_text(encoding="utf-8")
        # Manager should not have top-level "from aios.runtime" import
        tree = ast.parse(text)
        top_level_runtime = []
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("aios.runtime"):
                top_level_runtime.append(node.module)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.startswith("aios.runtime"):
                        top_level_runtime.append(a.name)
        assert top_level_runtime == [], f"manager.py should not have top-level runtime imports: {top_level_runtime}"

    def test_skill_sandbox_no_subprocess(self):
        p = SKILL_DIR / "sandbox.py"
        text = p.read_text(encoding="utf-8")
        assert "import subprocess" not in text
        assert "from subprocess" not in text


class TestSkillCapabilityBoundary:
    """Skill must use capability contract, not hard-code tool."""

    def test_skill_contracts_no_tool_import(self):
        violations = []
        for p in SKILL_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            if p.name in ("manager.py",):
                continue  # manager may reference tool via capability router duck typing
            for mod in _imports_of(p):
                if mod.startswith("aios.tool"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "\n".join(violations)

    def test_skill_does_not_hardcode_tool(self):
        # Skill contracts should declare required_capabilities, not tool_ids
        from aios.skill.contracts import SkillContract
        c = SkillContract.create(
            skill_id="test-skill",
            version="1.0.0",
            entrypoint="skill.main:run",
            required_capabilities=["execute_code"],
        )
        assert "execute_code" in c.required_capabilities
        # Should not have tool_id field
        assert not hasattr(c, "tool_id")


class TestArchitectureGuard:
    """Verify guard catches skill violations."""

    def test_guard_catches_skill_subprocess(self):
        from aios.governance.architecture.guard import scan_source
        violations = scan_source("import subprocess\n", "aios/skill/bad.py")
        assert any(v.rule == "ARCH-001" for v in violations)

    def test_guard_catches_skill_runtime_import(self):
        from aios.governance.architecture.guard import scan_source
        violations = scan_source("from aios.runtime.kernel import RuntimeKernel\n", "aios/skill/bad.py")
        assert any(v.rule == "ARCH-004" for v in violations)

    def test_guard_skill_layer_allowed(self):
        from aios.governance.architecture.guard import scan_source
        # Skill importing capability should be allowed
        violations = scan_source("from aios.capability.capability import CapabilityRegistry\n", "aios/skill/contracts.py")
        # This should not be a violation — skill may import capability
        # But contracts.py is skill layer, capability is below skill, so allowed
        assert not any(v.rule == "ARCH-004" for v in violations)

    def test_guard_classify_skill(self):
        from aios.governance.architecture.guard import classify_module
        assert classify_module("aios/skill/contracts.py") == "skill"
        assert classify_module("aios/skill/manager.py") == "skill"
        assert classify_module("aios/skill/sandbox.py") == "skill"
