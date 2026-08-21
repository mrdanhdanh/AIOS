"""Tests for Worker Router — AC-013-08 (TASK-013)."""

import pytest

from aios.worker.contract import WorkerContract, WorkerType
from aios.worker.lifecycle import WorkerHealth
from aios.worker.registry import WorkerRegistry
from aios.worker.router import RoutingRequest, WorkerRouter, WorkerRouterError


def _make_registry_with_workers() -> WorkerRegistry:
    reg = WorkerRegistry()
    for wid, wtype, caps in [
        ("general-worker", "general", ["research", "summarize", "transform", "inspect", "coordinate"]),
        ("coder-worker", "coder", ["code.read", "code.write", "test.run", "code.analyze", "code.refactor"]),
        ("doctor-worker", "doctor", ["diagnose.task", "inspect.logs", "inspect.artifacts", "analyze.failure"]),
        ("system-doctor-worker", "system_doctor", ["diagnose.runtime", "health.check", "inspect.config", "analyze.architecture"]),
    ]:
        c = WorkerContract.create(
            worker_id=wid, worker_type=wtype, capabilities=caps,
            input_schema={}, output_schema={}, lifecycle={}, execution_context={}, policy_context={}, evidence_contract={},
        )
        reg.register(c)
        reg.set_health(wid, WorkerHealth.READY)
    return reg


