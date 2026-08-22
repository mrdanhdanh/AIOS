"""Tests for resource limit guards (TASK-065 hardening)."""

import pytest

from aios.runtime.resource import GrantStatus, ResourceExhausted, ResourceGuard, ResourcePool


def test_guard_allows_when_capacity():
    pool = ResourcePool()
    pool.register("cpu", 4)
    g = ResourceGuard(pool)
    assert g.guard("cpu", 2) is True
    assert g.utilization("cpu") == 0.0


def test_guard_degrade_safe_on_exhaustion():
    pool = ResourcePool()
    pool.register("cpu", 2)
    g = ResourceGuard(pool)
    pool.request("h", "cpu", 2)  # consume all
    assert g.is_exhausted("cpu") is True
    assert g.guard("cpu", 1) is False  # degrade safe, no raise


def test_guard_unknown_resource_refused():
    pool = ResourcePool()
    g = ResourceGuard(pool)
    assert g.guard("nope", 1) is False


def test_guard_emits_trace_on_exhaustion():
    pool = ResourcePool()
    pool.register("cpu", 1)
    pool.request("h", "cpu", 1)
    g = ResourceGuard(pool)
    assert g.guard("cpu", 1) is False
    assert len(g._obs.traces()) >= 1


def test_guard_invalid_threshold():
    pool = ResourcePool()
    with pytest.raises(Exception):
        ResourceGuard(pool, exhaustion_threshold=0)
