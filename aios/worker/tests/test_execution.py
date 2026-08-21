"""Tests for Worker execution — AC-013-02/03/04/06/07/09 (TASK-013)."""

import pytest

from aios.capability.capability import CapabilityContract, CapabilityRegistry
from aios.worker.contract import WorkerContext, WorkerContract, WorkerRequest, WorkerResult, WorkerResultStatus, WorkerType
from aios.worker.execution import BaseWorker, CapabilityAccessError, PermissionBoundaryError, WorkerExecutionError
from aios.worker.lifecycle import WorkerLifecycle, WorkerStatus


def _make_registry_with_caps(caps) -> CapabilityRegistry:
    reg = CapabilityRegistry()
    for cap in caps:
        try:
            reg.register(CapabilityContract.create(cap, description=f"cap {cap}"))
        except Exception:
            pass
    return reg


class _TestWorker(BaseWorker):
    """Minimal concrete worker for testing."""

    def _do_work(self, request, context):
        # Simple: invoke first capability in scope
        if context.capability_scope:
            cap = context.capability_scope[0]
            self.invoke_capability(cap, context, payload={"test": True})
        return WorkerResult.create(
            status=WorkerResultStatus.SUCCEEDED,
            output={"summary": "test done"},
            execution={"run_id": context.run_id, "task_id": request.task_id, "worker_id": self.worker_id},
        )


class _FailingWorker(BaseWorker):
    def _do_work(self, request, context):
        raise RuntimeError("simulated failure")


def _make_worker(caps=None, permission_checker=None, lifecycle=None, cap_registry=None) -> _TestWorker:
    contract = WorkerContract.create(
        worker_id="test-worker",
        worker_type=WorkerType.GENERAL,
        capabilities=caps or ["cap.a", "cap.b"],
        input_schema={},
        output_schema={},
        lifecycle={},
        execution_context={},
        policy_context={},
        evidence_contract={},
    )
    return _TestWorker(
        contract=contract,
        capability_registry=cap_registry or _make_registry_with_caps(caps or ["cap.a", "cap.b"]),
        permission_checker=permission_checker,
        lifecycle=lifecycle or WorkerLifecycle(),
    )


class TestCapabilityOnlyAccess:
    def test_invoke_allowed_capability(self):
        worker = _make_worker(caps=["cap.a", "cap.b"])
        ctx = WorkerContext.create(task_id="t1", worker_id="test-worker", capability_scope=["cap.a"])
        result = worker.invoke_capability("cap.a", ctx, payload={"x": 1})
        assert result["capability"] == "cap.a"
        assert result["via"] == "capability"

    def test_invoke_not_in_contract_reject(self):
        worker = _make_worker(caps=["cap.a"])
        ctx = WorkerContext.create(task_id="t1", worker_id="test-worker", capability_scope=["cap.a", "cap.b"])
        with pytest.raises(CapabilityAccessError):
            worker.invoke_capability("cap.b", ctx)

    def test_invoke_not_in_scope_reject(self):
        worker = _make_worker(caps=["cap.a", "cap.b"])
        ctx = WorkerContext.create(task_id="t1", worker_id="test-worker", capability_scope=["cap.a"])
        with pytest.raises(CapabilityAccessError):
            worker.invoke_capability("cap.b", ctx)

    def test_invoke_not_in_scope_isolation(self):
        # Worker cannot self-expand scope
        worker = _make_worker(caps=["cap.a", "cap.b"])
        ctx = WorkerContext.create(task_id="t1", worker_id="test-worker", capability_scope=["cap.a"])
        # cap.b is in contract but not in scope — must fail
        with pytest.raises(CapabilityAccessError, match="not in execution scope"):
            worker.invoke_capability("cap.b", ctx)

    def test_invoke_empty_capability_reject(self):
        worker = _make_worker()
        ctx = WorkerContext.create(task_id="t1", worker_id="test-worker", capability_scope=["cap.a"])
        with pytest.raises(CapabilityAccessError):
            worker.invoke_capability("", ctx)

    def test_invoke_invalid_context_reject(self):
        worker = _make_worker()
        with pytest.raises(CapabilityAccessError):
            worker.invoke_capability("cap.a", "not-a-context")  # type: ignore


