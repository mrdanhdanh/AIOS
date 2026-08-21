"""Tests for mock extension backend and event client."""

from __future__ import annotations

import pytest

from aios.extension.contracts import (
    CommandId,
    CommandRequest,
    WorkspaceContext,
)
from aios.extension.event_client import ExtensionEventClient
from aios.extension.mock_backend import MockExtensionBackend


class TestMockExtensionBackend:
    def test_connect_disconnect(self) -> None:
        mock = MockExtensionBackend()
        assert mock.connected is False
        mock.connect()
        assert mock.connected is True
        mock.disconnect()
        assert mock.connected is False

    def test_execute_chat(self) -> None:
        mock = MockExtensionBackend()
        mock.connect()
        req = CommandRequest(
            command_id=CommandId.CHAT,
            context=WorkspaceContext(),
        )
        resp = mock.execute_command(req)
        assert resp.succeeded
        assert "response" in resp.result

    def test_execute_explain(self) -> None:
        mock = MockExtensionBackend()
        mock.connect()
        req = CommandRequest(
            command_id=CommandId.EXPLAIN,
            context=WorkspaceContext(),
        )
        resp = mock.execute_command(req)
        assert resp.succeeded
        assert "explanation" in resp.result

    def test_execute_fix(self) -> None:
        mock = MockExtensionBackend()
        mock.connect()
        req = CommandRequest(
            command_id=CommandId.FIX_SELECTION,
            context=WorkspaceContext(),
        )
        resp = mock.execute_command(req)
        assert resp.succeeded
        assert "fixes" in resp.result

    def test_execute_generate_test(self) -> None:
        mock = MockExtensionBackend()
        mock.connect()
        req = CommandRequest(
            command_id=CommandId.GENERATE_TEST,
            context=WorkspaceContext(),
        )
        resp = mock.execute_command(req)
        assert resp.succeeded
        assert "test_code" in resp.result

    def test_execute_unknown(self) -> None:
        mock = MockExtensionBackend()
        mock.connect()
        req = CommandRequest(
            command_id=CommandId.REVIEW_PR,
            context=WorkspaceContext(),
        )
        resp = mock.execute_command(req)
        assert resp.succeeded
        assert resp.result.get("mock") is True

    def test_get_health(self) -> None:
        mock = MockExtensionBackend()
        h = mock.get_health()
        assert h["status"] == "ok"
        assert h["mode"] == "mock"

    def test_list_tasks(self) -> None:
        mock = MockExtensionBackend()
        tasks = mock.list_tasks()
        assert len(tasks) >= 1

    def test_get_task_progress(self) -> None:
        mock = MockExtensionBackend()
        p = mock.get_task_progress("t1")
        assert p["task_id"] == "t1"

    def test_list_artifacts(self) -> None:
        mock = MockExtensionBackend()
        arts = mock.list_artifacts()
        assert len(arts) >= 1
        assert "provenance" in arts[0]

    def test_get_diagnostics(self) -> None:
        mock = MockExtensionBackend()
        diags = mock.get_diagnostics("test.py")
        assert len(diags) >= 1

    def test_command_log(self) -> None:
        mock = MockExtensionBackend()
        mock.connect()
        req = CommandRequest(
            command_id=CommandId.CHAT,
            context=WorkspaceContext(),
        )
        mock.execute_command(req)
        log = mock.get_command_log()
        assert len(log) == 1
        assert log[0]["command"] == "aios.chat"


class TestExtensionEventClient:
    def test_connect_disconnect(self) -> None:
        ec = ExtensionEventClient()
        assert ec.connected is False
        ec.connect()
        assert ec.connected is True
        ec.disconnect()
        assert ec.connected is False

    def test_on_event(self) -> None:
        ec = ExtensionEventClient()
        ec.connect()
        ec.on_event({"type": "test"})
        assert ec.event_count == 1

    def test_reconnect_preserves_events(self) -> None:
        ec = ExtensionEventClient()
        ec.connect()
        ec.on_event({"type": "before"})
        ec.disconnect()
        ec.reconnect()
        ec.on_event({"type": "after"})
        assert ec.event_count == 2
        assert ec.reconnect_count == 1

    def test_listener(self) -> None:
        received = []
        ec = ExtensionEventClient()
        ec.add_listener(lambda e: received.append(e))
        ec.on_event({"type": "test"})
        assert len(received) == 1

    def test_remove_listener(self) -> None:
        received = []
        listener = lambda e: received.append(e)
        ec = ExtensionEventClient()
        ec.add_listener(listener)
        ec.on_event({"type": "a"})
        ec.remove_listener(listener)
        ec.on_event({"type": "b"})
        assert len(received) == 1

    def test_filter_by_type(self) -> None:
        ec = ExtensionEventClient()
        ec.on_event({"type": "a"})
        ec.on_event({"type": "b"})
        ec.on_event({"type": "a"})
        filtered = ec.get_events(event_type="a")
        assert len(filtered) == 2

    def test_filter_by_limit(self) -> None:
        ec = ExtensionEventClient()
        for i in range(5):
            ec.on_event({"type": f"e{i}"})
        filtered = ec.get_events(limit=2)
        assert len(filtered) == 2

    def test_to_dict(self) -> None:
        ec = ExtensionEventClient()
        d = ec.to_dict()
        assert "ws_url" in d
        assert "connected" in d
