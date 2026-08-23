"""Unit + Contract + Integration + Architecture + Regression tests (TASK-133)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aios.coder.prompt import BuiltPrompt, PromptBuilder, PromptError, PromptRegistry


# --------------------------------------------------------------------------- #
# Versioning / immutable
# --------------------------------------------------------------------------- #
def test_register_and_get():
    reg = PromptRegistry()
    tpl = reg.register("codegen", "1.0", "Write {{fn}} in {{lang}}")
    assert tpl.version == "1.0"
    assert reg.get("codegen", "1.0").body == "Write {{fn}} in {{lang}}"


def test_duplicate_version_rejected():
    reg = PromptRegistry()
    reg.register("codegen", "1.0", "x")
    with pytest.raises(PromptError):
        reg.register("codegen", "1.0", "y")  # immutable (T001 Rule 1)


def test_latest_version():
    reg = PromptRegistry()
    reg.register("codegen", "1.0", "x")
    reg.register("codegen", "2.0", "y")
    assert reg.latest("codegen").version == "2.0"


# --------------------------------------------------------------------------- #
# Deterministic build
# --------------------------------------------------------------------------- #
def test_build_renders_variables():
    reg = PromptRegistry()
    reg.register("codegen", "1.0", "Write {{fn}} in {{lang}}")
    b = PromptBuilder(reg).build("codegen", "1.0", {"fn": "f", "lang": "py"})
    assert b.content == "Write f in py"
    assert len(b.content_hash) == 64


def test_build_deterministic():
    reg = PromptRegistry()
    reg.register("codegen", "1.0", "Write {{fn}} in {{lang}}")
    a = PromptBuilder(reg).build("codegen", "1.0", {"fn": "f", "lang": "py"})
    b = PromptBuilder(reg).build("codegen", "1.0", {"fn": "f", "lang": "py"})
    assert a.content_hash == b.content_hash


def test_build_missing_variable_rejected():
    reg = PromptRegistry()
    reg.register("codegen", "1.0", "Write {{fn}} in {{lang}}")
    with pytest.raises(PromptError):
        PromptBuilder(reg).build("codegen", "1.0", {"fn": "f"})


def test_build_unresolved_placeholder_rejected():
    reg = PromptRegistry()
    # variable name mismatch leaves placeholder -> fail-closed (T078)
    reg.register("codegen", "1.0", "Write {{fn}} in {{lang}}")
    with pytest.raises(PromptError):
        PromptBuilder(reg).build("codegen", "1.0", {"fn": "f", "lang": "{{leak}}"})


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #
def test_built_prompt_has_evidence():
    reg = PromptRegistry()
    reg.register("codegen", "1.0", "Write {{fn}}")
    b: BuiltPrompt = PromptBuilder(reg).build("codegen", "1.0", {"fn": "f"})
    assert b.evidence_id.startswith("ev-")


# --------------------------------------------------------------------------- #
# Architecture — no forbidden imports
# --------------------------------------------------------------------------- #
def test_module_has_no_forbidden_imports():
    src = Path(__file__).resolve().parents[1] / "prompt.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    forbidden = {"subprocess", "os", "aios.runtime.providers", "aios.runtime.filesystem"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert not (imported & forbidden), f"forbidden imports: {imported & forbidden}"
