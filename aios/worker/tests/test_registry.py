"""Tests for Worker Registry — AC-013-01/05/08 (TASK-013)."""

import threading

import pytest

from aios.worker.contract import WorkerContract, WorkerType
from aios.worker.lifecycle import WorkerHealth, WorkerStatus
from aios.worker.registry import WorkerRegistry, WorkerRegistryError


def _make_contract(worker_id: str, worker_type: str = "general", caps=None) -> WorkerContract:
    return WorkerContract.create(
        worker_id=worker_id,
        worker_type=worker_type,
        capabilities=caps or ["cap.a"],
        input_schema={},
        output_schema={},
        lifecycle={},
        execution_context={},
        policy_context={},
        evidence_contract={},
    )


class TestWorkerRegistry:
    def test_register_and_get(self):
        reg = WorkerRegistry()
        c = _make_contract("general-worker", "general", ["research", "summarize"])
        rw = reg.register(c)
        assert rw.contract.worker_id == "general-worker"
        assert reg.get("general-worker").contract.worker_id == "general-worker"
        assert reg.get_contract("general-worker").worker_id == "general-worker"

    def test_duplicate_reject(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1"))
        with pytest.raises(WorkerRegistryError):
            reg.register(_make_contract("w1"))

    def test_unknown_reject(self):
        reg = WorkerRegistry()
        with pytest.raises(WorkerRegistryError):
            reg.get("unknown")
        with pytest.raises(WorkerRegistryError):
            reg.remove("unknown")

    def test_non_contract_reject(self):
        reg = WorkerRegistry()
        with pytest.raises(WorkerRegistryError):
            reg.register("not-a-contract")  # type: ignore

    def test_list(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1", "general"))
        reg.register(_make_contract("w2", "coder"))
        assert len(reg.list()) == 2
        assert len(reg) == 2
        assert "w1" in reg
        assert "w2" in reg
        assert "w3" not in reg

    def test_list_sorted(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w-b"))
        reg.register(_make_contract("w-a"))
        lst = reg.list()
        assert lst[0].contract.worker_id == "w-a"
        assert lst[1].contract.worker_id == "w-b"

    def test_list_by_type(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("g1", "general"))
        reg.register(_make_contract("c1", "coder"))
        reg.register(_make_contract("g2", "general"))
        assert len(reg.list_by_type("general")) == 2
        assert len(reg.list_by_type("coder")) == 1
        assert len(reg.list_by_type("doctor")) == 0

    def test_list_by_health(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1"))
        reg.register(_make_contract("w2"))
        reg.set_health("w1", WorkerHealth.READY)
        assert len(reg.list_by_health(WorkerHealth.READY)) == 1
        assert len(reg.list_by_health("READY")) == 1

    def test_list_by_health_invalid(self):
        reg = WorkerRegistry()
        with pytest.raises(WorkerRegistryError):
            reg.list_by_health("INVALID")

    def test_remove(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1"))
        reg.remove("w1")
        assert "w1" not in reg
        with pytest.raises(WorkerRegistryError):
            reg.remove("w1")

    def test_set_health(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1"))
        reg.set_health("w1", WorkerHealth.READY)
        assert reg.get_health("w1") == WorkerHealth.READY
        reg.set_health("w1", "BUSY")
        assert reg.get_health("w1") == WorkerHealth.BUSY

    def test_set_health_invalid(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1"))
        with pytest.raises(WorkerRegistryError):
            reg.set_health("w1", "INVALID")

    def test_set_health_unknown(self):
        reg = WorkerRegistry()
        with pytest.raises(WorkerRegistryError):
            reg.set_health("unknown", WorkerHealth.READY)

    def test_is_available(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1"))
        reg.set_health("w1", WorkerHealth.READY)
        assert reg.is_available("w1") is True
        reg.set_health("w1", WorkerHealth.BUSY)
        assert reg.is_available("w1") is False
        reg.set_health("w1", WorkerHealth.UNAVAILABLE)
        assert reg.is_available("w1") is False
        reg.set_health("w1", WorkerHealth.DEGRADED)
        assert reg.is_available("w1") is False

    def test_available_workers(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1"))
        reg.register(_make_contract("w2"))
        reg.set_health("w1", WorkerHealth.READY)
        reg.set_health("w2", WorkerHealth.UNAVAILABLE)
        avail = reg.available_workers()
        assert len(avail) == 1
        assert avail[0].contract.worker_id == "w1"

    def test_set_status(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1"))
        reg.set_health("w1", WorkerHealth.READY)
        # Need to go through lifecycle: REGISTERED -> READY
        reg.lifecycle.mark_ready("w1")
        reg.set_status("w1", WorkerStatus.ASSIGNED)
        assert reg.get("w1").status == WorkerStatus.ASSIGNED

    def test_set_status_invalid(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1"))
        with pytest.raises(WorkerRegistryError):
            reg.set_status("w1", "INVALID")

    def test_clear(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1"))
        reg.clear()
        assert len(reg) == 0

    def test_to_dict(self):
        reg = WorkerRegistry()
        reg.register(_make_contract("w1", "general"))
        d = reg.to_dict()
        assert "w1" in d
        assert d["w1"]["contract"]["worker_id"] == "w1"

    def test_thread_safety(self):
        reg = WorkerRegistry()
        errors: list = []

        def worker(idx: int):
            try:
                reg.register(_make_contract(f"w-{idx}"))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []
        assert len(reg) == 20

    def test_four_workers_registered(self):
        reg = WorkerRegistry()
        for wid, wtype in [("general-worker", "general"), ("coder-worker", "coder"), ("doctor-worker", "doctor"), ("system-doctor-worker", "system_doctor")]:
            reg.register(_make_contract(wid, wtype))
        assert len(reg) == 4
        assert len(reg.list_by_type("general")) == 1
        assert len(reg.list_by_type("coder")) == 1
        assert len(reg.list_by_type("doctor")) == 1
        assert len(reg.list_by_type("system_doctor")) == 1
