"""Tests for Sandbox Pool — AC-015-07/08 (TASK-015)."""

import time

import pytest

from aios.skill.sandbox import Sandbox, SandboxError, SandboxPool, SandboxStatus


# -- Sandbox lifecycle --

def test_sandbox_create():
    sb = Sandbox.create()
    assert sb.status == SandboxStatus.CREATED
    assert sb.health == "healthy"


def test_sandbox_initialize():
    sb = Sandbox.create()
    sb.initialize()
    assert sb.status == SandboxStatus.READY
    assert sb.health == "healthy"


def test_sandbox_acquire():
    sb = Sandbox.create()
    sb.initialize()
    sb.acquire()
    assert sb.status == SandboxStatus.ACQUIRED


def test_sandbox_acquire_not_ready():
    sb = Sandbox.create()
    with pytest.raises(SandboxError):
        sb.acquire()


def test_sandbox_run():
    sb = Sandbox.create()
    sb.initialize()
    sb.acquire()
    result = sb.run(payload={"data": "test"})
    assert result["status"] == "completed"
    assert sb.status == SandboxStatus.RUNNING
    assert sb.execution_count == 1
    assert "last_payload" in sb.state


def test_sandbox_run_not_acquired():
    sb = Sandbox.create()
    sb.initialize()
    with pytest.raises(SandboxError):
        sb.run(payload="test")


def test_sandbox_reset():
    sb = Sandbox.create()
    sb.initialize()
    sb.acquire()
    sb.run(payload="test")
    sb.reset()
    assert sb.status == SandboxStatus.READY
    assert sb.state == {}
    assert sb.health == "healthy"


def test_sandbox_reset_clears_state():
    sb = Sandbox.create()
    sb.initialize()
    sb.acquire()
    sb.run(payload={"key": "value"})
    assert "last_payload" in sb.state
    sb.reset()
    assert sb.state == {}
    # Second execution should not see previous state
    sb.acquire()
    sb.run(payload={"key": "new"})
    assert sb.state["last_payload"] == {"key": "new"}


def test_sandbox_health_check():
    sb = Sandbox.create()
    sb.initialize()
    assert sb.health_check() is True
    sb.health = "unhealthy"
    assert sb.health_check() is False
    assert sb.status == SandboxStatus.FAILED


def test_sandbox_unhealthy_not_ready():
    sb = Sandbox.create()
    sb.initialize()
    sb.acquire()
    # Simulate failure
    try:
        sb.run(payload={"fail": True})
    except SandboxError:
        pass
    assert sb.status == SandboxStatus.FAILED
    assert sb.health == "unhealthy"
    # Cannot reset failed sandbox
    with pytest.raises(SandboxError):
        sb.reset()
    # Cannot acquire failed sandbox
    with pytest.raises(SandboxError):
        sb.acquire()


def test_sandbox_destroy():
    sb = Sandbox.create()
    sb.initialize()
    sb.destroy()
    assert sb.status == SandboxStatus.DESTROYED


def test_sandbox_timeout():
    sb = Sandbox.create(timeout=1.0)
    sb.initialize()
    sb.acquire()
    with pytest.raises(SandboxError, match="timeout"):
        sb.run(payload={"delay": 5})


def test_sandbox_is_idle():
    sb = Sandbox.create()
    sb.initialize()
    # Just initialized, not idle
    assert sb.is_idle(idle_timeout=300) is False
    # Simulate old idle_since
    sb.idle_since = "2020-01-01T00:00:00+00:00"
    assert sb.is_idle(idle_timeout=300) is True


# -- SandboxPool --

def test_pool_create():
    pool = SandboxPool(max_size=3)
    assert pool.size() == 0
    sb = pool.create_sandbox()
    assert pool.size() == 1
    assert sb.status == SandboxStatus.READY


def test_pool_max_size():
    pool = SandboxPool(max_size=2)
    pool.create_sandbox()
    pool.create_sandbox()
    with pytest.raises(SandboxError, match="max capacity"):
        pool.create_sandbox()


def test_pool_warm_start():
    pool = SandboxPool(max_size=5)
    created = pool.warm_start(count=3)
    assert len(created) == 3
    assert pool.size() == 3
    for sb in created:
        assert sb.status == SandboxStatus.READY


