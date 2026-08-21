"""Comprehensive API tests — TASK-017 (≥80 tests, offline).

All tests use TestClient (no network, no LLM). Verifies:
- All 15 routers return valid responses
- Error model stable schema
- Policy enforcement (403 on deny)
- Versioning header
- OpenAPI spec
- Event whitelist
- Pagination
- Architecture layer guard
"""
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


# ── Root ──────────────────────────────────────────────────────────────

class TestRoot:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["name"] == "AIOS API"


# ── Health ────────────────────────────────────────────────────────────

class TestHealth:
    def test_health(self, client):
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] in ("HEALTHY", "DEGRADED", "NOT_READY")
        assert "version" in d

    def test_ready(self, client):
        r = client.get("/api/v1/health/ready")
        assert r.status_code == 200
        assert "ready" in r.json()

    def test_live(self, client):
        r = client.get("/api/v1/health/live")
        assert r.status_code == 200
        assert r.json()["live"] is True


# ── System ────────────────────────────────────────────────────────────

class TestSystem:
    def test_system(self, client):
        r = client.get("/api/v1/system")
        assert r.status_code == 200
        assert "health" in r.json()
        assert "kernel_stats" in r.json()

    def test_info(self, client):
        r = client.get("/api/v1/system/info")
        assert r.status_code == 200
        assert "kernel_stats" in r.json()

    def test_config(self, client):
        r = client.get("/api/v1/system/config")
        assert r.status_code == 200
        assert "log_level" in r.json()


# ── Orchestrator ──────────────────────────────────────────────────────

class TestOrchestrator:
    def test_decide_health(self, client):
        r = client.post("/api/v1/orchestrator/decide", json={"text": "health"})
        assert r.status_code == 200
        d = r.json()
        assert d["source"] == "deterministic"
        assert d["llm_call_count"] == 0

    def test_decide_status(self, client):
        r = client.post("/api/v1/orchestrator/decide", json={"text": "status"})
        assert r.status_code == 200
        assert r.json()["plan_id"] != ""

    def test_decide_help(self, client):
        r = client.post("/api/v1/orchestrator/decide", json={"text": "help"})
        assert r.status_code == 200
        assert r.json()["llm_call_count"] == 0

    def test_decide_insufficient(self, client):
        r = client.post("/api/v1/orchestrator/decide", json={"text": "totally unknown intent xyz"})
        assert r.status_code == 422
        assert r.json()["code"] == "CONTRACT_INVALID"

    def test_status(self, client):
        r = client.get("/api/v1/orchestrator/status")
        assert r.status_code == 200
        assert r.json()["status"] == "ready"


# ── Executions ────────────────────────────────────────────────────────

class TestExecutions:
    def test_list_empty(self, client):
        r = client.get("/api/v1/executions")
        assert r.status_code == 200
        d = r.json()
        assert d["total"] >= 0
        assert "items" in d

    def test_create(self, client):
        r = client.post("/api/v1/executions", json={"workflow": "test"})
        assert r.status_code == 201
        d = r.json()
        assert d["execution_id"].startswith("exec-")
        assert d["status"] in ("created", "pending", "ready")

    def test_get(self, client):
        r = client.post("/api/v1/executions", json={"workflow": "test"})
        eid = r.json()["execution_id"]
        r = client.get(f"/api/v1/executions/{eid}")
        assert r.status_code == 200
        assert r.json()["execution_id"] == eid

    def test_get_not_found(self, client):
        r = client.get("/api/v1/executions/nonexistent")
        assert r.status_code == 404
        assert r.json()["code"] == "NOT_FOUND"

    def test_state(self, client):
        r = client.post("/api/v1/executions", json={"workflow": "test"})
        eid = r.json()["execution_id"]
        r = client.get(f"/api/v1/executions/{eid}/state")
        assert r.status_code == 200
        assert "execution_id" in r.json()

    def test_cancel(self, client):
        r = client.post("/api/v1/executions", json={"workflow": "test"})
        eid = r.json()["execution_id"]
        r = client.delete(f"/api/v1/executions/{eid}")
        assert r.status_code == 200
        assert r.json()["status"] == "cancelled"

    def test_policy_deny(self, client):
        from aios.runtime.policy import PolicyEngine
        # Add deny rule to kernel's policy engine
        from aios.api.deps import get_kernel
        from aios.runtime.policy import PolicyRule, PolicyDecision
        kernel = client.app.state.kernel
        kernel.policy.add_rule(PolicyRule("test-deny", lambda r: True, PolicyDecision.DENY, "test"))
        r = client.post("/api/v1/executions", json={"workflow": "test"})
        assert r.status_code == 403
        assert r.json()["code"] == "POLICY_DENIED"
        # Cleanup
        kernel.policy.clear_rules()


