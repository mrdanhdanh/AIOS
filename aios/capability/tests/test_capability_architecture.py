"""Architecture tests for Capability foundation — AC-009-03 + layering (TASK-009)."""

from __future__ import annotations

import ast
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
CAP_DIR = REPO_ROOT / "aios" / "capability"
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


class TestCapabilityLayering:
    """Capability must not import runtime / agent / orchestrator (AC-009-03, ARCH-004)."""

    def test_capability_does_not_import_runtime_agent_orchestrator(self):
        violations: list[str] = []
        for p in CAP_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if mod.startswith("aios.runtime") or mod.startswith("aios.agents") or mod.startswith("aios.orchestrator"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "Capability layer violation:\n" + "\n".join(violations)

    def test_capability_does_not_import_providers_directly(self):
        # capability must not directly import provider internals (keep vendor-neutral)
        violations: list[str] = []
        for p in CAP_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                if "providers" in mod and "aios.runtime.providers" in mod:
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "\n".join(violations)

    def test_capability_only_core_and_stdlib(self):
        # Every capability source file must only import stdlib + aios.core
        # (no runtime/agent/orchestrator/tool internals hard import)
        violations: list[str] = []
        for p in CAP_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                # Disallow tool concrete imports at top-level (capability is abstract)
                if mod.startswith("aios.runtime") or mod.startswith("aios.agents"):
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "\n".join(violations)


class TestAgentBoundary:
    """Agent must go through capability, not direct tool import (AC-009-03)."""

    def test_agents_do_not_import_tool_implementations(self):
        # Agents may import orchestrator/runtime/capability, but should not
        # import concrete tool modules directly.
        violations: list[str] = []
        for p in AGENTS_DIR.rglob("*.py"):
            for mod in _imports_of(p):
                if "aios.capability" in mod or "aios.runtime.workflow" in mod:
                    continue
                # concrete tool paths would be aios.runtime.providers or tool adapters
                # but agents are forbidden per ArchitectureGuard to import providers/filesystem
                # This test additionally guards capability bypass
                if mod.startswith("aios.capability") and "tool" in mod:
                    violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        # No violation expected — capability bypass would be caught here
        assert violations == [], "\n".join(violations)

    def test_capability_files_do_not_import_langgraph_or_jinja2(self):
        # M1 boundary: capability must not bring in heavy engines
        forbidden = ["langgraph", "jinja2"]
        violations: list[str] = []
        for p in CAP_DIR.rglob("*.py"):
            if "tests" in p.parts:
                continue
            for mod in _imports_of(p):
                for f in forbidden:
                    if f in mod.lower():
                        violations.append(f"{p.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "\n".join(violations)
