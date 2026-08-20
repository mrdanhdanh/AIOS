"""Architecture boundary tests for TASK-002.

Ensures aios.core (runtime foundation) does not depend on upper layers
that must not exist at M1 foundation stage:
  - aios.agents / aios.runtime / aios.governance / aios.harness
  - LLM / provider specifics

Also validates package importability and layout conventions.
"""
from __future__ import annotations

import ast
import pathlib


# Resolve aios/core directory
CORE_DIR = pathlib.Path(__file__).parent.parent  # aios/core
REPO_ROOT = CORE_DIR.parent.parent  # repo root

# Upper-layer prefixes that core must NOT import
FORBIDDEN_PREFIXES = (
    "aios.agents",
    "aios.runtime",
    "aios.governance",
    "aios.harness",
    "openai",
    "anthropic",
    "langchain",
)


def _iter_core_py_files():
    for p in CORE_DIR.rglob("*.py"):
        # skip tests and __pycache__
        if "tests" in p.parts or "__pycache__" in p.parts:
            continue
        yield p


def _imports_of(path: pathlib.Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.append(node.module)
    return out


class TestArchitectureBoundary:
    def test_core_does_not_import_upper_layers(self):
        violations: list[str] = []
        for py in _iter_core_py_files():
            for mod in _imports_of(py):
                for prefix in FORBIDDEN_PREFIXES:
                    if mod == prefix or mod.startswith(prefix + "."):
                        violations.append(f"{py.relative_to(REPO_ROOT)} imports {mod}")
        assert violations == [], "Architecture boundary violated:\n" + "\n".join(violations)

    def test_core_package_importable_without_upper_layers(self):
        # Re-import smoke for each core submodule
        import importlib
        for mod in [
            "aios.core.config",
            "aios.core.logging",
            "aios.core.healthcheck",
            "aios.core.metadata",
        ]:
            assert importlib.import_module(mod) is not None

    def test_configs_directory_exists(self):
        assert (REPO_ROOT / "configs").is_dir(), "configs/ directory required by M1 spec"
        # at least default.yaml present
        assert (REPO_ROOT / "configs" / "default.yaml").exists()

    def test_ci_workflow_exists(self):
        assert (REPO_ROOT / ".github" / "workflows" / "ci.yml").exists(), "CI workflow required for TASK-002 DoD"

    def test_healthcheck_distinguishes_three_states(self):
        from aios.core.healthcheck import HealthStatus
        # spec: healthy / unhealthy / not-ready|unavailable
        assert HealthStatus.HEALTHY
        assert HealthStatus.UNHEALTHY
        # not-ready / unavailable both exist and are considered not-ready
        assert HealthStatus.NOT_READY
        assert HealthStatus.UNAVAILABLE
        assert HealthStatus.NOT_READY.is_not_ready
        assert HealthStatus.UNAVAILABLE.is_not_ready
        # DEGRADED is backward-compat alias of not-ready
        assert HealthStatus.DEGRADED.is_not_ready
        assert not HealthStatus.HEALTHY.is_not_ready
        assert not HealthStatus.UNHEALTHY.is_not_ready

    def test_healthcheck_not_ready_takes_precedence(self):
        from aios.core.healthcheck import HealthCheck, HealthStatus
        hc = HealthCheck(ready=False)
        hc.mark_not_ready("bootstrapping")
        result = hc.run()
        assert result.status == HealthStatus.NOT_READY
        # even if no probes failed, not-ready dominates
        assert any(p.name == "_readiness" for p in result.probes)

    def test_healthcheck_unhealthy_via_critical_probe(self):
        from aios.core.healthcheck import HealthCheck, HealthStatus

        def boom():
            raise RuntimeError("critical down")

        hc = HealthCheck()
        hc.register("critical_dep", boom, critical=True)
        result = hc.run()
        assert result.status == HealthStatus.UNHEALTHY

    def test_healthcheck_degraded_via_non_critical_probe(self):
        from aios.core.healthcheck import HealthCheck, HealthStatus

        def boom():
            raise RuntimeError("non-critical down")

        hc = HealthCheck()
        hc.register("cache", boom)  # non-critical by default
        result = hc.run()
        assert result.status == HealthStatus.DEGRADED
