"""Tests for extension API client."""

from __future__ import annotations

import pytest

from aios.extension.api_client import ExtensionApiClient
from aios.extension.contracts import (
    CommandId,
    CommandRequest,
    WorkspaceContext,
)


class TestExtensionApiClient:
    def test_instantiation(self) -> None:
        client = ExtensionApiClient()
        assert client.base_url == "http://localhost:8000"
        assert client.connected is False

    def test_connect_disconnect(self) -> None:
        client = ExtensionApiClient()
        client.connect()
        assert client.connected is True
        client.disconnect()
        assert client.connected is False

    def test_execute_command(self) -> None:
        client = ExtensionApiClient()
        req = CommandRequest(
            command_id=CommandId.CHAT,
            context=WorkspaceContext(),
            prompt="hello",
        )
        resp = client.execute_command(req)
        assert resp.succeeded
        assert resp.result["submitted"] is True

    def test_send_chat(self) -> None:
        client = ExtensionApiClient()
        resp = client.send_chat("hi", WorkspaceContext())
        assert resp.succeeded
        assert "response" in resp.result

    def test_explain_code(self) -> None:
        client = ExtensionApiClient()
        resp = client.explain_code("x = 1", "test.py")
        assert resp.succeeded

    def test_fix_code(self) -> None:
        client = ExtensionApiClient()
        resp = client.fix_code("x = 1", "test.py")
        assert resp.succeeded

    def test_list_tasks(self) -> None:
        client = ExtensionApiClient()
        tasks = client.list_tasks()
        assert isinstance(tasks, list)

    def test_get_task_progress(self) -> None:
        client = ExtensionApiClient()
        progress = client.get_task_progress("task-1")
        assert progress["task_id"] == "task-1"

    def test_list_artifacts(self) -> None:
        client = ExtensionApiClient()
        arts = client.list_artifacts()
        assert isinstance(arts, list)

    def test_get_diagnostics(self) -> None:
        client = ExtensionApiClient()
        diags = client.get_diagnostics("test.py")
        assert isinstance(diags, list)

    def test_get_health(self) -> None:
        client = ExtensionApiClient()
        health = client.get_health()
        assert health["status"] == "ok"

    def test_to_dict(self) -> None:
        client = ExtensionApiClient()
        d = client.to_dict()
        assert "base_url" in d
        assert "connected" in d
