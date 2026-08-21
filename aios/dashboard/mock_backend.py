"""Mock dashboard backend for offline/simulation mode.

AC-018-10: Dashboard runs offline with Mock backend.
Implements the same DashboardClientProtocol as the real client.
"""

from __future__ import annotations

import time
from typing import Any


class MockDashboardBackend:
    """Mock backend that provides simulated data for all dashboard views.

    Implements the same interface as DashboardClient for seamless swap.
    AC-018-10: Enables offline dashboard operation.
    """

    def __init__(self) -> None:
        self._connected = False
        self._event_log: list[dict[str, Any]] = []
        self._start_time = time.time()

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    # ── Health ──

    def get_health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "runtime": "healthy",
            "orchestrator": "healthy",
            "database": "healthy",
            "model": "unknown",
            "memory": "healthy",
            "workflow": "healthy",
            "capability": "healthy",
            "tool": "healthy",
            "skill": "healthy",
        }

    def get_system_info(self) -> dict[str, Any]:
        return {
            "version": "0.5.0-mock",
            "name": "AIOS",
            "runtime": "mock",
            "uptime": int(time.time() - self._start_time),
        }

    # ── Orchestrator ──

    def get_orchestrator_status(self) -> dict[str, Any]:
        return {
            "status": "idle",
            "active_executions": 0,
            "queued_tasks": 0,
        }

    # ── Executions ──

    def list_executions(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {
                "id": "exec-mock-001",
                "status": "completed",
                "workflow_id": "wf-001",
                "created_at": "2026-08-22T00:00:00Z",
                "duration_ms": 1500,
            },
            {
                "id": "exec-mock-002",
                "status": "running",
                "workflow_id": "wf-002",
                "created_at": "2026-08-22T00:01:00Z",
                "duration_ms": 0,
            },
        ]

    def get_execution(self, execution_id: str) -> dict[str, Any]:
        return {
            "id": execution_id,
            "status": "completed",
            "workflow_id": "wf-001",
            "created_at": "2026-08-22T00:00:00Z",
            "duration_ms": 1500,
            "nodes": [
                {"id": "node-1", "status": "completed", "name": "normalize"},
                {"id": "node-2", "status": "completed", "name": "execute"},
            ],
        }

    # ── Workflows ──

    def list_workflows(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"id": "wf-001", "name": "mock-workflow", "status": "active", "nodes": 3},
        ]

    # ── Tasks ──

    def list_tasks(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"id": "task-mock-001", "title": "Mock Task", "status": "DONE"},
        ]

    # ── Agents ──

    def list_agents(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"id": "agent-general", "type": "general", "status": "idle"},
            {"id": "agent-coder", "type": "coder", "status": "idle"},
        ]

    # ── Capabilities ──

    def list_capabilities(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"id": "cap-code", "name": "code_generation", "tools": ["python", "shell"]},
            {"id": "cap-test", "name": "test_generation", "tools": ["pytest"]},
        ]

    # ── Tools ──

    def list_tools(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"id": "tool-python", "name": "python", "health": "healthy", "invocations": 42},
            {"id": "tool-pytest", "name": "pytest", "health": "healthy", "invocations": 18},
        ]

    # ── Skills ──

    def list_skills(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"id": "skill-mock", "name": "mock-skill", "version": "1.0.0", "status": "enabled"},
        ]

    # ── Memory ──

    def list_memory(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"id": "mem-001", "type": "conversation", "scope": "session", "content": "mock memory"},
            {"id": "mem-002", "type": "knowledge", "scope": "global", "content": "mock knowledge"},
        ]

    # ── Artifacts ──

    def list_artifacts(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {
                "id": "art-001",
                "type": "source",
                "version": 1,
                "checksum": "abc123",
                "execution_id": "exec-mock-001",
                "created_at": "2026-08-22T00:00:00Z",
            },
        ]

    # ── Models ──

    def list_models(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {
                "id": "model-mock",
                "provider": "mock",
                "name": "mock-model",
                "requests": 10,
                "tokens": 5000,
                "cost": 0.0,
            },
        ]

    # ── Prompts ──

    def list_prompts(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {
                "id": "prompt-001",
                "version": 1,
                "template": "You are a helpful assistant.",
                "variables": [],
            },
        ]

    # ── Events ──

    def list_events(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {
                "type": "execution.completed",
                "execution_id": "exec-mock-001",
                "timestamp": "2026-08-22T00:00:01Z",
            },
        ]

    def record_event(self, event: dict[str, Any]) -> None:
        """Record an event in the mock log."""
        self._event_log.append({**event, "timestamp": time.time()})

    def get_event_log(self) -> list[dict[str, Any]]:
        """Get all recorded events."""
        return list(self._event_log)
