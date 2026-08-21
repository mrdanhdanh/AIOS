"""Tests for harness contracts and kernel."""

from __future__ import annotations

import pytest

from aios.harness.contracts import Assertion, HarnessError, HarnessRun, HarnessSpec, RunResult, RunStatus
from aios.harness.kernel import HarnessKernel


class TestHarnessContracts:
    def test_run_status_values(self) -> None:
        assert len(RunStatus) == 8

    def test_assertion(self) -> None:
        a = Assertion(name="test", passed=True, detail="ok")
        d = a.to_dict()
        assert d["passed"] is True

    def test_spec(self) -> None:
        spec = HarnessSpec(spec_id="s1", name="test")
        assert spec.content_hash
        assert spec.to_dict()["spec_id"] == "s1"

    def test_run_lifecycle(self) -> None:
        run = HarnessRun()
        assert run.status == RunStatus.CREATED
        run.transition(RunStatus.PREPARING)
        assert run.status == RunStatus.PREPARING

    def test_run_invalid_transition(self) -> None:
        run = HarnessRun()
        with pytest.raises(HarnessError):
            run.transition(RunStatus.COMPLETED)

    def test_run_result(self) -> None:
        r = RunResult(passed=True, verdict="PASS")
        d = r.to_dict()
        assert d["verdict"] == "PASS"


class TestHarnessKernel:
    def test_create_run(self) -> None:
        kernel = HarnessKernel()
        spec = HarnessSpec(spec_id="s1", name="test")
        run = kernel.create_run(spec)
        assert run.status == RunStatus.CREATED

    def test_execute_full_lifecycle(self) -> None:
        kernel = HarnessKernel()
        spec = HarnessSpec(spec_id="s1", name="test")
        run = kernel.create_run(spec)
        result = kernel.execute(run, spec)
        assert result.status == RunStatus.COMPLETED
        assert result.result is not None
        assert result.result.passed

    def test_execute_with_step(self) -> None:
        kernel = HarnessKernel()
        def prepare(run: HarnessRun, spec: HarnessSpec) -> None:
            pass
        kernel.register_step(RunStatus.PREPARING, prepare)
        spec = HarnessSpec(spec_id="s1", name="test")
        run = kernel.create_run(spec)
        result = kernel.execute(run, spec)
        assert result.status == RunStatus.COMPLETED

    def test_execute_failure(self) -> None:
        kernel = HarnessKernel()
        def fail_step(run: HarnessRun, spec: HarnessSpec) -> None:
            raise RuntimeError("boom")
        kernel.register_step(RunStatus.RUNNING, fail_step)
        spec = HarnessSpec(spec_id="s1", name="test")
        run = kernel.create_run(spec)
        result = kernel.execute(run, spec)
        assert result.status == RunStatus.FAILED

    def test_list_runs(self) -> None:
        kernel = HarnessKernel()
        spec = HarnessSpec(spec_id="s1", name="test")
        kernel.create_run(spec)
        kernel.create_run(spec)
        assert len(kernel.list_runs()) == 2
