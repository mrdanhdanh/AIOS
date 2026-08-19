"""Automated tests for the resource quota service (TASK-005)."""

import pytest

from aios.runtime.resource import GrantStatus, ResourceError, ResourcePool


def test_register_and_request_grants():
    pool = ResourcePool()
    pool.register("gpu", 2)
    g = pool.request("h1", "gpu", 1)
    assert g.status == GrantStatus.GRANTED
    assert pool.available("gpu") == 1


def test_request_rejects_when_full():
    pool = ResourcePool()
    pool.register("gpu", 1)
    pool.request("h1", "gpu", 1)
    g2 = pool.request("h2", "gpu", 1)
    assert g2.status == GrantStatus.REJECTED
    assert pool.waiting_count("gpu") == 0


def test_request_queues_when_full():
    pool = ResourcePool()
    pool.register("gpu", 1)
    pool.request("h1", "gpu", 1)
    g2 = pool.request("h2", "gpu", 1, queue=True)
    assert g2.status == GrantStatus.QUEUED
    assert pool.waiting_count("gpu") == 1


def test_release_promotes_waiting():
    pool = ResourcePool()
    pool.register("gpu", 1)
    g1 = pool.request("h1", "gpu", 1)
    g2 = pool.request("h2", "gpu", 1, queue=True)
    pool.release(g1.grant_id)
    # g2 should now be granted.
    assert pool.status(g2.grant_id) == GrantStatus.GRANTED
    assert pool.available("gpu") == 0


def test_request_unknown_resource_raises():
    pool = ResourcePool()
    with pytest.raises(ResourceError):
        pool.request("h", "nope", 1)


def test_negative_capacity_rejected():
    pool = ResourcePool()
    with pytest.raises(ResourceError):
        pool.register("x", -1)


def test_usage_tracking():
    pool = ResourcePool()
    pool.register("mem", 10)
    g = pool.request("h", "mem", 4)
    assert pool.usage("mem") == 4
    pool.release(g.grant_id)
    assert pool.usage("mem") == 0
