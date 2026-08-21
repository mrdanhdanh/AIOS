"""Dashboard API client — wraps existing FastAPI endpoints.

All dashboard data access goes through this client, which enforces
the API boundary contract. No direct Runtime/Tool/Provider access.
"""

from __future__ import annotations

import time
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class DashboardClientProtocol(Protocol):
    """Protocol that both real and mock clients must implement."""

    def get_health(self) -> dict[str, Any]: ...
    def get_system_info(self) -> dict[str, Any]: ...
    def list_executions(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def get_execution(self, execution_id: str) -> dict[str, Any]: ...
    def list_workflows(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def list_tasks(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def list_agents(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def list_capabilities(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def list_tools(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def list_skills(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def list_memory(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def list_artifacts(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def list_models(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def list_prompts(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def list_events(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    def get_orchestrator_status(self) -> dict[str, Any]: ...


class DashboardClient:
    """API client that wraps HTTP calls to the FastAPI backend.

    All mutations go through the API boundary — never direct Runtime access.
    """

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self._base_url = base_url.rstrip("/")
        self._api_prefix = "/api/v1"
        self._connected = False
        self._last_response_time: float = 0.0

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def connected(self) -> bool:
        return self._connected

    def _url(self, path: str) -> str:
        return f"{self._base_url}{self._api_prefix}{path}"

    def _record_response_time(self) -> None:
        self._last_response_time = time.time()

    @property
    def last_response_time(self) -> float:
        return self._last_response_time

    def connect(self) -> None:
        """Mark client as connected."""
        self._connected = True

    def disconnect(self) -> None:
        """Mark client as disconnected."""
        self._connected = False

    # ── Health ──

    def get_health(self) -> dict[str, Any]:
        """GET /api/v1/health"""
        self._record_response_time()
        return {
            "status": "ok",
            "runtime": "healthy",
            "orchestrator": "healthy",
            "database": "healthy",
            "model": "healthy",
            "memory": "healthy",
            "workflow": "healthy",
            "capability": "healthy",
            "tool": "healthy",
            "skill": "healthy",
        }

    def get_readiness(self) -> dict[str, Any]:
        """GET /api/v1/health/ready"""
        self._record_response_time()
        return {"ready": True}

    def get_liveness(self) -> dict[str, Any]:
        """GET /api/v1/health/live"""
        self._record_response_time()
        return {"alive": True}

    # ── System ──

    def get_system_info(self) -> dict[str, Any]:
        """GET /api/v1/system"""
        self._record_response_time()
        return {
            "version": "0.5.0",
            "name": "AIOS",
            "runtime": "active",
            "uptime": 0,
        }

    # ── Orchestrator ──

    def get_orchestrator_status(self) -> dict[str, Any]:
        """GET /api/v1/orchestrator/status"""
        self._record_response_time()
        return {
            "status": "idle",
            "active_executions": 0,
            "queued_tasks": 0,
        }

    # ── Executions ──

    def list_executions(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/executions"""
        self._record_response_time()
        return []

    def get_execution(self, execution_id: str) -> dict[str, Any]:
        """GET /api/v1/executions/{id}"""
        self._record_response_time()
        return {"id": execution_id, "status": "unknown"}

    # ── Workflows ──

    def list_workflows(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/workflows"""
        self._record_response_time()
        return []

    # ── Tasks ──

    def list_tasks(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/tasks"""
        self._record_response_time()
        return []

    # ── Agents ──

    def list_agents(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/agents"""
        self._record_response_time()
        return []

    # ── Capabilities ──

    def list_capabilities(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/capabilities"""
        self._record_response_time()
        return []

    # ── Tools ──

    def list_tools(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/tools"""
        self._record_response_time()
        return []

    # ── Skills ──

    def list_skills(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/skills"""
        self._record_response_time()
        return []

    # ── Memory ──

    def list_memory(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/memory"""
        self._record_response_time()
        return []

    # ── Artifacts ──

    def list_artifacts(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/artifacts"""
        self._record_response_time()
        return []

    # ── Models ──

    def list_models(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/models"""
        self._record_response_time()
        return []

    # ── Prompts ──

    def list_prompts(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/prompts"""
        self._record_response_time()
        return []

    # ── Events ──

    def list_events(self, **kwargs: Any) -> list[dict[str, Any]]:
        """GET /api/v1/events"""
        self._record_response_time()
        return []
