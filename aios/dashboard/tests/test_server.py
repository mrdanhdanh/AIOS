"""Tests for dashboard server."""

from __future__ import annotations

import pytest

from aios.dashboard.client import DashboardClient
from aios.dashboard.health import HealthStatus
from aios.dashboard.mock_backend import MockDashboardBackend
from aios.dashboard.server import DashboardServer
from aios.dashboard.websocket_client import DashboardWebSocketClient


class TestDashboardServer:
    """Test suite for DashboardServer."""

    def _make_server(self, use_mock: bool = False) -> DashboardServer:
        if use_mock:
            client = MockDashboardBackend()
            client.connect()
        else:
            client = DashboardClient()
        ws = DashboardWebSocketClient()
        ws.connect()
        return DashboardServer(client=client, ws_client=ws)

    def test_instantiation(self) -> None:
        server = self._make_server()
        assert server.client is not None
        assert server.ws_client is not None

    def test_chat_view(self) -> None:
        server = self._make_server(use_mock=True)
        view = server.get_chat_view("conv-1")
        d = view.to_dict()
        assert d["view"] == "chat"
        assert d["conversation_id"] == "conv-1"

    def test_workflow_view(self) -> None:
        server = self._make_server(use_mock=True)
        view = server.get_workflow_view("wf-001")
        d = view.to_dict()
        assert d["view"] == "workflow"
        assert d["workflow_id"] == "wf-001"

    def test_workflow_view_empty(self) -> None:
        server = self._make_server()
        view = server.get_workflow_view("nonexistent")
        assert view.workflow_id == ""

    def test_timeline_view(self) -> None:
        server = self._make_server()
        # Add some events
        server.ws_client.on_event({"type": "exec.started"})
        server.ws_client.on_event({"type": "exec.done"})
        view = server.get_timeline_view()
        d = view.to_dict()
        assert d["view"] == "timeline"
        assert d["count"] == 2

    def test_tools_view(self) -> None:
        server = self._make_server(use_mock=True)
        view = server.get_tools_view()
        d = view.to_dict()
        assert d["view"] == "tools"
        assert d["total_invocations"] > 0

    def test_memory_view(self) -> None:
        server = self._make_server(use_mock=True)
        view = server.get_memory_view()
        d = view.to_dict()
        assert d["view"] == "memory"
        assert d["total_entries"] > 0

    def test_artifact_view(self) -> None:
        server = self._make_server(use_mock=True)
        view = server.get_artifact_view()
        d = view.to_dict()
        assert d["view"] == "artifacts"
        assert d["count"] > 0

    def test_skills_view(self) -> None:
        server = self._make_server(use_mock=True)
        view = server.get_skills_view()
        d = view.to_dict()
        assert d["view"] == "skills"
        assert d["installed_count"] > 0

    def test_models_view(self) -> None:
        server = self._make_server(use_mock=True)
        view = server.get_models_view()
        d = view.to_dict()
        assert d["view"] == "models"

    def test_prompts_view(self) -> None:
        server = self._make_server(use_mock=True)
        view = server.get_prompts_view()
        d = view.to_dict()
        assert d["view"] == "prompts"
        assert d["count"] > 0

    def test_health_view(self) -> None:
        server = self._make_server(use_mock=True)
        view = server.get_health_view()
        d = view.to_dict()
        assert d["view"] == "health"
        assert len(d["components"]) == 9
        # Mock has model=unknown, so overall should not be PASS
        assert d["overall_status"] != "pass"

    def test_get_all_views(self) -> None:
        server = self._make_server(use_mock=True)
        all_views = server.get_all_views()
        assert len(all_views) == 10
        assert "chat" in all_views
        assert "health" in all_views

    def test_send_chat_message(self) -> None:
        server = self._make_server()
        result = server.send_chat_message("hello")
        assert result["status"] == "sent"
        assert result["message"] == "hello"

    def test_execute_workflow(self) -> None:
        server = self._make_server()
        result = server.execute_workflow("wf-1")
        assert result["status"] == "submitted"

    def test_install_skill(self) -> None:
        server = self._make_server()
        result = server.install_skill("skill-1")
        assert result["status"] == "installing"

    def test_refresh_health(self) -> None:
        server = self._make_server(use_mock=True)
        view = server.refresh_health()
        assert view.to_dict()["view"] == "health"


class TestDashboardServerWithWebSocket:
    """Test WebSocket integration in server."""

    def test_ws_event_appears_in_timeline(self) -> None:
        client = MockDashboardBackend()
        client.connect()
        ws = DashboardWebSocketClient()
        ws.connect()
        server = DashboardServer(client=client, ws_client=ws)

        ws.on_event({"type": "execution.started", "id": "ex-1"})
        ws.on_event({"type": "execution.completed", "id": "ex-1"})

        view = server.get_timeline_view()
        assert view.to_dict()["count"] == 2

    def test_ws_event_filtering(self) -> None:
        ws = DashboardWebSocketClient()
        ws.connect()
        ws.on_event({"type": "a"})
        ws.on_event({"type": "b"})
        ws.on_event({"type": "a"})

        events_a = ws.get_events(event_type="a")
        assert len(events_a) == 2

        events_b = ws.get_events(event_type="b")
        assert len(events_b) == 1

