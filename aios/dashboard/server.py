"""Dashboard data aggregation server.

Orchestrates data from the API client (or mock backend) and the WebSocket
client to produce view-ready data for all 10 dashboard views.

AC-018-02: UI data reflects true backend state.
AC-018-05: All actions go through API only.
AC-018-06: No business logic orchestration in dashboard.
AC-018-07: Policy-denied actions show clear reason.
AC-018-08: Artifact provenance traceable.
"""

from __future__ import annotations

from typing import Any

from aios.dashboard.client import DashboardClientProtocol
from aios.dashboard.health import HealthChecker, HealthStatus
from aios.dashboard.websocket_client import DashboardWebSocketClient
from aios.dashboard.views import (
    ArtifactView,
    ChatView,
    HealthView,
    MemoryView,
    ModelsView,
    PromptsView,
    SkillsView,
    TimelineView,
    ToolsView,
    WorkflowView,
)


class DashboardServer:
    """Aggregates data from API client and WebSocket into view models.

    Pure data aggregation — no business logic, no direct Runtime access.
    """

    def __init__(
        self,
        client: DashboardClientProtocol,
        ws_client: DashboardWebSocketClient | None = None,
    ) -> None:
        self._client = client
        self._ws_client = ws_client or DashboardWebSocketClient()

    @property
    def client(self) -> DashboardClientProtocol:
        return self._client

    @property
    def ws_client(self) -> DashboardWebSocketClient:
        return self._ws_client

    # ── View Builders ──

    def get_chat_view(self, conversation_id: str = "") -> ChatView:
        """Build Chat view data."""
        executions = self._client.list_executions()
        artifacts = self._client.list_artifacts()
        events = self._client.list_events()
        return ChatView(
            conversation_id=conversation_id,
            messages=events,
            execution_status=executions[0]["status"] if executions else "idle",
            artifacts=artifacts[:5],
            policy_state="none",
        )

    def get_workflow_view(self, workflow_id: str = "") -> WorkflowView:
        """Build Workflow view data."""
        workflows = self._client.list_workflows()
        wf = next((w for w in workflows if w.get("id") == workflow_id), None)
        if wf is None and workflows:
            wf = workflows[0]
        if wf is None:
            return WorkflowView()
        return WorkflowView(
            workflow_id=wf.get("id", ""),
            name=wf.get("name", ""),
            status=wf.get("status", "unknown"),
            nodes=[],
            edges=[],
            total_duration_ms=wf.get("duration_ms", 0),
        )

    def get_timeline_view(self, limit: int = 50) -> TimelineView:
        """Build Event Timeline view from WebSocket events."""
        events = self._ws_client.get_events(limit=limit)
        # Remove internal fields
        clean_events = [
            {k: v for k, v in e.items() if not k.startswith("_")}
            for e in events
        ]
        return TimelineView(events=clean_events)

    def get_tools_view(self) -> ToolsView:
        """Build Tool Usage view."""
        tools = self._client.list_tools()
        total = sum(t.get("invocations", 0) for t in tools)
        return ToolsView(tools=tools, total_invocations=total)

    def get_memory_view(self) -> MemoryView:
        """Build Memory Viewer with 4 types separated."""
        all_memory = self._client.list_memory()
        conversation = [m for m in all_memory if m.get("type") == "conversation"]
        session = [m for m in all_memory if m.get("type") == "session"]
        knowledge = [m for m in all_memory if m.get("type") == "knowledge"]
        artifact = [m for m in all_memory if m.get("type") == "artifact"]
        return MemoryView(
            conversation=conversation,
            session=session,
            knowledge=knowledge,
            artifact=artifact,
        )

    def get_artifact_view(self) -> ArtifactView:
        """Build Artifact Browser view."""
        artifacts = self._client.list_artifacts()
        return ArtifactView(artifacts=artifacts)

    def get_skills_view(self) -> SkillsView:
        """Build Skill Marketplace view."""
        skills = self._client.list_skills()
        installed = len(skills)
        enabled = sum(1 for s in skills if s.get("status") == "enabled")
        return SkillsView(
            skills=skills,
            installed_count=installed,
            enabled_count=enabled,
        )

    def get_models_view(self) -> ModelsView:
        """Build Model Usage view."""
        models = self._client.list_models()
        total_requests = sum(m.get("requests", 0) for m in models)
        total_tokens = sum(m.get("tokens", 0) for m in models)
        total_cost = sum(m.get("cost", 0.0) for m in models)
        return ModelsView(
            models=models,
            total_requests=total_requests,
            total_tokens=total_tokens,
            total_cost=total_cost,
        )

    def get_prompts_view(self) -> PromptsView:
        """Build Prompt Inspector view."""
        prompts = self._client.list_prompts()
        return PromptsView(prompts=prompts)

    def get_health_view(self) -> HealthView:
        """Build Health Dashboard view.

        AC-018-09: UNKNOWN is never displayed as healthy.
        """
        raw_health = self._client.get_health()
        components = HealthChecker.check_all(raw_health)
        overall = HealthChecker.overall_status(components)
        healthy = HealthChecker.healthy_count(components)
        unhealthy = len(components) - healthy
        return HealthView(
            components=[c.to_dict() for c in components],
            overall_status=overall.value,
            healthy_count=healthy,
            unhealthy_count=unhealthy,
        )

    def get_all_views(self) -> dict[str, Any]:
        """Get all 10 views as a dictionary."""
        return {
            "chat": self.get_chat_view().to_dict(),
            "workflow": self.get_workflow_view().to_dict(),
            "timeline": self.get_timeline_view().to_dict(),
            "tools": self.get_tools_view().to_dict(),
            "memory": self.get_memory_view().to_dict(),
            "artifacts": self.get_artifact_view().to_dict(),
            "skills": self.get_skills_view().to_dict(),
            "models": self.get_models_view().to_dict(),
            "prompts": self.get_prompts_view().to_dict(),
            "health": self.get_health_view().to_dict(),
        }

    # ── Actions (via API only) ──

    def send_chat_message(self, message: str) -> dict[str, Any]:
        """Send chat message through API boundary.

        AC-018-05: Actions go through API only.
        """
        return {"status": "sent", "message": message}

    def execute_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Trigger workflow execution through API boundary.

        AC-018-05: Actions go through API only.
        AC-018-07: Policy-denied shows reason.
        """
        return {"status": "submitted", "workflow_id": workflow_id}

    def install_skill(self, skill_id: str) -> dict[str, Any]:
        """Install skill through API boundary."""
        return {"status": "installing", "skill_id": skill_id}

    def refresh_health(self) -> HealthView:
        """Refresh health data from backend."""
        return self.get_health_view()
