"""Tests for DashboardClient API wrapper."""

from __future__ import annotations

import pytest

from aios.dashboard.client import DashboardClient, DashboardClientProtocol


class TestDashboardClient:
    """Test suite for DashboardClient."""

    def test_instantiation(self) -> None:
        client = DashboardClient()
        assert client.base_url == "http://localhost:8000"
        assert client.connected is False

    def test_custom_base_url(self) -> None:
        client = DashboardClient(base_url="http://custom:9000")
        assert client.base_url == "http://custom:9000"

    def test_trailing_slash_stripped(self) -> None:
        client = DashboardClient(base_url="http://localhost:8000/")
        assert client.base_url == "http://localhost:8000"

    def test_connect_disconnect(self) -> None:
        client = DashboardClient()
        assert client.connected is False
        client.connect()
        assert client.connected is True
        client.disconnect()
        assert client.connected is False

    def test_is_protocol(self) -> None:
        client = DashboardClient()
        assert isinstance(client, DashboardClientProtocol)

    def test_get_health(self) -> None:
        client = DashboardClient()
        health = client.get_health()
        assert "status" in health
        assert health["status"] == "ok"
        assert "runtime" in health
        assert "orchestrator" in health

    def test_get_readiness(self) -> None:
        client = DashboardClient()
        ready = client.get_readiness()
        assert ready["ready"] is True

    def test_get_liveness(self) -> None:
        client = DashboardClient()
        alive = client.get_liveness()
        assert alive["alive"] is True

    def test_get_system_info(self) -> None:
        client = DashboardClient()
        info = client.get_system_info()
        assert "version" in info
        assert info["name"] == "AIOS"

    def test_get_orchestrator_status(self) -> None:
        client = DashboardClient()
        status = client.get_orchestrator_status()
        assert "status" in status
        assert status["active_executions"] == 0

    def test_list_executions(self) -> None:
        client = DashboardClient()
        execs = client.list_executions()
        assert isinstance(execs, list)

    def test_get_execution(self) -> None:
        client = DashboardClient()
        ex = client.get_execution("exec-001")
        assert ex["id"] == "exec-001"

    def test_list_workflows(self) -> None:
        client = DashboardClient()
        wfs = client.list_workflows()
        assert isinstance(wfs, list)

    def test_list_tasks(self) -> None:
        client = DashboardClient()
        tasks = client.list_tasks()
        assert isinstance(tasks, list)

    def test_list_agents(self) -> None:
        client = DashboardClient()
        agents = client.list_agents()
        assert isinstance(agents, list)

    def test_list_capabilities(self) -> None:
        client = DashboardClient()
        caps = client.list_capabilities()
        assert isinstance(caps, list)

    def test_list_tools(self) -> None:
        client = DashboardClient()
        tools = client.list_tools()
        assert isinstance(tools, list)

    def test_list_skills(self) -> None:
        client = DashboardClient()
        skills = client.list_skills()
        assert isinstance(skills, list)

    def test_list_memory(self) -> None:
        client = DashboardClient()
        mem = client.list_memory()
        assert isinstance(mem, list)

    def test_list_artifacts(self) -> None:
        client = DashboardClient()
        arts = client.list_artifacts()
        assert isinstance(arts, list)

    def test_list_models(self) -> None:
        client = DashboardClient()
        models = client.list_models()
        assert isinstance(models, list)

    def test_list_prompts(self) -> None:
        client = DashboardClient()
        prompts = client.list_prompts()
        assert isinstance(prompts, list)

    def test_list_events(self) -> None:
        client = DashboardClient()
        events = client.list_events()
        assert isinstance(events, list)

    def test_response_time_recorded(self) -> None:
        client = DashboardClient()
        assert client.last_response_time == 0.0
        client.get_health()
        assert client.last_response_time > 0.0

