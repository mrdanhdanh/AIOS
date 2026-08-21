"""Tests for dashboard view models."""

from __future__ import annotations

import pytest

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


class TestChatView:
    def test_default(self) -> None:
        v = ChatView()
        d = v.to_dict()
        assert d["view"] == "chat"
        assert d["execution_status"] == "idle"
        assert d["messages"] == []

    def test_with_data(self) -> None:
        v = ChatView(
            conversation_id="conv-1",
            messages=[{"role": "user", "content": "hi"}],
            execution_status="running",
        )
        d = v.to_dict()
        assert d["conversation_id"] == "conv-1"
        assert len(d["messages"]) == 1


class TestWorkflowView:
    def test_default(self) -> None:
        v = WorkflowView()
        d = v.to_dict()
        assert d["view"] == "workflow"
        assert d["status"] == "unknown"

    def test_with_data(self) -> None:
        v = WorkflowView(workflow_id="wf-1", name="test", status="active")
        d = v.to_dict()
        assert d["workflow_id"] == "wf-1"
        assert d["name"] == "test"


class TestTimelineView:
    def test_default(self) -> None:
        v = TimelineView()
        d = v.to_dict()
        assert d["view"] == "timeline"
        assert d["count"] == 0

    def test_with_events(self) -> None:
        v = TimelineView(events=[{"type": "exec.started"}, {"type": "exec.done"}])
        assert v.to_dict()["count"] == 2


class TestToolsView:
    def test_default(self) -> None:
        v = ToolsView()
        d = v.to_dict()
        assert d["view"] == "tools"
        assert d["total_invocations"] == 0

    def test_with_tools(self) -> None:
        v = ToolsView(tools=[{"name": "py"}], total_invocations=10)
        assert v.to_dict()["total_invocations"] == 10


class TestMemoryView:
    def test_default(self) -> None:
        v = MemoryView()
        d = v.to_dict()
        assert d["view"] == "memory"
        assert d["total_entries"] == 0

    def test_with_data(self) -> None:
        v = MemoryView(
            conversation=[{"c": 1}],
            knowledge=[{"k": 1}, {"k": 2}],
        )
        assert v.to_dict()["total_entries"] == 3


class TestArtifactView:
    def test_default(self) -> None:
        v = ArtifactView()
        d = v.to_dict()
        assert d["view"] == "artifacts"
        assert d["count"] == 0

    def test_with_artifacts(self) -> None:
        v = ArtifactView(artifacts=[{"id": "a1"}, {"id": "a2"}])
        assert v.to_dict()["count"] == 2


class TestSkillsView:
    def test_default(self) -> None:
        v = SkillsView()
        d = v.to_dict()
        assert d["view"] == "skills"
        assert d["installed_count"] == 0

    def test_with_skills(self) -> None:
        v = SkillsView(
            skills=[{"s": 1}, {"s": 2}, {"s": 3}],
            installed_count=3,
            enabled_count=2,
        )
        d = v.to_dict()
        assert d["installed_count"] == 3
        assert d["enabled_count"] == 2


class TestModelsView:
    def test_default(self) -> None:
        v = ModelsView()
        d = v.to_dict()
        assert d["view"] == "models"
        assert d["total_cost"] == 0.0

    def test_with_models(self) -> None:
        v = ModelsView(
            models=[{"m": 1}],
            total_requests=10,
            total_tokens=5000,
            total_cost=0.5,
        )
        d = v.to_dict()
        assert d["total_tokens"] == 5000


class TestPromptsView:
    def test_default(self) -> None:
        v = PromptsView()
        d = v.to_dict()
        assert d["view"] == "prompts"
        assert d["count"] == 0


class TestHealthView:
    def test_default(self) -> None:
        v = HealthView()
        d = v.to_dict()
        assert d["view"] == "health"
        assert d["overall_status"] == "unknown"

    def test_with_components(self) -> None:
        v = HealthView(
            components=[{"name": "rt", "status": "pass"}],
            overall_status="pass",
            healthy_count=1,
            unhealthy_count=0,
        )
        d = v.to_dict()
        assert d["healthy_count"] == 1

