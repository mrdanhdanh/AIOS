"""Automated tests for the Architecture Guard gate (Rule 3)."""

from aios.governance.architecture import (
    ArchitectureGuard,
    ArchitectureError,
    Violation,
    scan_source,
)


def test_agent_importing_subprocess_fails():
    """Rule 3 / ARCH-001: agent importing subprocess directly -> FAIL."""
    code = (
        "import subprocess\n"
        "\n"
        "class MyAgent:\n"
        "    def run(self):\n"
        "        subprocess.run(['ls'])\n"
    )
    violations = scan_source(code, module_path="aios/agents/my_agent.py")
    rules = {v.rule for v in violations}
    assert "ARCH-001" in rules
    assert any("subprocess" in v.detail for v in violations)


def test_agent_importing_provider_fails():
    """Rule 3 / ARCH-002: agent importing provider adapter directly -> FAIL."""
    code = "from aios.core.providers import OpenAIProvider\n"
    violations = scan_source(code, module_path="aios/agents/spec_writer.py")
    assert any(v.rule == "ARCH-002" for v in violations)


def test_agent_importing_filesystem_fails():
    """Rule 3 / ARCH-003: agent importing filesystem adapter directly -> FAIL."""
    code = "from aios.runtime.filesystem import read_file\n"
    violations = scan_source(code, module_path="aios/agents/critic.py")
    assert any(v.rule == "ARCH-003" for v in violations)


def test_clean_agent_module_passes():
    code = (
        "from aios.governance.task_registry import TaskRegistry\n"
        "\n"
        "class OrchestratorClient:\n"
        "    pass\n"
    )
    violations = scan_source(code, module_path="aios/agents/orchestrator.py")
    assert violations == [], violations


def test_gate_result_converges():
    guard = ArchitectureGuard()
    bad = ("import os\n", "aios/agents/bad.py")
    good = ("from aios.governance import TaskRegistry\n", "aios/agents/good.py")
    result = guard.check(sources=[bad, good])
    assert result.passed is False
    assert len(result.violations) >= 1


def test_syntax_error_raises():
    with __import__("pytest").raises(ArchitectureError):
        scan_source("def broken(:", module_path="x.py")