class TestWorkerRouter:
    def test_route_general_task(self):
        reg = _make_registry_with_workers()
        router = WorkerRouter(registry=reg)
        req = RoutingRequest(task_id="task-001", task_type="general", required_capabilities=["research"])
        decision = router.route(req)
        assert decision.worker_type == "general"
        assert decision.worker_id == "general-worker"

    def test_route_coding_task(self):
        reg = _make_registry_with_workers()
        router = WorkerRouter(registry=reg)
        req = RoutingRequest(task_id="task-001", task_type="coding", required_capabilities=["code.read"])
        decision = router.route(req)
        assert decision.worker_type == "coder"
        assert decision.worker_id == "coder-worker"

    def test_route_diagnosis_task(self):
        reg = _make_registry_with_workers()
        router = WorkerRouter(registry=reg)
        req = RoutingRequest(task_id="task-001", task_type="diagnosis", required_capabilities=["diagnose.task"])
        decision = router.route(req)
        assert decision.worker_type == "doctor"

    def test_route_system_diagnosis_task(self):
        reg = _make_registry_with_workers()
        router = WorkerRouter(registry=reg)
        req = RoutingRequest(task_id="task-001", task_type="system_diagnosis", required_capabilities=["health.check"])
        decision = router.route(req)
        assert decision.worker_type == "system_doctor"

    def test_route_by_capability_not_name(self):
        reg = _make_registry_with_workers()
        router = WorkerRouter(registry=reg)
        # Route based on capability, not worker name
        req = RoutingRequest(task_id="task-001", task_type="coding", required_capabilities=["code.write"])
        decision = router.route(req)
        assert decision.worker_id == "coder-worker"
        # Even if we ask for general type but need coder capability, it should fallback
        req2 = RoutingRequest(task_id="task-002", task_type="general", required_capabilities=["code.write"])
        decision2 = router.route(req2)
        # Should fallback to coder since general doesn't have code.write
        assert decision2.worker_id == "coder-worker"
        assert decision2.is_fallback is True

    def test_route_unhealthy_worker_skipped(self):
        reg = _make_registry_with_workers()
        reg.set_health("coder-worker", WorkerHealth.UNAVAILABLE)
        router = WorkerRouter(registry=reg)
        req = RoutingRequest(task_id="task-001", task_type="coding", required_capabilities=["code.read"])
        # Coder is unavailable, should fallback or fail
        # Since no other worker has code.read, it should fail
        with pytest.raises(WorkerRouterError):
            router.route(req)

    def test_route_degraded_skipped(self):
        reg = _make_registry_with_workers()
        reg.set_health("general-worker", WorkerHealth.DEGRADED)
        router = WorkerRouter(registry=reg)
        req = RoutingRequest(task_id="task-001", task_type="general", required_capabilities=["research"])
        with pytest.raises(WorkerRouterError):
            router.route(req)

    def test_route_preferred_worker(self):
        reg = _make_registry_with_workers()
        router = WorkerRouter(registry=reg)
        req = RoutingRequest(task_id="task-001", task_type="general", required_capabilities=["research"], preferred_worker_id="general-worker")
        decision = router.route(req)
        assert decision.worker_id == "general-worker"

    def test_route_preferred_unhealthy_fallback(self):
        reg = _make_registry_with_workers()
        reg.set_health("general-worker", WorkerHealth.UNAVAILABLE)
        router = WorkerRouter(registry=reg)
        req = RoutingRequest(task_id="task-001", task_type="general", required_capabilities=["research"], preferred_worker_id="general-worker")
        # Preferred is unhealthy, should try normal routing (which also fails since general is unavailable)
        with pytest.raises(WorkerRouterError):
            router.route(req)

    def test_route_no_matching_capability(self):
        reg = _make_registry_with_workers()
        router = WorkerRouter(registry=reg)
        req = RoutingRequest(task_id="task-001", task_type="general", required_capabilities=["nonexistent.capability"])
        with pytest.raises(WorkerRouterError):
            router.route(req)

    def test_route_policy_gated(self):
        reg = _make_registry_with_workers()
        # Policy denies coder-worker
        def policy_checker(task_id: str, worker_id: str) -> bool:
            return worker_id != "coder-worker"
        router = WorkerRouter(registry=reg, policy_checker=policy_checker)
        req = RoutingRequest(task_id="task-001", task_type="coding", required_capabilities=["code.read"])
        with pytest.raises(WorkerRouterError):
            router.route(req)

    def test_route_policy_allows_fallback(self):
        reg = _make_registry_with_workers()
        # Policy allows all
        router = WorkerRouter(registry=reg, policy_checker=lambda t, w: True)
        req = RoutingRequest(task_id="task-001", task_type="coding", required_capabilities=["code.read"])
        decision = router.route(req)
        assert decision.worker_id == "coder-worker"

    def test_route_empty_capabilities(self):
        reg = _make_registry_with_workers()
        router = WorkerRouter(registry=reg)
        req = RoutingRequest(task_id="task-001", task_type="general", required_capabilities=[])
        decision = router.route(req)
        assert decision.worker_type == "general"

    def test_route_task_type_aliases(self):
        reg = _make_registry_with_workers()
        router = WorkerRouter(registry=reg)
        for task_type, expected_worker_type in [
            ("research", "general"),
            ("code", "coder"),
            ("edit_code", "coder"),
            ("diagnose", "doctor"),
            ("runtime_diagnosis", "system_doctor"),
            ("health_check", "system_doctor"),
        ]:
            req = RoutingRequest(task_id=f"task-{task_type}", task_type=task_type, required_capabilities=[])
            decision = router.route(req)
            assert decision.worker_type == expected_worker_type, f"task_type {task_type!r} should route to {expected_worker_type!r}"

    def test_can_route(self):
        reg = _make_registry_with_workers()
        router = WorkerRouter(registry=reg)
        assert router.can_route(RoutingRequest(task_id="t1", task_type="general", required_capabilities=["research"])) is True
        assert router.can_route(RoutingRequest(task_id="t1", task_type="general", required_capabilities=["nonexistent"])) is False

    def test_history(self):
        reg = _make_registry_with_workers()
        router = WorkerRouter(registry=reg)
        router.route(RoutingRequest(task_id="t1", task_type="general", required_capabilities=["research"]))
        router.route(RoutingRequest(task_id="t2", task_type="coding", required_capabilities=["code.read"]))
        assert len(router.history()) == 2
        router.clear_history()
        assert len(router.history()) == 0

    def test_routing_request_validation(self):
        with pytest.raises(WorkerRouterError):
            RoutingRequest(task_id="", task_type="general").validate()
        with pytest.raises(WorkerRouterError):
            RoutingRequest(task_id="t1", task_type="").validate()
        with pytest.raises(WorkerRouterError):
            RoutingRequest(task_id="t1", task_type="general", required_capabilities=[""]).validate()

    def test_deterministic_routing(self):
        reg = WorkerRegistry()
        # Register two general workers with same capabilities
        for wid in ["general-b", "general-a"]:
            c = WorkerContract.create(worker_id=wid, worker_type="general", capabilities=["research"], input_schema={}, output_schema={}, lifecycle={}, execution_context={}, policy_context={}, evidence_contract={})
            reg.register(c)
            reg.set_health(wid, WorkerHealth.READY)
        router = WorkerRouter(registry=reg)
        req = RoutingRequest(task_id="t1", task_type="general", required_capabilities=["research"])
        d1 = router.route(req)
        d2 = router.route(req)
        # Deterministic: same worker chosen (sorted by worker_id)
        assert d1.worker_id == d2.worker_id == "general-a"