def test_pool_acquire_release():
    pool = SandboxPool(max_size=3)
    pool.warm_start(count=2)
    sb = pool.acquire()
    assert sb.status == SandboxStatus.ACQUIRED
    # Run and release
    sb.run(payload="test")
    pool.release(sb.sandbox_id)
    # Should be back to READY
    sb2 = pool.get(sb.sandbox_id)
    assert sb2.status == SandboxStatus.READY
    assert sb2.state == {}


def test_pool_acquire_creates_if_needed():
    pool = SandboxPool(max_size=3)
    sb = pool.acquire()
    assert sb.status == SandboxStatus.ACQUIRED
    assert pool.size() == 1


def test_pool_acquire_no_available():
    pool = SandboxPool(max_size=1)
    sb = pool.acquire()
    # Pool at max, no READY available
    with pytest.raises(SandboxError):
        pool.acquire()


def test_pool_release_unhealthy_destroy():
    pool = SandboxPool(max_size=3)
    sb = pool.acquire()
    # Make unhealthy
    try:
        sb.run(payload={"fail": True})
    except SandboxError:
        pass
    assert sb.status == SandboxStatus.FAILED
    pool.release(sb.sandbox_id)
    # Should be destroyed
    assert pool.size() == 0
    with pytest.raises(SandboxError):
        pool.get(sb.sandbox_id)


def test_pool_health_check_all():
    pool = SandboxPool(max_size=3)
    pool.warm_start(count=2)
    result = pool.health_check_all()
    assert len(result) == 2
    assert all(v is True for v in result.values())


def test_pool_evict_idle():
    pool = SandboxPool(max_size=3, idle_timeout=1)
    pool.warm_start(count=2)
    # Make one idle
    for sb in pool.list():
        sb.idle_since = "2020-01-01T00:00:00+00:00"
    evicted = pool.evict_idle()
    assert len(evicted) == 2
    assert pool.size() == 0


def test_pool_destroy_sandbox():
    pool = SandboxPool(max_size=3)
    sb = pool.create_sandbox()
    pool.destroy_sandbox(sb.sandbox_id)
    assert pool.size() == 0


def test_pool_get_unknown():
    pool = SandboxPool(max_size=3)
    with pytest.raises(SandboxError):
        pool.get("unknown")


def test_pool_release_unknown():
    pool = SandboxPool(max_size=3)
    with pytest.raises(SandboxError):
        pool.release("unknown")


def test_pool_available_count():
    pool = SandboxPool(max_size=5)
    pool.warm_start(count=3)
    assert pool.available_count() == 3
    sb = pool.acquire()
    assert pool.available_count() == 2


def test_pool_clear():
    pool = SandboxPool(max_size=3)
    pool.warm_start(count=2)
    pool.clear()
    assert pool.size() == 0


def test_pool_isolation_between_runs():
    """AC-015-08: execution A must not leak state to execution B."""
    pool = SandboxPool(max_size=2)
    sb = pool.acquire()
    sb.run(payload={"secret": "execution-A-data"})
    assert sb.state["last_payload"]["secret"] == "execution-A-data"
    pool.release(sb.sandbox_id)
    # Acquire again — should be reset
    sb2 = pool.acquire()
    # If same sandbox reused, state should be cleared
    # If different sandbox, also no leakage
    assert "secret" not in str(sb2.state) or sb2.state.get("last_payload", {}).get("secret") != "execution-A-data"
    # Run B
    sb2.run(payload={"data": "execution-B"})
    assert sb2.state["last_payload"]["data"] == "execution-B"
    assert "execution-A-data" not in str(sb2.state)


def test_pool_resource_constraints():
    pool = SandboxPool(max_size=3, default_resources={"cpu": 2, "memory_mb": 1024})
    sb = pool.create_sandbox(resources={"cpu": 4, "memory_mb": 2048})
    assert sb.resources["cpu"] == 4


def test_sandbox_lifecycle_full():
    """Test full lifecycle: CREATED -> INITIALIZING -> READY -> ACQUIRED -> RUNNING -> RESETTING -> READY."""
    sb = Sandbox.create()
    assert sb.status == SandboxStatus.CREATED
    sb.initialize()
    assert sb.status == SandboxStatus.READY
    sb.acquire()
    assert sb.status == SandboxStatus.ACQUIRED
    sb.run(payload="test")
    assert sb.status == SandboxStatus.RUNNING
    sb.reset()
    assert sb.status == SandboxStatus.READY
    # Second cycle
    sb.acquire()
    sb.run(payload="test2")
    sb.reset()
    assert sb.status == SandboxStatus.READY
    assert sb.execution_count == 2