class TestPermissionBoundary:
    def test_permission_denied_blocked(self):
        worker = _make_worker(caps=["cap.a"], permission_checker=lambda wid, cap: False)
        ctx = WorkerContext.create(task_id="t1", worker_id="test-worker", capability_scope=["cap.a"])
        with pytest.raises(PermissionBoundaryError):
            worker.invoke_capability("cap.a", ctx)

    def test_permission_allowed(self):
        worker = _make_worker(caps=["cap.a"], permission_checker=lambda wid, cap: True)
        ctx = WorkerContext.create(task_id="t1", worker_id="test-worker", capability_scope=["cap.a"])
        result = worker.invoke_capability("cap.a", ctx)
        assert result["capability"] == "cap.a"

    def test_no_checker_allows(self):
        worker = _make_worker(caps=["cap.a"], permission_checker=None)
        ctx = WorkerContext.create(task_id="t1", worker_id="test-worker", capability_scope=["cap.a"])
        result = worker.invoke_capability("cap.a", ctx)
        assert result["capability"] == "cap.a"

    def test_request_permission_no_checker_denied(self):
        worker = _make_worker(permission_checker=None)
        assert worker.request_permission("cap.a") is False

    def test_request_permission_checker_denied(self):
        worker = _make_worker(permission_checker=lambda wid, cap: False)
        assert worker.request_permission("cap.a") is False

    def test_request_permission_checker_allowed(self):
        worker = _make_worker(permission_checker=lambda wid, cap: True)
        assert worker.request_permission("cap.a") is True

    def test_worker_cannot_self_grant(self):
        # Worker has no method to grant itself permission — only request
        worker = _make_worker(permission_checker=lambda wid, cap: False)
        # Even if worker tries to invoke, it gets BLOCKED
        ctx = WorkerContext.create(task_id="t1", worker_id="test-worker", capability_scope=["cap.a"])
        with pytest.raises(PermissionBoundaryError):
            worker.invoke_capability("cap.a", ctx)
        # request_permission returns False, not True
        assert worker.request_permission("cap.a") is False


