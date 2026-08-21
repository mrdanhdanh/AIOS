"""Harness kernel — lifecycle driver for harness runs."""

from __future__ import annotations

import threading
from typing import Any, Callable

from aios.harness.contracts import HarnessError, HarnessRun, HarnessSpec, RunResult, RunStatus


class KernelError(Exception):
    """Raised on harness kernel errors."""


StepFunc = Callable[[HarnessRun, HarnessSpec], None]


class HarnessKernel:
    """Drives harness runs through their lifecycle.

    AC-029-03: Lifecycle follows CREATED→PREPARING→VALIDATING→RUNNING→VERIFYING→COMPLETED.
    AC-029-08: Deterministic (no LLM).
    """

    def __init__(self) -> None:
        self._steps: dict[RunStatus, StepFunc] = {}
        self._runs: dict[str, HarnessRun] = {}
        self._lock = threading.Lock()

    def register_step(self, status: RunStatus, fn: StepFunc) -> None:
        self._steps[status] = fn

    def create_run(self, spec: HarnessSpec) -> HarnessRun:
        run = HarnessRun(spec_id=spec.spec_id)
        with self._lock:
            self._runs[run.run_id] = run
        return run

    def execute(self, run: HarnessRun, spec: HarnessSpec) -> HarnessRun:
        """Execute a run through its lifecycle."""
        lifecycle = [
            RunStatus.PREPARING,
            RunStatus.VALIDATING,
            RunStatus.RUNNING,
            RunStatus.VERIFYING,
            RunStatus.COMPLETED,
        ]
        for status in lifecycle:
            try:
                run.transition(status)
                step = self._steps.get(status)
                if step:
                    step(run, spec)
            except Exception as e:
                run.transition(RunStatus.FAILED)
                run.result = RunResult(passed=False, verdict="FAIL")
                return run
        if run.result is None:
            run.result = RunResult(passed=True, verdict="PASS")
        return run

    def get_run(self, run_id: str) -> HarnessRun | None:
        return self._runs.get(run_id)

    def list_runs(self) -> list[HarnessRun]:
        return list(self._runs.values())
