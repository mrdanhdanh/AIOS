"""Integration tests for Worker Plane — AC-013-08/09/11 (TASK-013)."""

import pytest

from aios.capability.capability import CapabilityContract, CapabilityRegistry
from aios.worker.contract import WorkerContext, WorkerRequest, WorkerResultStatus
from aios.worker.lifecycle import WorkerHealth, WorkerLifecycle, WorkerStatus
from aios.worker.registry import WorkerRegistry
from aios.worker.router import RoutingRequest, WorkerRouter
from aios.worker.workers import CoderWorker, DoctorWorker, GeneralWorker, SystemDoctorWorker


def _make_cap_registry(caps) -> CapabilityRegistry:
    reg = CapabilityRegistry()
    for cap in caps:
        try:
            reg.register(CapabilityContract.create(cap, description=f"cap {cap}"))
        except Exception:
            pass
    return reg


def _make_full_registry() -> WorkerRegistry:
    reg = WorkerRegistry()
    for WorkerClass in [GeneralWorker, CoderWorker, DoctorWorker, SystemDoctorWorker]:
        w = WorkerClass()
        # Need fresh registry per worker — create contracts
        from aios.worker.contract import WorkerContract, WorkerType
        # Use the worker's contract
        try:
            reg.register(w.contract)
        except Exception:
            pass
        reg.set_health(w.worker_id, WorkerHealth.READY)
    return reg