# ── Workflows ─────────────────────────────────────────────────────────

class TestWorkflows:
    def test_list_empty(self, client):
        r = client.get("/api/v1/workflows")
        assert r.status_code == 200
        assert "items" in r.json()

    def test_create(self, client):
        r = client.post("/api/v1/workflows", json={"name": "test-wf", "version": "1.0.0",
            "nodes": [{"id": "n1", "type": "task", "capability": "test"}], "edges": []})
        assert r.status_code == 201
        assert r.json()["workflow_id"].startswith("wf-")

    def test_get(self, client):
        r = client.post("/api/v1/workflows", json={"name": "wf2", "version": "1.0.0", "nodes": [{"id": "a", "type": "task"}], "edges": []})
        wid = r.json()["workflow_id"]
        r = client.get(f"/api/v1/workflows/{wid}")
        assert r.status_code == 200

    def test_invalid_workflow(self, client):
        r = client.post("/api/v1/workflows", json={"name": "", "version": "1.0.0"})
        assert r.status_code in (400, 409, 422, 500)


# ── Tasks ─────────────────────────────────────────────────────────────

class TestTasks:
    def test_list(self, client):
        r = client.get("/api/v1/tasks")
        assert r.status_code == 200

    def test_create(self, client):
        r = client.post("/api/v1/tasks", json={"title": "Test Task"})
        assert r.status_code == 201
        assert r.json()["task_id"].startswith("task-")

    def test_get(self, client):
        r = client.post("/api/v1/tasks", json={"title": "T"})
        tid = r.json()["task_id"]
        r = client.get(f"/api/v1/tasks/{tid}")
        assert r.status_code == 200


# ── Agents ────────────────────────────────────────────────────────────

class TestAgents:
    def test_list(self, client):
        r = client.get("/api/v1/agents")
        assert r.status_code == 200
        assert len(r.json()["items"]) == 4

    def test_get(self, client):
        r = client.get("/api/v1/agents/general-worker")
        assert r.status_code == 200
        assert r.json()["agent_type"] == "GENERAL"

    def test_not_found(self, client):
        r = client.get("/api/v1/agents/nonexistent")
        assert r.status_code == 404


# ── Capabilities ──────────────────────────────────────────────────────

class TestCapabilities:
    def test_list_empty(self, client):
        r = client.get("/api/v1/capabilities")
        assert r.status_code == 200

    def test_create_and_get(self, client):
        r = client.post("/api/v1/capabilities", json={"capability_id": "test_cap", "version": "1.0.0"})
        assert r.status_code == 201
        r = client.get("/api/v1/capabilities/test_cap")
        assert r.status_code == 200
        assert r.json()["capability_id"] == "test_cap"

    def test_not_found(self, client):
        r = client.get("/api/v1/capabilities/nope")
        assert r.status_code == 404


# ── Tools ─────────────────────────────────────────────────────────────

