"""AIOS Dashboard — Operational UI data layer.

Provides data aggregation, API client, WebSocket client, mock backend,
and 10 view models for the unified operational dashboard.
"""

from aios.dashboard.client import DashboardClient, DashboardClientProtocol
from aios.dashboard.health import HealthStatus, HealthChecker
from aios.dashboard.mock_backend import MockDashboardBackend
from aios.dashboard.server import DashboardServer
from aios.dashboard.views import (
    ChatView,
    WorkflowView,
    TimelineView,
    ToolsView,
    MemoryView,
    ArtifactView,
    SkillsView,
    ModelsView,
    PromptsView,
    HealthView,
)
from aios.dashboard.websocket_client import DashboardWebSocketClient

__all__ = [
    "DashboardClient",
    "DashboardClientProtocol",
    "HealthStatus",
    "HealthChecker",
    "MockDashboardBackend",
    "DashboardServer",
    "DashboardWebSocketClient",
    "ChatView",
    "WorkflowView",
    "TimelineView",
    "ToolsView",
    "MemoryView",
    "ArtifactView",
    "SkillsView",
    "ModelsView",
    "PromptsView",
    "HealthView",
]