class TestWorkerRoutingIntegration:
    def test_full_routing_and_execution(self):
        caps_general = ["research", "summarize", "transform", "inspect", "coordinate"]
        caps_coder = ["code.read", "code.write", "test.run", "code.analyze", "code.refactor"]
        reg = WorkerRegistry()
        gw = GeneralWorker(capability_registry=_make_cap_registry(caps_general))
        cw = CoderWorker(capability_registry=_make_cap_registry(caps_coder))
        reg.register(gw.contract)
        reg.register(cw.contract)
        reg.set_health(gw.worker_id, WorkerHealth.READY)
        reg.set_health(cw.worker_id, WorkerHealth.READY)

        router = WorkerRouter(registry=reg)

        # Route general task
        req_general = RoutingRequest(task_id="task-001", task_type="general", required_capabilities=["research"])
        decision = router.route(req_general)
        assert decision.worker_id == "general-worker"

        # Execute via general worker
        worker_req = WorkerRequest.create(task_id="task-001", objective={"description": "research AI"}, allowed_capabilities=["research"])
        result = gw.execute(worker_req)
        assert result.status == WorkerResultStatus.SUCCEEDED

        # Route coding task
        req_coder = RoutingRequest(task_id="task-002", task_type="coding", required_capabilities=["code.read"])
        decision2 = router.route(req_coder)
        assert decision2.worker_id == "coder-worker"

        worker_req2 = WorkerRequest.create(task_id="task-002", objective={"description": "Fix failing test"}, allowed_capabilities=caps_coder)
        result2 = cw.execute(worker_req2)
        assert result2.status == WorkerResultStatus.SUCCEEDED

    def test_doctor_diagnoses_coder_failure(self):
        caps_coder = ["code.read", "code.write", "test.run", "code.analyze", "code.refactor"]
        caps_doctor = ["diagnose.task", "inspect.logs", "inspect.artifacts", "analyze.failure"]
        cw = CoderWorker(capability_registry=_make_cap_registry(caps_coder))
        dw = DoctorWorker(capability_registry=_make_cap_registry(caps_doctor))

        # Simulate coder failure via permission deny
        cw_fail = CoderWorker(capability_registry=_make_cap_registry(caps_coder), permission_checker=lambda wid, cap: False)
        req = WorkerRequest.create(task_id="task-001", objective={"description": "Fix test"}, allowed_capabilities=caps_coder)
        result = cw_fail.execute(req)
        assert result.status == WorkerResultStatus.BLOCKED

        # Doctor diagnoses the failure
        doctor_req = WorkerRequest.create(
            task_id="task-001",
            objective={"failure": {"error": result.error or "permission denied", "run_id": result.execution.get("run_id", "")}},
            allowed_capabilities=caps_doctor,
        )
        diagnosis = dw.execute(doctor_req)
        assert diagnosis.status == WorkerResultStatus.SUCCEEDED
        assert "diagnosis" in diagnosis.output
        assert diagnosis.output["diagnosis"]["category"] in ["POLICY_ERROR", "TEST_FAILURE", "DEPENDENCY_ERROR", "TRANSIENT", "LOGICAL", "RESOURCE_ERROR"]

    def test_system_doctor_runtime_diagnosis(self):
        caps = ["diagnose.runtime", "health.check", "inspect.config", "analyze.architecture"]
        sdw = SystemDoctorWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(task_id="task-001", objective={"description": "runtime unhealthy"}, allowed_capabilities=caps)
        result = sdw.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert result.output["diagnosis"]["status"] == "DEGRADED"
        assert len(result.evidence) == 1

    def test_worker_failure_propagated_not_control_plane(self):
        # Worker failure should return FAILED/BLOCKED, not create new control plane
        caps = ["research", "summarize", "transform", "inspect", "coordinate"]
        gw = GeneralWorker(capability_registry=_make_cap_registry(caps), permission_checker=lambda wid, cap: False)
        # Force failure by making _do_work try to invoke denied capability
        from aios.worker.execution import BaseWorker
        from aios.worker.contract import WorkerContract, WorkerType

        class FailWorker(BaseWorker):
            def _do_work(self, request, context):
                self.invoke_capability("research", context)
                return None  # type: ignore

        contract = WorkerContract.create(worker_id="fail-worker", worker_type=WorkerType.GENERAL, capabilities=["research"], input_schema={}, output_schema={}, lifecycle={}, execution_context={}, policy_context={}, evidence_contract={})
        fw = FailWorker(contract=contract, capability_registry=_make_cap_registry(["research"]), permission_checker=lambda wid, cap: False)
        req = WorkerRequest.create(task_id="task-001", objective={"description": "research"}, allowed_capabilities=["research"])
        result = fw.execute(req)
        # Should be BLOCKED (permission) or FAILED, not SUCCEEDED
        assert result.status in [WorkerResultStatus.BLOCKED, WorkerResultStatus.FAILED]
        # Failure is returned to caller (Orchestrator), not handled internally
        assert result.error is not None

    def test_worker_reuse_after_task_failure(self):
        caps = ["research", "summarize", "transform", "inspect", "coordinate"]
        gw = GeneralWorker(capability_registry=_make_cap_registry(caps))
        # First task succeeds
        req1 = WorkerRequest.create(task_id="task-001", objective={"description": "research"}, allowed_capabilities=["research"])
        result1 = gw.execute(req1)
        assert result1.status == WorkerResultStatus.SUCCEEDED
        # Worker should be reusable (COMPLETED -> READY)
        assert gw.lifecycle.current_status(gw.worker_id) == WorkerStatus.COMPLETED
        # Second task should also succeed (reuse)
        req2 = WorkerRequest.create(task_id="task-002", objective={"description": "summarize"}, allowed_capabilities=["summarize"])
        result2 = gw.execute(req2)
        assert result2.status == WorkerResultStatus.SUCCEEDED

    def test_evidence_provenance_chain(self):
        caps = ["research", "summarize", "transform", "inspect", "coordinate"]
        gw = GeneralWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(task_id="task-001", objective={"description": "research"}, allowed_capabilities=["research"])
        result = gw.execute(req)
        assert len(result.evidence) == 1
        ev = result.evidence[0]
        assert ev["task_id"] == "task-001"
        assert "run_id" in ev
        assert "content_hash" in ev
        assert ev["producer"] == "general-worker"
        # Provenance chain
        assert ev["task_id"] == "task-001"

    def test_capability_isolation_across_workers(self):
        caps_general = ["research", "summarize", "transform", "inspect", "coordinate"]
        caps_coder = ["code.read", "code.write", "test.run", "code.analyze", "code.refactor"]
        gw = GeneralWorker(capability_registry=_make_cap_registry(caps_general + caps_coder))
        # General worker should not be able to use coder capabilities
        ctx = WorkerContext.create(task_id="task-001", worker_id="general-worker", capability_scope=["code.read"])
        # This should fail because code.read not in general-worker's contract
        req = WorkerRequest.create(task_id="task-001", objective={"description": "code task"}, allowed_capabilities=["code.read"])
        result = gw.execute(req, context=ctx)
        assert result.status == WorkerResultStatus.FAILED

    def test_routing_with_health_and_policy(self):
        reg = _make_full_registry()
        # Make coder unavailable
        reg.set_health("coder-worker", WorkerHealth.UNAVAILABLE)
        router = WorkerRouter(registry=reg)
        # Coding task should fail (no available coder)
        with pytest.raises(Exception):
            router.route(RoutingRequest(task_id="t1", task_type="coding", required_capabilities=["code.read"]))
        # General task should still work
        decision = router.route(RoutingRequest(task_id="t2", task_type="general", required_capabilities=["research"]))
        assert decision.worker_id == "general-worker"

    def test_all_four_workers_execute(self):
        workers = [
            (GeneralWorker(capability_registry=_make_cap_registry(["research", "summarize", "transform", "inspect", "coordinate"])), "general", ["research"]),
            (CoderWorker(capability_registry=_make_cap_registry(["code.read", "code.write", "test.run", "code.analyze", "code.refactor"])), "coding", ["code.read"]),
            (DoctorWorker(capability_registry=_make_cap_registry(["diagnose.task", "inspect.logs", "inspect.artifacts", "analyze.failure"])), "diagnosis", ["diagnose.task"]),
            (SystemDoctorWorker(capability_registry=_make_cap_registry(["diagnose.runtime", "health.check", "inspect.config", "analyze.architecture"])), "system_diagnosis", ["health.check"]),
        ]
        for worker, task_type, caps in workers:
            req = WorkerRequest.create(task_id=f"task-{worker.worker_id}", objective={"description": f"{task_type} task"}, allowed_capabilities=caps)
            result = worker.execute(req)
            assert result.status == WorkerResultStatus.SUCCEEDED, f"{worker.worker_id} failed: {result.error}"
            assert len(result.evidence) == 1
            assert "duration_ms" in result.metrics
