"""Tests for :mod:`aios.core.healthcheck`."""

from __future__ import annotations

import pytest

from aios.core.config import Config
from aios.core.healthcheck import (
    HealthCheck,
    HealthResult,
    HealthStatus,
    ProbeResult,
)


class TestHealthCheck:
    """Verify probe registration and execution."""

    def test_healthy_when_no_probes(self):
        hc = HealthCheck()
        result = hc.run()
        assert result.status == HealthStatus.HEALTHY
        assert result.probes == []

    def test_healthy_when_all_probes_pass(self):
        hc = HealthCheck()
        hc.register("ok1", lambda: None)
        hc.register("ok2", lambda: None)
        result = hc.run()
        assert result.status == HealthStatus.HEALTHY
        assert len(result.probes) == 2
        assert all(p.healthy for p in result.probes)

    def test_degraded_when_probe_fails(self):
        def failing_probe():
            raise RuntimeError("db down")

        hc = HealthCheck()
        hc.register("db", failing_probe)
        result = hc.run()
        assert result.status == HealthStatus.DEGRADED
        assert len(result.probes) == 1
        assert result.probes[0].healthy is False
        assert "RuntimeError" in result.probes[0].message

    def test_mixed_probes(self):
        def ok():
            pass

        def bad():
            raise ValueError("oops")

        hc = HealthCheck()
        hc.register("ok", ok)
        hc.register("bad", bad)
        result = hc.run()
        assert result.status == HealthStatus.DEGRADED
        healthy_count = sum(1 for p in result.probes if p.healthy)
        failed_count = sum(1 for p in result.probes if not p.healthy)
        assert healthy_count == 1
        assert failed_count == 1

    def test_unregister_removes_probe(self):
        hc = HealthCheck()
        hc.register("temp", lambda: None)
        hc.unregister("temp")
        result = hc.run()
        assert result.probes == []

    def test_unregister_nonexistent_is_noop(self):
        hc = HealthCheck()
        hc.unregister("does_not_exist")  # should not raise


class TestHealthResult:
    """Verify HealthResult serialisation."""

    def test_as_dict_structure(self):
        result = HealthResult(
            status=HealthStatus.HEALTHY,
            probes=[ProbeResult(name="db", healthy=True)],
        )
        d = result.as_dict()
        assert d["status"] == "HEALTHY"
        assert len(d["probes"]) == 1
        assert d["probes"][0]["name"] == "db"
        assert d["probes"][0]["healthy"] is True


class TestHealthCheckWithConfig:
    """Verify Config injection."""

    def test_accepts_config(self):
        cfg = Config()
        hc = HealthCheck(config=cfg)
        result = hc.run()
        assert result.status == HealthStatus.HEALTHY
