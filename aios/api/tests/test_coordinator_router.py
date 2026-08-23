"""Coordinator router tests — TASK-221 (offline, TestClient)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from aios.api.app import create_app


@pytest.fixture()
def client():
    from aios.api.events import EventService
    from aios.core.events import EventBus
    from aios.runtime.kernel import RuntimeKernel
    bus = EventBus()
    kern = RuntimeKernel()
    svc = EventService(bus=bus)
    app = create_app(kernel=kern, event_service=svc)
    return TestClient(app, raise_server_exceptions=False)


class TestCoordinatorRun:
    def test_run_returns_coordination_result(self, client):
        body = {
            "task_id": "TASK-900",
            "objective": "Add order processing function",
            "scope": "orders module only",
            "deliverables": ["impl orders.py", "test orders"],
            "acceptance": ["AC1", "AC2"],
            "dependencies": [],
        }
        r = client.post("/api/v1/coordinator/run", json=body)
        assert r.status_code == 200
        d = r.json()
        assert d["task_id"] == "TASK-900"
        assert d["approved"] is True
        assert d["closed"] is True
        assert "spec.md" in d["artifacts"]
        assert "critique-1.md" in d["artifacts"]
        assert "critique-2.md" in d["artifacts"]
        assert "tasks.md" in d["artifacts"]
        step_names = [s["name"] for s in d["steps"]]
        assert step_names == ["spec", "critique-1", "critique-2", "breakdown", "review", "orchestrate"]

    def test_run_missing_objective_rejected(self, client):
        r = client.post("/api/v1/coordinator/run", json={"task_id": "TASK-901", "objective": ""})
        assert r.status_code == 422  # pydantic validation


class TestCoordinatorGet:
    def test_get_after_run(self, client):
        body = {"task_id": "TASK-902", "objective": "demo"}
        client.post("/api/v1/coordinator/run", json=body)
        r = client.get("/api/v1/coordinator/TASK-902")
        assert r.status_code == 200
        assert r.json()["task_id"] == "TASK-902"

    def test_get_unknown_404(self, client):
        r = client.get("/api/v1/coordinator/TASK-NOPE")
        assert r.status_code == 404
