"""Regression runner implementation (Rule 7)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional


class RegressionError(Exception):
    """Raised for invalid runner configuration."""


@dataclass
class RegressionOutcome:
    task_id: str
    passed: bool
    detail: str = ""


@dataclass
class RegressionResult:
    blocked: bool
    failed_task: Optional[str] = None
    outcomes: List[TestOutcome] = field(default_factory=list)

    def __bool__(self) -> bool:  # True == not blocked
        return not self.blocked


class RegressionRunner:
    """Runs the test suite for a task's dependency closure.

    ``test_runner`` is a callable ``(task_id) -> TestOutcome`` supplied by the
    caller (so the runner stays decoupled from any specific test framework).
    """

    def __init__(self, test_runner: Optional[Callable[[str], TestOutcome]] = None) -> None:
        self._test_runner = test_runner

    def set_runner(self, test_runner: Callable[[str], TestOutcome]) -> None:
        self._test_runner = test_runner

    def run(
        self,
        task_id: str,
        dependency_closure: Iterable[str],
        test_runner: Optional[Callable[[str], RegressionOutcome]] = None,
    ) -> RegressionResult:
        runner = test_runner or self._test_runner
        if runner is None:
            raise RegressionError("No test runner configured for regression.")
        outcomes: List[RegressionOutcome] = []
        for dep in sorted(set(dependency_closure)):
            outcome = runner(dep)
            outcomes.append(outcome)
            if not outcome.passed:
                return RegressionResult(
                    blocked=True, failed_task=dep, outcomes=outcomes
                )
        return RegressionResult(blocked=False, outcomes=outcomes)
