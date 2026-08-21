"""Tests for mock dashboard backend."""

from __future__ import annotations

import pytest

from aios.dashboard.client import DashboardClientProtocol
from aios.dashboard.mock_backend import MockDashboardBackend


class TestMockDashboardBackend:
    """Test suite for MockDashboardBackend."""

    def test_is_protocol(self) -> None:
        mock = MockDashboardBackend()
        assert isinstance(mock, DashboardClientProtocol)

    def test_connect_disconnect(self) -> None:
        mock = MockDashboardBackend()
        assert mock.connected is False
        mock.connect()
        assert mock.connected is True
        mock.disconnect()
        assert mock.connected is False

    def test_health(self) -> None:
        mock = MockDashboardBackend()
        h = mock.get_health()
        assert h["status"] == "ok"
        assert "runtime" in h
        assert "model" in h

    def test_health_model_unknown(self) -> None:
        """AC-018-10: Mock backend has model=unknown for testing."""
        mock = MockDashboardBackend()
        h = mock.get_health()
        assert h["model"] == "unknown"

    def test_system_info(self) -> None:
        mock = MockDashboardBackend()
        info = mock.get_system_info()
        assert "mock" in info["version"]
        assert info["runtime"] == "mock"

    def test_orchestrator_status(self) -> None:
        mock = MockDashboardBackend()
        status = mock.get_orchestrator_status()
        assert status["status"] == "idle"

    def test_list_executions(self) -> None:
        mock = MockDashboardBackend()
        execs = mock.list_executions()
        assert len(execs) >= 1
        assert execs[0]["id"] == "exec-mock-001"

    def test_get_execution(self) -> None:
        mock = MockDashboardBackend()
        ex = mock.get_execution("exec-1")
        assert ex["id"] == "exec-1"
        assert "nodes" in ex

    def test_list_workflows(self) -> None:
        mock = MockDashboardBackend()
        wfs = mock.list_workflows()
        assert len(wfs) >= 1

    def test_list_tasks(self) -> None:
        mock = MockDashboardBackend()
        tasks = mock.list_tasks()
        assert len(tasks) >= 1

    def test_list_agents(self) -> None:
        mock = MockDashboardBackend()
        agents = mock.list_agents()
        assert len(agents) >= 1

    def test_list_capabilities(self) -> None:
        mock = MockDashboardBackend()
        caps = mock.list_capabilities()
        assert len(caps) >= 1

    def test_list_tools(self) -> None:
        mock = MockDashboardBackend()
        tools = mock.list_tools()
        assert len(tools) >= 1
        assert "invocations" in tools[0]

    def test_list_skills(self) -> None:
        mock = MockDashboardBackend()
        skills = mock.list_skills()
        assert len(skills) >= 1

    def test_list_memory(self) -> None:
        mock = MockDashboardBackend()
        mem = mock.list_memory()
        assert len(mem) >= 1
        types = {m["type"] for m in mem}
        assert "conversation" in types or "knowledge" in types

    def test_list_artifacts(self) -> None:
        mock = MockDashboardBackend()
        arts = mock.list_artifacts()
        assert len(arts) >= 1
        assert "checksum" in arts[0]

    def test_list_models(self) -> None:
        mock = MockDashboardBackend()
        models = mock.list_models()
        assert len(models) >= 1

    def test_list_prompts(self) -> None:
        mock = MockDashboardBackend()
        prompts = mock.list_prompts()
        assert len(prompts) >= 1

    def test_list_events(self) -> None:
        mock = MockDashboardBackend()
        events = mock.list_events()
        assert len(events) >= 1

    def test_record_event(self) -> None:
        mock = MockDashboardBackend()
        mock.record_event({"type": "test"})
        log = mock.get_event_log()
        assert len(log) == 1
        assert log[0]["type"] == "test"
        assert "timestamp" in log[0]

    def test_event_log_independent_copy(self) -> None:
        mock = MockDashboardBackend()
        mock.record_event({"type": "a"})
        log1 = mock.get_event_log()
        mock.record_event({"type": "b"})
        log2 = mock.get_event_log()
        assert len(log1) == 1
        assert len(log2) == 2


