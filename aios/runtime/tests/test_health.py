"""Tests for the runtime health model (TASK-065 hardening)."""

from aios.runtime.health import HealthMonitor, HealthStatus, RuntimeHealth


def test_runtime_health_defaults():
    h = RuntimeHealth(component="executor")
    assert h.component == "executor"
    assert h.status == HealthStatus.HEALTHY
    assert h.last_check
    assert h.evidence_ref is None
    d = h.to_dict()
    assert d["status"] == "healthy"
    assert d["component"] == "executor"


def test_runtime_health_explicit():
    h = RuntimeHealth(
        component="db", status=HealthStatus.DEGRADED, evidence_ref="run-1"
    )
    assert h.status == HealthStatus.DEGRADED
    assert h.evidence_ref == "run-1"


def test_health_monitor_record_and_get():
    m = HealthMonitor()
    m.record("db", HealthStatus.DEGRADED, evidence_ref="run-1")
    got = m.get("db")
    assert got is not None
    assert got.status == HealthStatus.DEGRADED
    assert got.evidence_ref == "run-1"


def test_health_monitor_overall():
    m = HealthMonitor()
    assert m.overall() == HealthStatus.HEALTHY
    m.record("a", HealthStatus.HEALTHY)
    m.record("b", HealthStatus.DEGRADED)
    assert m.overall() == HealthStatus.DEGRADED
    m.record("c", HealthStatus.UNHEALTHY)
    assert m.overall() == HealthStatus.UNHEALTHY


def test_health_monitor_snapshot():
    m = HealthMonitor()
    m.record("x", HealthStatus.HEALTHY)
    assert len(m.snapshot()) == 1