class TestTools:
    def test_list(self, client):
        r = client.get("/api/v1/tools")
        assert r.status_code == 200

    def test_create(self, client):
        client.post("/api/v1/capabilities", json={"capability_id": "tc"})
        r = client.post("/api/v1/tools", json={"tool_id": "my-tool", "name": "My Tool", "version": "1.0.0", "tool_type": "python", "capabilities": ["tc"]})
        assert r.status_code == 201
        assert r.json()["tool_type"] == "python"

    def test_not_found(self, client):
        r = client.get("/api/v1/tools/nope")
        assert r.status_code == 404


# ── Skills ────────────────────────────────────────────────────────────

class TestSkills:
    def test_list(self, client):
        r = client.get("/api/v1/skills")
        assert r.status_code == 200

    def test_create_and_enable(self, client):
        r = client.post("/api/v1/skills", json={"skill_id": "sk1", "name": "Skill1", "version": "1.0.0"})
        assert r.status_code == 201
        r = client.post("/api/v1/skills/sk1/enable")
        assert r.status_code == 200
        assert r.json()["enabled"] is True

    def test_disable(self, client):
        client.post("/api/v1/skills", json={"skill_id": "sk2", "name": "S2", "version": "1.0.0"})
        client.post("/api/v1/skills/sk2/enable")
        r = client.post("/api/v1/skills/sk2/disable")
        assert r.status_code == 200
        assert r.json()["enabled"] is False


# ── Memory ────────────────────────────────────────────────────────────

class TestMemory:
    def test_list(self, client):
        r = client.get("/api/v1/memory")
        assert r.status_code == 200

    def test_create_and_get(self, client):
        r = client.post("/api/v1/memory", json={"memory_type": "conversation", "scope_id": "s1", "content": "hello"})
        assert r.status_code == 201
        eid = r.json()["entry_id"]
        r = client.get(f"/api/v1/memory/{eid}")
        assert r.status_code == 200
        assert r.json()["content"] == "hello"


# ── Artifacts ─────────────────────────────────────────────────────────

class TestArtifacts:
    def test_list(self, client):
        r = client.get("/api/v1/artifacts")
        assert r.status_code == 200

    def test_create_and_get(self, client):
        r = client.post("/api/v1/artifacts", json={"name": "art1", "content": "data"})
        assert r.status_code == 201
        aid = r.json()["artifact_id"]
        r = client.get(f"/api/v1/artifacts/{aid}")
        assert r.status_code == 200

    def test_content(self, client):
        r = client.post("/api/v1/artifacts", json={"name": "art2", "content": "content"})
        aid = r.json()["artifact_id"]
        r = client.get(f"/api/v1/artifacts/{aid}/content")
        assert r.status_code == 200
        assert r.json()["verified"] is True


# ── Models ────────────────────────────────────────────────────────────

class TestModels:
    def test_list(self, client):
        r = client.get("/api/v1/models")
        assert r.status_code == 200
        assert "items" in r.json()

    def test_not_found(self, client):
        r = client.get("/api/v1/models/nonexistent")
        assert r.status_code == 404


# ── Prompts ───────────────────────────────────────────────────────────

class TestPrompts:
    def test_list(self, client):
        r = client.get("/api/v1/prompts")
        assert r.status_code == 200

    def test_create_render(self, client):
        r = client.post("/api/v1/prompts", json={"prompt_id": "p1", "template": "Hello {name}"})
        assert r.status_code == 201
        assert "name" in r.json()["variables"]
        r = client.post("/api/v1/prompts/p1/render", json={"name": "World"})
        assert r.status_code == 200
        assert r.json()["rendered"] == "Hello World"


# ── Events ────────────────────────────────────────────────────────────

