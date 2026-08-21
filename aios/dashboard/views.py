"""Dashboard view models for all 10 views.

Each view aggregates data from the API client into a structured model
suitable for frontend rendering. No business logic — pure data shaping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatView:
    """View 1 — Chat: conversation, execution status, responses, artifacts."""

    conversation_id: str = ""
    messages: list[dict[str, Any]] = field(default_factory=list)
    execution_status: str = "idle"
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    policy_state: str = "none"

    def to_dict(self) -> dict[str, Any]:
        return {
            "view": "chat",
            "conversation_id": self.conversation_id,
            "messages": self.messages,
            "execution_status": self.execution_status,
            "artifacts": self.artifacts,
            "policy_state": self.policy_state,
        }


@dataclass
class WorkflowView:
    """View 2 — Workflow Viewer: nodes, dependencies, state, duration."""

    workflow_id: str = ""
    name: str = ""
    status: str = "unknown"
    nodes: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)
    total_duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "view": "workflow",
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status,
            "nodes": self.nodes,
            "edges": self.edges,
            "total_duration_ms": self.total_duration_ms,
        }


@dataclass
class TimelineView:
    """View 3 — Event Timeline: ordered events with timestamps."""

    events: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "view": "timeline",
            "events": self.events,
            "count": len(self.events),
        }


@dataclass
class ToolsView:
    """View 4 — Tool Usage: capability, invocations, latency, policy."""

    tools: list[dict[str, Any]] = field(default_factory=list)
    total_invocations: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "view": "tools",
            "tools": self.tools,
            "total_invocations": self.total_invocations,
        }


@dataclass
class MemoryView:
    """View 5 — Memory Viewer: 4 memory types with isolation."""

    conversation: list[dict[str, Any]] = field(default_factory=list)
    session: list[dict[str, Any]] = field(default_factory=list)
    knowledge: list[dict[str, Any]] = field(default_factory=list)
    artifact: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "view": "memory",
            "conversation": self.conversation,
            "session": self.session,
            "knowledge": self.knowledge,
            "artifact": self.artifact,
            "total_entries": (
                len(self.conversation)
                + len(self.session)
                + len(self.knowledge)
                + len(self.artifact)
            ),
        }


@dataclass
class ArtifactView:
    """View 6 — Artifact Browser: ID, type, version, checksum, provenance."""

    artifacts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "view": "artifacts",
            "artifacts": self.artifacts,
            "count": len(self.artifacts),
        }


@dataclass
class SkillsView:
    """View 7 — Skill Marketplace: installed, enabled, version, health."""

    skills: list[dict[str, Any]] = field(default_factory=list)
    installed_count: int = 0
    enabled_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "view": "skills",
            "skills": self.skills,
            "installed_count": self.installed_count,
            "enabled_count": self.enabled_count,
        }


@dataclass
class ModelsView:
    """View 8 — Model Usage: provider, tokens, cost, latency."""

    models: list[dict[str, Any]] = field(default_factory=list)
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "view": "models",
            "models": self.models,
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
        }


@dataclass
class PromptsView:
    """View 9 — Prompt Inspector: ID, version, template, variables."""

    prompts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "view": "prompts",
            "prompts": self.prompts,
            "count": len(self.prompts),
        }


@dataclass
class HealthView:
    """View 10 — Health Dashboard: component health with status normalization."""

    components: list[dict[str, Any]] = field(default_factory=list)
    overall_status: str = "unknown"
    healthy_count: int = 0
    unhealthy_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "view": "health",
            "components": self.components,
            "overall_status": self.overall_status,
            "healthy_count": self.healthy_count,
            "unhealthy_count": self.unhealthy_count,
        }
