"""Tests for the FastAPI bridge of AIOS Dashboard 1.0 (TASK-072)."""

from __future__ import annotations

from aios.core.healthcheck import HealthCheck
from aios.dashboard.api_bridge import create_dashboard_router
from aios.dashboard.observability_views import ObservabilityDashboard
from aios.security.auth import AuthValidator, TokenRecord


def _dashboard() -> ObservabilityDashboard:
    av = AuthValidator()
    av.register_token("good", TokenRecord(subject="tester", scopes=["dashboard:read"]))
    hc = HealthCheck()
    hc.register("db", lambda: None)
    return ObservabilityDashboard(auth_validator=av, health_check=hc)


def _client(dashboard: ObservabilityDashboard):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(create_dashboard_router(dashboard))
    return TestClient(app)


class TestDashboardRouter:
    def test_unauthenticated_blocked(self) -> None:
        client = _client(_dashboard())
        resp = client.get("/dashboard/health")
        assert resp.status_code == 401

    def test_authenticated_view(self) -> None:
        client = _client(_dashboard())
        resp = client.get("/dashboard/health", headers={"X-API-Key": "good"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["view"] == "health"
        assert body["read_only"] is True

    def test_bearer_token_accepted(self) -> None:
        client = _client(_dashboard())
        resp = client.get("/dashboard/health", headers={"Authorization": "Bearer good"})
        assert resp.status_code == 200

    def test_unknown_view_404(self) -> None:
        client = _client(_dashboard())
        resp = client.get("/dashboard/bogus", headers={"X-API-Key": "good"})
        assert resp.status_code == 404

    def test_list_views(self) -> None:
        client = _client(_dashboard())
        resp = client.get("/dashboard")
        assert resp.status_code == 200
        assert set(resp.json()["views"]) == {
            "health",
            "goals",
            "autonomy",
            "evidence",
            "alerts",
        }
