"""Tests for dashboard health status normalization."""

from __future__ import annotations

import pytest

from aios.dashboard.health import ComponentHealth, HealthChecker, HealthStatus


class TestHealthStatus:
    """Test HealthStatus enum."""

    def test_pass_is_healthy(self) -> None:
        assert HealthStatus.PASS.is_healthy() is True

    def test_warning_not_healthy(self) -> None:
        assert HealthStatus.WARNING.is_healthy() is False

    def test_error_not_healthy(self) -> None:
        assert HealthStatus.ERROR.is_healthy() is False

    def test_unknown_not_healthy(self) -> None:
        # AC-018-09: UNKNOWN is NOT healthy
        assert HealthStatus.UNKNOWN.is_healthy() is False


class TestHealthChecker:
    """Test HealthChecker normalization."""

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("ok", HealthStatus.PASS),
            ("healthy", HealthStatus.PASS),
            ("PASS", HealthStatus.PASS),
            ("up", HealthStatus.PASS),
            ("active", HealthStatus.PASS),
            ("warning", HealthStatus.WARNING),
            ("degraded", HealthStatus.WARNING),
            ("error", HealthStatus.ERROR),
            ("failed", HealthStatus.ERROR),
            ("down", HealthStatus.ERROR),
            ("unknown", HealthStatus.UNKNOWN),
            ("unchecked", HealthStatus.UNKNOWN),
            ("bogus_value", HealthStatus.UNKNOWN),
        ],
    )
    def test_normalize_status(self, raw: str, expected: HealthStatus) -> None:
        assert HealthChecker.normalize_status(raw) == expected

    def test_normalize_case_insensitive(self) -> None:
        assert HealthChecker.normalize_status("OK") == HealthStatus.PASS
        assert HealthChecker.normalize_status("Error") == HealthStatus.ERROR

    def test_normalize_strips_whitespace(self) -> None:
        assert HealthChecker.normalize_status("  ok  ") == HealthStatus.PASS

    def test_check_component(self) -> None:
        comp = HealthChecker.check_component("runtime", "healthy")
        assert comp.name == "runtime"
        assert comp.status == HealthStatus.PASS
        assert comp.is_healthy is True

    def test_check_all_components(self) -> None:
        health_data = {
            "runtime": "healthy",
            "orchestrator": "healthy",
            "database": "error",
            "model": "unknown",
            "memory": "healthy",
            "workflow": "healthy",
            "capability": "healthy",
            "tool": "healthy",
            "skill": "healthy",
        }
        components = HealthChecker.check_all(health_data)
        assert len(components) == 9

    def test_check_all_missing_component_gets_unknown(self) -> None:
        components = HealthChecker.check_all({})
        assert all(c.status == HealthStatus.UNKNOWN for c in components)

    def test_overall_status_all_pass(self) -> None:
        components = [
            ComponentHealth("a", HealthStatus.PASS),
            ComponentHealth("b", HealthStatus.PASS),
        ]
        assert HealthChecker.overall_status(components) == HealthStatus.PASS

    def test_overall_status_any_error(self) -> None:
        components = [
            ComponentHealth("a", HealthStatus.PASS),
            ComponentHealth("b", HealthStatus.ERROR),
        ]
        assert HealthChecker.overall_status(components) == HealthStatus.ERROR

    def test_overall_status_warning(self) -> None:
        components = [
            ComponentHealth("a", HealthStatus.PASS),
            ComponentHealth("b", HealthStatus.WARNING),
        ]
        assert HealthChecker.overall_status(components) == HealthStatus.WARNING

    def test_overall_status_unknown(self) -> None:
        components = [
            ComponentHealth("a", HealthStatus.PASS),
            ComponentHealth("b", HealthStatus.UNKNOWN),
        ]
        assert HealthChecker.overall_status(components) == HealthStatus.UNKNOWN

    def test_healthy_count(self) -> None:
        components = [
            ComponentHealth("a", HealthStatus.PASS),
            ComponentHealth("b", HealthStatus.ERROR),
            ComponentHealth("c", HealthStatus.PASS),
        ]
        assert HealthChecker.healthy_count(components) == 2

    def test_unhealthy_components(self) -> None:
        components = [
            ComponentHealth("a", HealthStatus.PASS),
            ComponentHealth("b", HealthStatus.ERROR),
            ComponentHealth("c", HealthStatus.UNKNOWN),
        ]
        unhealthy = HealthChecker.unhealthy_components(components)
        assert len(unhealthy) == 2
        assert unhealthy[0].name == "b"
        assert unhealthy[1].name == "c"

    def test_component_health_to_dict(self) -> None:
        comp = ComponentHealth("runtime", HealthStatus.PASS, "all good", 1.5)
        d = comp.to_dict()
        assert d["name"] == "runtime"
        assert d["status"] == "pass"
        assert d["is_healthy"] is True
        assert d["latency_ms"] == 1.5

