"""Automated tests for the Regression Gate (Rule 7)."""

import pytest

from aios.governance.regression import (
    RegressionError,
    RegressionOutcome,
    RegressionResult,
    RegressionRunner,
)


def test_closure_failure_blocks_task():
    """Rule 7: failure inside the dependency closure -> task BLOCKED."""

    def runner(tid):
        return RegressionOutcome(tid, passed=(tid != "TASK-001"))

    reg = RegressionRunner(runner)
    result = reg.run("TASK-003", {"TASK-001", "TASK-002"})
    assert isinstance(result, RegressionResult)
    assert result.blocked is True
    assert result.failed_task == "TASK-001"


def test_closure_all_pass_not_blocked():
    def runner(tid):
        return RegressionOutcome(tid, passed=True)

    reg = RegressionRunner(runner)
    result = reg.run("TASK-003", {"TASK-001", "TASK-002"})
    assert result.blocked is False
    assert result.failed_task is None
    assert len(result.outcomes) == 2


def test_no_runner_configured_raises():
    reg = RegressionRunner()
    with pytest.raises(RegressionError):
        reg.run("TASK-003", {"TASK-001"})
