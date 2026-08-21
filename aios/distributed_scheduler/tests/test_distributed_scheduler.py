"""Tests for distributed scheduler."""
from __future__ import annotations
import pytest
from aios.distributed_scheduler.contracts import Lease, LeaseState
from aios.distributed_scheduler.scheduler import DistributedScheduler

class TestDistributedScheduler:
    def test_acquire_lease(self):
        sched = DistributedScheduler()
        l = sched.acquire_lease("n1", "res1")
        assert l.state == LeaseState.HELD
    def test_release_lease(self):
        sched = DistributedScheduler()
        l = sched.acquire_lease("n1", "res1")
        sched.release_lease(l.lease_id)
        assert l.state == LeaseState.RELEASED
    def test_duplicate_lease(self):
        sched = DistributedScheduler()
        sched.acquire_lease("n1", "res1")
        with pytest.raises(RuntimeError): sched.acquire_lease("n2", "res1")
    def test_check_expired(self):
        sched = DistributedScheduler()
        sched.acquire_lease("n1", "res1")
        expired = sched.check_expired()
        assert len(expired) == 1
        assert expired[0].state == LeaseState.EXPIRED
    def test_list_leases(self):
        sched = DistributedScheduler()
        sched.acquire_lease("n1", "r1"); sched.acquire_lease("n2", "r2")
        assert len(sched.list_leases()) == 2