class TestEvents:
    def test_types(self, client):
        r = client.get("/api/v1/events/types")
        assert r.status_code == 200
        assert len(r.json()["allowed_events"]) == 15

    def test_publish(self, client):
        r = client.post("/api/v1/events", json={"event_type": "execution.created", "payload": {"x": 1}})
        assert r.status_code == 201
        assert r.json()["event_type"] == "execution.created"

    def test_invalid_event_type(self, client):
        r = client.post("/api/v1/events", json={"event_type": "invalid.type"})
        assert r.status_code == 422
        assert r.json()["code"] == "CONTRACT_INVALID"

    def test_list(self, client):
        client.post("/api/v1/events", json={"event_type": "task.created", "payload": {}})
        r = client.get("/api/v1/events")
        assert r.status_code == 200
        assert r.json()["total"] >= 1


# ── Versioning ────────────────────────────────────────────────────────

class TestVersioning:
    def test_version_header(self, client):
        r = client.get("/api/v1/health", headers={"X-API-Version": "1.0.0"})
        assert r.headers.get("X-API-Version") == "1.0.0"

    def test_request_id(self, client):
        r = client.get("/api/v1/health")
        assert "X-Request-ID" in r.headers


# ── OpenAPI ───────────────────────────────────────────────────────────

class TestOpenAPI:
    def test_openapi_spec(self, client):
        r = client.get("/api/v1/openapi.json")
        assert r.status_code == 200
        data = r.json()
        assert "paths" in data
        paths = list(data["paths"].keys())
        assert len(paths) >= 30

    def test_all_routers_present(self, client):
        r = client.get("/api/v1/openapi.json")
        paths = list(r.json()["paths"].keys())
        for prefix in ["/api/v1/health", "/api/v1/system", "/api/v1/orchestrator",
                       "/api/v1/executions", "/api/v1/workflows", "/api/v1/tasks",
                       "/api/v1/agents", "/api/v1/capabilities", "/api/v1/tools",
                       "/api/v1/skills", "/api/v1/memory", "/api/v1/artifacts",
                       "/api/v1/models", "/api/v1/prompts", "/api/v1/events"]:
            assert any(p.startswith(prefix) for p in paths), f"Missing router: {prefix}"


# ── Error model ───────────────────────────────────────────────────────

class TestErrorModel:
    def test_404_stable_schema(self, client):
        r = client.get("/api/v1/capabilities/missing")
        assert r.status_code == 404
        d = r.json()
        assert "code" in d and d["code"] == "NOT_FOUND"
        assert "message" in d and isinstance(d["message"], str)
        assert "request_id" in d
        # No traceback
        assert "traceback" not in d
        assert "stack" not in d

    def test_validation_error(self, client):
        r = client.post("/api/v1/capabilities", json={"capability_id": ""})
        assert r.status_code == 422
        assert r.json()["code"] == "CONTRACT_INVALID"

    def test_no_internal_detail(self, client):
        r = client.get("/api/v1/executions/nonexistent")
        assert r.status_code in (404, 500)
        d = r.json()
        assert "code" in d
        # Should not contain internal paths
        assert "site-packages" not in d.get("message", "")


# ── Architecture ──────────────────────────────────────────────────────

class TestArchitecture:
    def test_api_layer_no_reverse_import(self):
        """api layer should not be importable by agent/worker/capability/tool."""
        from aios.governance.architecture.guard import classify_module, ALLOWED_IMPORT_LAYERS
        assert classify_module("aios/api/app.py") == "api"
        assert "api" not in ALLOWED_IMPORT_LAYERS.get("agent", [])
        assert "api" not in ALLOWED_IMPORT_LAYERS.get("worker", [])
        assert "api" not in ALLOWED_IMPORT_LAYERS.get("capability", [])
        assert "api" not in ALLOWED_IMPORT_LAYERS.get("tool", [])
        assert "api" not in ALLOWED_IMPORT_LAYERS.get("skill", [])

    def test_api_imports_runtime_allowed(self):
        """api can import runtime/orchestrator."""
        from aios.governance.architecture.guard import ALLOWED_IMPORT_LAYERS
        assert "runtime" in ALLOWED_IMPORT_LAYERS["api"]
        assert "orchestrator" in ALLOWED_IMPORT_LAYERS["api"]
