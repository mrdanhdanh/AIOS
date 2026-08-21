"""Mock extension backend for offline testing.

AC-019-08: Offline deterministic path works.
"""

from __future__ import annotations

import time
from typing import Any

from aios.extension.contracts import (
    CommandId,
    CommandRequest,
    CommandResponse,
    ExtensionDiagnostic,
    DiagnosticSeverity,
    WorkspaceContext,
)


class MockExtensionBackend:
    """Mock backend that simulates AIOS API responses.

    Enables offline extension testing without a running AIOS instance.
    """

    def __init__(self) -> None:
        self._connected = False
        self._command_log: list[dict[str, Any]] = []
        self._start_time = time.time()

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    def execute_command(self, request: CommandRequest) -> CommandResponse:
        """Simulate command execution."""
        self._command_log.append({
            "command": request.command_id.value,
            "timestamp": time.time(),
        })

        if request.command_id == CommandId.CHAT:
            return CommandResponse(
                command_id=CommandId.CHAT,
                status="success",
                result={"response": "Mock AIOS response"},
            )
        elif request.command_id == CommandId.EXPLAIN:
            return CommandResponse(
                command_id=CommandId.EXPLAIN,
                status="success",
                result={"explanation": "Mock explanation of the code"},
            )
        elif request.command_id == CommandId.FIX_SELECTION:
            return CommandResponse(
                command_id=CommandId.FIX_SELECTION,
                status="success",
                result={"fixes": [{"line": 1, "description": "Mock fix"}]},
            )
        elif request.command_id == CommandId.GENERATE_TEST:
            return CommandResponse(
                command_id=CommandId.GENERATE_TEST,
                status="success",
                result={"test_code": "def test_mock(): assert True"},
            )
        else:
            return CommandResponse(
                command_id=request.command_id,
                status="success",
                result={"mock": True},
            )

    def get_health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "mode": "mock",
            "uptime": int(time.time() - self._start_time),
        }

    def list_tasks(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"id": "task-mock-001", "title": "Mock Task", "status": "DONE", "progress": 100},
        ]

    def get_task_progress(self, task_id: str) -> dict[str, Any]:
        return {"task_id": task_id, "status": "DONE", "progress": 100}

    def list_artifacts(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {
                "id": "art-ext-001",
                "type": "source",
                "checksum": "mock checksum",
                "execution_id": "exec-mock",
                "provenance": {"source": "mock"},
            },
        ]

    def get_diagnostics(self, file_path: str = "") -> list[dict[str, Any]]:
        return [
            {
                "severity": "info",
                "message": "Mock diagnostic",
                "file": file_path,
                "source": "aios",
            },
        ]

    def get_command_log(self) -> list[dict[str, Any]]:
        """Get all executed commands."""
        return list(self._command_log)
