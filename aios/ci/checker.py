"""Local CI/CD checker — mirrors the GitHub Actions CI steps offline.

This lets you catch the same failures CI would, *before* pushing:

- dependency check (pytest, fastapi, pydantic must be importable — the exact
  thing that broke CI in TASK-017's test_api.py)
- pytest of ``aios/core/tests`` (the bootstrap step)
- pytest of the full ``aios`` suite (the full-suite step)

Three ways to use it
--------------------
1. Manual CLI::

       aiagent ci check                 # full suite
       aiagent ci check --scope core   # only the bootstrap step (fast)
       python -m aios.ci run --scope full

2. Programmatic (insert at the end of task processing)::

       from aios.ci.checker import run_ci_check
       report = run_ci_check(scope="full")
       if not report.overall.ok:
           ... block the task from being marked DONE ...

3. Automatic git hook (fail-closed gate at the push boundary)::

       aiagent ci install-hook         # installs .git/hooks/pre-push
       aiagent ci uninstall-hook
"""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Sequence

# Repo root == two levels up from this file (aios/ci/checker.py -> repo).
REPO_ROOT = Path(__file__).resolve().parents[2]

# Modules that must be importable for the CI steps to succeed.
REQUIRED_MODULES = ("pytest", "fastapi", "pydantic")

# Default timeouts (seconds) per scope so a hung test can't wedge the gate.
DEFAULT_TIMEOUT: dict[str, float | None] = {"core": 300.0, "full": 1200.0}

_SUMMARY_RE = re.compile(r"(\d+)\s+(passed|failed|errors?|skipped)")


class CIStatus(str, Enum):
    """Verdict for a single check or the whole report (fail-closed friendly)."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    UNKNOWN = "unknown"

    @property
    def ok(self) -> bool:
        """True when the gate should let the action proceed."""
        return self in (CIStatus.PASS, CIStatus.WARNING)


@dataclass
class CheckResult:
    name: str
    status: CIStatus = CIStatus.UNKNOWN
    detail: str = ""
    exit_code: int | None = None
    duration_s: float = 0.0
    passed: int = 0
    total: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status.value,
            "detail": self.detail,
            "exit_code": self.exit_code,
            "duration_s": round(self.duration_s, 3),
            "passed": self.passed,
            "total": self.total,
        }


@dataclass
class CIReport:
    results: list[CheckResult] = field(default_factory=list)
    scope: str = "full"

    @property
    def overall(self) -> CIStatus:
        if not self.results:
            return CIStatus.UNKNOWN
        if any(r.status is CIStatus.FAIL for r in self.results):
            return CIStatus.FAIL
        if any(r.status is CIStatus.UNKNOWN for r in self.results):
            return CIStatus.UNKNOWN
        return CIStatus.PASS

    def to_dict(self) -> dict:
        return {
            "overall": self.overall.value,
            "scope": self.scope,
            "results": [r.to_dict() for r in self.results],
        }

    def to_markdown(self) -> str:
        lines = [f"# CI Check Report — `{self.scope}`", "", f"**Overall:** {self.overall.value.upper()}", ""]
        for r in self.results:
            lines.append(f"- [{r.status.value.upper()}] **{r.name}** — {r.detail}")
        return "\n".join(lines)

    def print(self) -> None:
        for r in self.results:
            print(f"[{r.status.value.upper()}] {r.name}: {r.detail}")
        print(f"OVERALL: {self.overall.value.upper()}")


# A runner executes a command and returns (returncode, stdout, stderr).
Runner = Callable[[Sequence[str], float | None], tuple[int, str, str]]


def _default_runner(cmd: Sequence[str], timeout: float | None) -> tuple[int, str, str]:
    proc = subprocess.run(
        list(cmd),
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


class CIChecker:
    """Runs the CI steps locally and produces a :class:`CIReport`."""

    def __init__(self, runner: Runner | None = None, workspace: Path | None = None) -> None:
        self._runner = runner or _default_runner
        self._ws = workspace or REPO_ROOT

    # -- individual checks -------------------------------------------------

    def check_dependencies(self) -> CheckResult:
        start = time.time()
        missing = [m for m in REQUIRED_MODULES if importlib.util.find_spec(m) is None]
        dur = time.time() - start
        if missing:
            return CheckResult(
                "dependencies",
                CIStatus.FAIL,
                f"missing modules: {', '.join(missing)} (run: pip install -e \".[dev,api]\")",
                duration_s=dur,
            )
        return CheckResult(
            "dependencies",
            CIStatus.PASS,
            f"all present: {', '.join(REQUIRED_MODULES)}",
            duration_s=dur,
        )

    def check_pytest(self, name: str, target: str, timeout: float | None = None) -> CheckResult:
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            target,
            "-q",
            "--tb=short",
            "-p",
            "no:cacheprovider",
        ]
        start = time.time()
        try:
            code, out, err = self._runner(cmd, timeout)
        except subprocess.TimeoutExpired:
            return CheckResult(name, CIStatus.FAIL, "timed out", duration_s=time.time() - start)
        dur = time.time() - start
        passed, total = self._parse_summary(out + "\n" + err)
        if code == 0:
            status = CIStatus.PASS
            detail = f"{passed}/{total} passed"
        else:
            status = CIStatus.FAIL
            detail = f"exit={code}; {passed}/{total} passed"
        return CheckResult(name, status, detail, exit_code=code, duration_s=dur, passed=passed, total=total)

    @staticmethod
    def _parse_summary(text: str) -> tuple[int, int]:
        passed = failed = errors = skipped = 0
        for m in _SUMMARY_RE.finditer(text):
            n = int(m.group(1))
            kind = m.group(2)
            if kind == "passed":
                passed += n
            elif kind == "failed":
                failed += n
            elif kind.startswith("error"):
                errors += n
            elif kind == "skipped":
                skipped += n
        total = passed + failed + errors + skipped
        return passed, total

    # -- orchestration -----------------------------------------------------

    def run(self, scope: str = "full", timeout: float | None = None) -> CIReport:
        """Run the requested CI scope and return a report.

        scope="core" -> dependencies + aios/core/tests
        scope="full" -> dependencies + aios/core/tests + aios (full suite)
        """
        if scope not in ("core", "full"):
            raise ValueError(f"unknown scope: {scope!r} (expected 'core' or 'full')")

        report = CIReport(scope=scope)
        deps = self.check_dependencies()
        report.results.append(deps)

        # Fail-closed short-circuit: without deps the suites can't possibly pass.
        if deps.status is CIStatus.FAIL:
            return report

        report.results.append(
            self.check_pytest("core-tests", "aios/core/tests", timeout or DEFAULT_TIMEOUT["core"])
        )
        if scope == "full":
            report.results.append(
                self.check_pytest("full-suite", "aios", timeout or DEFAULT_TIMEOUT["full"])
            )
        return report


def run_ci_check(scope: str = "full", timeout: float | None = None) -> CIReport:
    """Programmatic entry point — call at the end of task processing."""
    return CIChecker().run(scope=scope, timeout=timeout)
