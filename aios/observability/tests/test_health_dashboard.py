"""Tests for TASK-021 Health API and Dashboard integration (AC-021-10)."""

from __future__ import annotations

from aios.observability.dashboard import DashboardIntegration, DashboardSnapshot
from aios.observability.doctor import ComponentReport, DoctorService, HealthLevel
from aios.observability.health_api import HealthAPI, SystemHealth


def _doctor_with(level: HealthLevel) -> DoctorService:
    doc = DoctorService()
    doc.register(
        "runtime",
        lambda: ComponentReport(name="runtime", level=level),
    )
    return doc


def test_health_api_aggregates_doctor_and_arch() -> None:
    api = HealthAPI(doctor=_doctor_with(HealthLevel.PASS))
    health = api.get_health()
    assert isinstance(health, SystemHealth)
    assert health.doctor is not None
    assert health.architecture is not None


def test_health_api_fail_closed_on_error() -> None:
    api = HealthAPI(doctor=_doctor_with(HealthLevel.ERROR))
    assert api.get_health().overall == HealthLevel.ERROR
    assert api.is_healthy() is False


def test_health_api_unknown_is_not_healthy() -> None:
    api = HealthAPI(doctor=_doctor_with(HealthLevel.UNKNOWN))
    assert api.get_health().overall == HealthLevel.UNKNOWN
    assert api.is_healthy() is False


def test_dashboard_snapshot_is_read_only_projection() -> None:
    api = HealthAPI(doctor=_doctor_with(HealthLevel.PASS))
    dash = DashboardIntegration(health_api=api)
    snap = dash.snapshot()
    assert isinstance(snap, DashboardSnapshot)
    assert snap.health["overall"] == "pass"
    assert "metrics" in snap.to_dict()