class TestMockWebSocketClient:
    """Test WebSocket client."""

    def test_connect_disconnect(self) -> None:
        from aios.dashboard.websocket_client import DashboardWebSocketClient
        ws = DashboardWebSocketClient()
        assert ws.connected is False
        ws.connect()
        assert ws.connected is True
        ws.disconnect()
        assert ws.connected is False

    def test_on_event(self) -> None:
        from aios.dashboard.websocket_client import DashboardWebSocketClient
        ws = DashboardWebSocketClient()
        ws.connect()
        ws.on_event({"type": "test"})
        assert ws.event_count == 1
        assert ws.sequence == 1

    def test_event_ordering(self) -> None:
        from aios.dashboard.websocket_client import DashboardWebSocketClient
        ws = DashboardWebSocketClient()
        ws.connect()
        ws.on_event({"type": "a"})
        ws.on_event({"type": "b"})
        ws.on_event({"type": "c"})
        events = ws.get_events()
        assert events[0]["_sequence"] == 1
        assert events[1]["_sequence"] == 2
        assert events[2]["_sequence"] == 3

    def test_reconnect_preserves_events(self) -> None:
        from aios.dashboard.websocket_client import DashboardWebSocketClient
        ws = DashboardWebSocketClient()
        ws.connect()
        ws.on_event({"type": "before"})
        ws.disconnect()
        ws.reconnect()
        ws.on_event({"type": "after"})
        assert ws.event_count == 2
        assert ws.reconnect_count == 1
        events = ws.get_events()
        assert events[0]["type"] == "before"
        assert events[1]["type"] == "after"

    def test_listener(self) -> None:
        from aios.dashboard.websocket_client import DashboardWebSocketClient
        received = []
        ws = DashboardWebSocketClient()
        ws.add_listener(lambda e: received.append(e))
        ws.on_event({"type": "test"})
        assert len(received) == 1
        assert received[0]["type"] == "test"

    def test_remove_listener(self) -> None:
        from aios.dashboard.websocket_client import DashboardWebSocketClient
        received = []
        listener = lambda e: received.append(e)
        ws = DashboardWebSocketClient()
        ws.add_listener(listener)
        ws.on_event({"type": "a"})
        ws.remove_listener(listener)
        ws.on_event({"type": "b"})
        assert len(received) == 1

    def test_filter_by_type(self) -> None:
        from aios.dashboard.websocket_client import DashboardWebSocketClient
        ws = DashboardWebSocketClient()
        ws.on_event({"type": "a"})
        ws.on_event({"type": "b"})
        ws.on_event({"type": "a"})
        filtered = ws.get_events(event_type="a")
        assert len(filtered) == 2

    def test_filter_by_sequence(self) -> None:
        from aios.dashboard.websocket_client import DashboardWebSocketClient
        ws = DashboardWebSocketClient()
        ws.on_event({"type": "a"})
        ws.on_event({"type": "b"})
        ws.on_event({"type": "c"})
        filtered = ws.get_events(since_sequence=1)
        assert len(filtered) == 2

    def test_filter_by_limit(self) -> None:
        from aios.dashboard.websocket_client import DashboardWebSocketClient
        ws = DashboardWebSocketClient()
        for i in range(5):
            ws.on_event({"type": f"e{i}"})
        filtered = ws.get_events(limit=2)
        assert len(filtered) == 2

    def test_get_last_event(self) -> None:
        from aios.dashboard.websocket_client import DashboardWebSocketClient
        ws = DashboardWebSocketClient()
        assert ws.get_last_event() is None
        ws.on_event({"type": "last"})
        assert ws.get_last_event()["type"] == "last"

    def test_to_dict(self) -> None:
        from aios.dashboard.websocket_client import DashboardWebSocketClient
        ws = DashboardWebSocketClient()
        d = ws.to_dict()
        assert "ws_url" in d
        assert "connected" in d
        assert "event_count" in d

