"""API schemas — Pydantic v2 contracts for REST boundary (TASK-017).

Layering: ``api`` layer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

from aios.core.version import SemVer, VersionError

T = TypeVar("T")
API_VERSION = "1.0.0"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Pagination ────────────────────────────────────────────────────────

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(default_factory=list)
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    has_next: bool = False
    version: str = Field(default=API_VERSION)


class ApiResponse(BaseModel, Generic[T]):
    data: T
    version: str = Field(default=API_VERSION)


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: str


# ── Health / System ──────────────────────────────────────────────────

class ProbeSchema(BaseModel):
    name: str
    healthy: bool
    message: str = ""


class HealthResponse(BaseModel):
    status: str
    probes: List[ProbeSchema] = Field(default_factory=list)
    version: str = Field(default=API_VERSION)
    timestamp: str = Field(default_factory=_now)


class SystemInfoResponse(BaseModel):
    version: str = Field(default="0.2.0")
    health: HealthResponse
    kernel_stats: Dict[str, Any] = Field(default_factory=dict)


# ── Execution ────────────────────────────────────────────────────────

class ExecutionCreateRequest(BaseModel):
    workflow: Optional[str] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    context_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResponse(BaseModel):
    execution_id: str
    status: str
    workflow: Optional[str] = None
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    step_status: Dict[str, str] = Field(default_factory=dict)


# ── Workflow ─────────────────────────────────────────────────────────

class WorkflowCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    version: str = "1.0.0"
    description: str = ""
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    retries: int = Field(default=0, ge=0)
    timeout: int = Field(default=300, ge=1)


class WorkflowResponse(BaseModel):
    workflow_id: str
    name: str
    version: str
    description: str = ""
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ── Task ─────────────────────────────────────────────────────────────

class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = ""
    goal_id: Optional[str] = None
    priority: str = "NORMAL"
    dependencies: List[str] = Field(default_factory=list)
    workflow_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    task_id: str
    title: str
    description: str = ""
    status: str
    priority: str
    goal_id: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ── Agent ────────────────────────────────────────────────────────────

class AgentResponse(BaseModel):
    agent_id: str
    agent_type: str
    status: str
    health: str = "UNKNOWN"
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ── Capability ───────────────────────────────────────────────────────

class CapabilityCreateRequest(BaseModel):
    capability_id: str = Field(min_length=1)
    version: str = "1.0.0"
    description: str = ""
    permissions: List[str] = Field(default_factory=list)
    resources: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class CapabilityResponse(BaseModel):
    capability_id: str
    version: str
    description: str = ""
    permissions: List[str] = Field(default_factory=list)
    resources: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now)


# ── Tool ─────────────────────────────────────────────────────────────

class ToolCreateRequest(BaseModel):
    tool_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    version: str = "1.0.0"
    tool_type: str = "python"
    description: str = ""
    capabilities: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    resources: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=0, ge=0)


class ToolResponse(BaseModel):
    tool_id: str
    name: str
    version: str
    tool_type: str
    description: str = ""
    capabilities: List[str] = Field(default_factory=list)
    health: str = "healthy"
    priority: int = 0
    enabled: bool = True
    created_at: str = Field(default_factory=_now)


# ── Skill ────────────────────────────────────────────────────────────

class SkillCreateRequest(BaseModel):
    skill_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    dependencies: List[Dict[str, str]] = Field(default_factory=list)
    required_capabilities: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    resources: Dict[str, Any] = Field(default_factory=dict)
    runtime: str = "python"
    entrypoint: str = "main.py"


class SkillResponse(BaseModel):
    skill_id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    status: str = "pending"
    enabled: bool = False
    required_capabilities: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now)


# ── Memory ───────────────────────────────────────────────────────────

class MemoryCreateRequest(BaseModel):
    memory_type: str
    scope_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    producer: str = ""
    source: str = ""
    task_id: str = ""
    run_id: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryResponse(BaseModel):
    entry_id: str
    memory_type: str
    scope_id: str
    content: str
    content_hash: str
    producer: str = ""
    source: str = ""
    status: str = "active"
    created_at: str = Field(default_factory=_now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ── Artifact ─────────────────────────────────────────────────────────

class ArtifactCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    content: str = Field(min_length=1)
    content_type: str = "application/octet-stream"
    version: str = "0.1.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ArtifactResponse(BaseModel):
    artifact_id: str
    name: str
    content_type: str
    version: str
    checksum: str
    created_at: str = Field(default_factory=_now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ── Model ────────────────────────────────────────────────────────────

class ModelResponse(BaseModel):
    model_id: str
    provider: str
    display_name: str = ""
    capabilities: List[str] = Field(default_factory=list)
    offline: bool = False
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


# ── Prompt ───────────────────────────────────────────────────────────

class PromptCreateRequest(BaseModel):
    prompt_id: str = Field(min_length=1)
    version: str = "1.0.0"
    template: str = Field(min_length=1)
    description: str = ""


class PromptResponse(BaseModel):
    prompt_id: str
    version: str
    template: str
    variables: List[str] = Field(default_factory=list)
    description: str = ""
    created_at: str = Field(default_factory=_now)


# ── Event ────────────────────────────────────────────────────────────

class EventPublishRequest(BaseModel):
    event_type: str = Field(min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)
    source: str = "api"


class EventResponse(BaseModel):
    event_id: str
    event_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=_now)
    version: str = API_VERSION
    source: str = "api"


# ── Orchestrator ─────────────────────────────────────────────────────

class OrchestratorDecideRequest(BaseModel):
    text: str = Field(min_length=1)
    context_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OrchestratorDecideResponse(BaseModel):
    plan_id: str
    source: str
    llm_call_count: int = 0
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)
