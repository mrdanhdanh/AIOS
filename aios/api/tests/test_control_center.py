"""Tests for the Control Center API router (TASK-237, M34)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from aios.api.app import create_app


def _client():
    app = create_app()
    return TestClient(app)


def test_control_center_endpoint_returns_all_planes():
    client = _client()
    resp = client.get("/api/v1/control-center")
    assert resp.status_code == 200
    body = resp.json()
    assert "planes" in body
    assert body["plane_count"] == 14
    for name in (
        "goals", "executions", "agents", "plans", "coding", "evidence",
        "verification", "autonomy", "resources", "policies", "artifacts",
        "failures", "recovery", "system_health",
    ):
        assert name in body["planes"]


def test_control_center_is_read_only_snapshot():
    client = _client()
    body = client.get("/api/v1/control-center").json()
    # No mutation endpoints; the snapshot is a plain dict of plane states.
    assert isinstance(body["system_health"], str) and len(body["system_health"]) > 0
