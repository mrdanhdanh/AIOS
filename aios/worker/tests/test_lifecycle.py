"""Tests for Worker lifecycle — AC-013-05 (TASK-013)."""

import threading

import pytest

from aios.worker.lifecycle import WorkerHealth, WorkerLifecycle, WorkerLifecycleError, WorkerStatus


class TestWorkerStatus:
    def test_register_and_initial_state(self):
        lc = WorkerLifecycle()
        state = lc.register("worker-001")
        assert state.status == WorkerStatus.REGISTERED
        assert state.health == WorkerHealth.REGISTERED
        assert lc.current_status("worker-001") == WorkerStatus.REGISTERED

    def test_duplicate_register_reject(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        with pytest.raises(WorkerLifecycleError):
            lc.register("w1")

    def test_unknown_worker_reject(self):
        lc = WorkerLifecycle()
        with pytest.raises(WorkerLifecycleError):
            lc.get("unknown")
        with pytest.raises(WorkerLifecycleError):
            lc.current_status("unknown")

    def test_invalid_worker_id_reject(self):
        lc = WorkerLifecycle()
        with pytest.raises(WorkerLifecycleError):
            lc.register("")


class TestWorkerLifecycleTransitions:
    def test_happy_path(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        lc.mark_ready("w1")
        assert lc.current_status("w1") == WorkerStatus.READY
        lc.assign("w1")
        assert lc.current_status("w1") == WorkerStatus.ASSIGNED
        lc.start("w1")
        assert lc.current_status("w1") == WorkerStatus.RUNNING
        lc.completing("w1")
        assert lc.current_status("w1") == WorkerStatus.COMPLETING
        lc.complete("w1")
        assert lc.current_status("w1") == WorkerStatus.COMPLETED
        assert lc.is_terminal("w1") is True

    def test_failure_path(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        lc.mark_ready("w1")
        lc.assign("w1")
        lc.start("w1")
        lc.fail("w1")
        assert lc.current_status("w1") == WorkerStatus.FAILED
        lc.recovering("w1")
        assert lc.current_status("w1") == WorkerStatus.RECOVERING
        lc.recover_to_ready("w1")
        assert lc.current_status("w1") == WorkerStatus.READY

    def test_failure_to_failed(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        lc.mark_ready("w1")
        lc.assign("w1")
        lc.start("w1")
        lc.fail("w1")
        lc.recovering("w1")
        lc.recover_to_failed("w1")
        assert lc.current_status("w1") == WorkerStatus.FAILED

    def test_cancel_from_various_states(self):
        for start_state in [WorkerStatus.REGISTERED, WorkerStatus.READY, WorkerStatus.ASSIGNED, WorkerStatus.RUNNING]:
            lc = WorkerLifecycle()
            lc.register("w1")
            if start_state != WorkerStatus.REGISTERED:
                # Transition to start_state
                if start_state == WorkerStatus.READY:
                    lc.mark_ready("w1")
                elif start_state == WorkerStatus.ASSIGNED:
                    lc.mark_ready("w1")
                    lc.assign("w1")
                elif start_state == WorkerStatus.RUNNING:
                    lc.mark_ready("w1")
                    lc.assign("w1")
                    lc.start("w1")
            lc.cancel("w1")
            assert lc.current_status("w1") == WorkerStatus.CANCELLED
            assert lc.is_terminal("w1") is True

    def test_invalid_transition_reject(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        # REGISTERED -> RUNNING invalid
        with pytest.raises(WorkerLifecycleError):
            lc.start("w1")
        # REGISTERED -> COMPLETED invalid
        with pytest.raises(WorkerLifecycleError):
            lc.complete("w1")

    def test_terminal_no_further_transition(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        lc.mark_ready("w1")
        lc.assign("w1")
        lc.start("w1")
        lc.completing("w1")
        lc.complete("w1")
        with pytest.raises(WorkerLifecycleError):
            lc.assign("w1")
        with pytest.raises(WorkerLifecycleError):
            lc.start("w1")

    def test_cancelled_terminal(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        lc.cancel("w1")
        assert lc.is_terminal("w1") is True
        with pytest.raises(WorkerLifecycleError):
            lc.mark_ready("w1")

    def test_can_transition(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        assert lc.can_transition("w1", WorkerStatus.READY) is True
        assert lc.can_transition("w1", WorkerStatus.RUNNING) is False
        assert lc.can_transition("unknown", WorkerStatus.READY) is False

    def test_health_tracking(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        assert lc.current_health("w1") == WorkerHealth.REGISTERED
        lc.mark_ready("w1")
        assert lc.current_health("w1") == WorkerHealth.READY
        lc.assign("w1")
        assert lc.current_health("w1") == WorkerHealth.BUSY
        lc.start("w1")
        assert lc.current_health("w1") == WorkerHealth.BUSY
        lc.fail("w1")
        assert lc.current_health("w1") == WorkerHealth.DEGRADED

    def test_set_health(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        lc.mark_ready("w1")
        lc.set_health("w1", WorkerHealth.DEGRADED)
        assert lc.current_health("w1") == WorkerHealth.DEGRADED
        lc.set_health("w1", "UNAVAILABLE")
        assert lc.current_health("w1") == WorkerHealth.UNAVAILABLE

    def test_set_health_invalid(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        with pytest.raises(WorkerLifecycleError):
            lc.set_health("w1", "INVALID")

    def test_worker_lifecycle_not_mixed_with_task(self):
        # Worker can be READY even after task failure
        lc = WorkerLifecycle()
        lc.register("w1")
        lc.mark_ready("w1")
        lc.assign("w1")
        lc.start("w1")
        lc.fail("w1")
        # Worker is FAILED, but after recovery it is READY again
        lc.recovering("w1")
        lc.recover_to_ready("w1")
        assert lc.current_status("w1") == WorkerStatus.READY
        # Worker READY to receive next task even though previous task failed

    def test_list_and_clear(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        lc.register("w2")
        assert len(lc.list_all()) == 2
        lc.clear()
        assert len(lc.list_all()) == 0

    def test_remove(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        lc.remove("w1")
        with pytest.raises(WorkerLifecycleError):
            lc.get("w1")
        with pytest.raises(WorkerLifecycleError):
            lc.remove("w1")

    def test_to_dict(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        lc.mark_ready("w1")
        d = lc.to_dict()
        assert "w1" in d
        assert d["w1"]["status"] == "READY"

    def test_thread_safety(self):
        lc = WorkerLifecycle()
        errors: list = []

        def worker(idx: int):
            try:
                lc.register(f"w-{idx}")
                lc.mark_ready(f"w-{idx}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []
        assert len(lc.list_all()) == 20

    def test_transition_with_string(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        lc.transition("w1", "READY")
        assert lc.current_status("w1") == WorkerStatus.READY

    def test_transition_invalid_string(self):
        lc = WorkerLifecycle()
        lc.register("w1")
        with pytest.raises(WorkerLifecycleError):
            lc.transition("w1", "INVALID_STATUS")