class TestWorkerExecution:
    def test_execute_succeeded(self):
        worker = _make_worker(caps=["cap.a"])
        req = WorkerRequest.create(task_id="task-001", objective={"description": "do work"}, allowed_capabilities=["cap.a"])
        result = worker.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert result.output["summary"] == "test done"
        assert "run_id" in result.execution
        assert "duration_ms" in result.metrics

    def test_execute_with_context(self):
        worker = _make_worker(caps=["cap.a"])
        req = WorkerRequest.create(task_id="task-001", objective={"description": "do work"}, allowed_capabilities=["cap.a"])
        ctx = WorkerContext.create(task_id="task-001", worker_id="test-worker", capability_scope=["cap.a"])
        result = worker.execute(req, context=ctx)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert result.execution["run_id"] == ctx.run_id

    def test_execute_context_scope_not_in_contract_reject(self):
        worker = _make_worker(caps=["cap.a"])
        req = WorkerRequest.create(task_id="task-001", objective={}, allowed_capabilities=["cap.a"])
        ctx = WorkerContext.create(task_id="task-001", worker_id="test-worker", capability_scope=["cap.b"])
        result = worker.execute(req, context=ctx)
        # Should fail because cap.b not in contract
        assert result.status == WorkerResultStatus.FAILED

    def test_execute_failure_propagated(self):
        contract = WorkerContract.create(
            worker_id="failing-worker", worker_type=WorkerType.GENERAL,
            capabilities=["cap.a"], input_schema={}, output_schema={}, lifecycle={}, execution_context={}, policy_context={}, evidence_contract={},
        )
        worker = _FailingWorker(contract=contract, capability_registry=_make_registry_with_caps(["cap.a"]))
        req = WorkerRequest.create(task_id="task-001", objective={}, allowed_capabilities=["cap.a"])
        result = worker.execute(req)
        assert result.status == WorkerResultStatus.FAILED
        assert "simulated failure" in result.error

    def test_execute_permission_denied_blocked(self):
        worker = _make_worker(caps=["cap.a"], permission_checker=lambda wid, cap: False)
        # Override _do_work to try invoke
        class PermWorker(BaseWorker):
            def _do_work(self, request, context):
                self.invoke_capability("cap.a", context)
                return WorkerResult.create(status=WorkerResultStatus.SUCCEEDED, output={"summary": "ok"}, execution={"run_id": context.run_id, "task_id": request.task_id, "worker_id": self.worker_id})
        contract = WorkerContract.create(worker_id="perm-worker", worker_type=WorkerType.GENERAL, capabilities=["cap.a"], input_schema={}, output_schema={}, lifecycle={}, execution_context={}, policy_context={}, evidence_contract={})
        pw = PermWorker(contract=contract, capability_registry=_make_registry_with_caps(["cap.a"]), permission_checker=lambda wid, cap: False)
        req = WorkerRequest.create(task_id="task-001", objective={}, allowed_capabilities=["cap.a"])
        result = pw.execute(req)
        assert result.status == WorkerResultStatus.BLOCKED

    def test_execute_lifecycle_transitions(self):
        lc = WorkerLifecycle()
        worker = _make_worker(caps=["cap.a"], lifecycle=lc)
        req = WorkerRequest.create(task_id="task-001", objective={}, allowed_capabilities=["cap.a"])
        result = worker.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert lc.current_status("test-worker") == WorkerStatus.COMPLETED

    def test_execute_reuse_after_completed(self):
        lc = WorkerLifecycle()
        worker = _make_worker(caps=["cap.a"], lifecycle=lc)
        req = WorkerRequest.create(task_id="task-001", objective={}, allowed_capabilities=["cap.a"])
        result1 = worker.execute(req)
        assert result1.status == WorkerResultStatus.SUCCEEDED
        # Second execution should reuse worker (COMPLETED -> READY)
        req2 = WorkerRequest.create(task_id="task-002", objective={}, allowed_capabilities=["cap.a"])
        result2 = worker.execute(req2)
        assert result2.status == WorkerResultStatus.SUCCEEDED

    def test_execute_reuse_after_failed(self):
        lc = WorkerLifecycle()
        contract = WorkerContract.create(
            worker_id="reuse-worker", worker_type=WorkerType.GENERAL,
            capabilities=["cap.a"], input_schema={}, output_schema={}, lifecycle={}, execution_context={}, policy_context={}, evidence_contract={},
        )
        call_count = [0]
        class FlakyWorker(BaseWorker):
            def _do_work(self, request, context):
                call_count[0] += 1
                if call_count[0] == 1:
                    raise RuntimeError("first fail")
                return WorkerResult.create(status=WorkerResultStatus.SUCCEEDED, output={"summary": "recovered"}, execution={"run_id": context.run_id, "task_id": request.task_id, "worker_id": self.worker_id})
        worker = FlakyWorker(contract=contract, capability_registry=_make_registry_with_caps(["cap.a"]), lifecycle=lc)
        req1 = WorkerRequest.create(task_id="task-001", objective={}, allowed_capabilities=["cap.a"])
        result1 = worker.execute(req1)
        assert result1.status == WorkerResultStatus.FAILED
        # Worker should be recoverable
        req2 = WorkerRequest.create(task_id="task-002", objective={}, allowed_capabilities=["cap.a"])
        result2 = worker.execute(req2)
        assert result2.status == WorkerResultStatus.SUCCEEDED

    def test_execute_invalid_request_reject(self):
        worker = _make_worker()
        with pytest.raises(WorkerExecutionError):
            worker.execute("not-a-request")  # type: ignore

    def test_execute_invalid_context_reject(self):
        worker = _make_worker()
        req = WorkerRequest.create(task_id="task-001", objective={}, allowed_capabilities=["cap.a"])
        with pytest.raises(WorkerExecutionError):
            worker.execute(req, context="bad")  # type: ignore

    def test_create_evidence(self):
        worker = _make_worker()
        ev = worker.create_evidence(task_id="t1", run_id="r1", content="hello", evidence_type="result")
        assert ev.task_id == "t1"
        assert ev.run_id == "r1"
        assert ev.producer == "test-worker"
        assert ev.is_admissible is True

    def test_health(self):
        worker = _make_worker()
        assert worker.health() in ["READY", "REGISTERED", "BUSY", "DEGRADED", "UNAVAILABLE", "UNKNOWN"]

    def test_worker_does_not_import_runtime(self):
        # Verify worker module doesn't import runtime internals
        import ast
        import pathlib
        worker_dir = pathlib.Path(__file__).resolve().parents[1]
        for py in worker_dir.glob("*.py"):
            if "tests" in py.parts:
                continue
            text = py.read_text(encoding="utf-8")
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert "aios.runtime" not in alias.name, f"{py.name} imports {alias.name}"
                        assert "aios.orchestrator" not in alias.name, f"{py.name} imports {alias.name}"
                        assert alias.name not in ("subprocess", "os"), f"{py.name} imports {alias.name}"
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        assert "aios.runtime" not in node.module, f"{py.name} imports {node.module}"
                        assert "aios.orchestrator" not in node.module, f"{py.name} imports {node.module}"
                        assert node.module not in ("subprocess", "os"), f"{py.name} imports {node.module}"
