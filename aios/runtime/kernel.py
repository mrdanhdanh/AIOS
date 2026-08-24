"""Runtime kernel — composition & wiring of runtime services (TASK-005, M1).

The :class:`RuntimeKernel` is the single composition root for the runtime
control substrate. It instantiates the five TASK-004 services and the four
TASK-005 services and registers them in an
:class:`~aios.core.container.Container` so that later layers (orchestrator,
workers) resolve them by type without tight coupling.

Wiring honors the architecture layering (``runtime`` never imports
agent/orchestrator) and the deterministic-first rule (the policy engine decides
before the executor runs anything).

Layering: ``runtime`` layer — relative imports only.
"""

from __future__ import annotations

from typing import Any, Optional

from aios.core.config import Config
from aios.core.container import Container, Lifetime
from aios.core.events import EventBus

from aios.runtime.config_guard import require_valid_config

from aios.capability.capability import CapabilityRegistry
from aios.capability.catalog import SystemCatalog
from aios.capability.graph import KnowledgeGraph
from aios.capability.prompt import PromptRegistry

from aios.tool.registry import ToolRegistry

from aios.skill.registry import SkillRegistry
from aios.skill.resolver import SkillDependencyResolver
from aios.skill.sandbox import SandboxPool
from aios.skill.manager import SkillManager

from .artifact import ArtifactStore
from .audit import AuditTrail
from .context import ContextStore
from .execution import Executor
from .knowledge import KnowledgeIndex
from .memory import MemoryStore
from .permission import PermissionBroker
from .policy import PolicyEngine
from .resource import ResourcePool
from .scheduler import Scheduler
from .state import StateStore


__all__ = ["RuntimeKernel", "KernelError"]


class KernelError(Exception):
    """Raised on kernel wiring errors."""


def _read_real_exec_env() -> Optional[dict]:
    """Read the opt-in real-execution flag from the environment (TASK-222)."""
    import os

    if os.environ.get("AIOS_REAL_EXECUTION_ENABLED", "").lower() in {"1", "true", "yes"}:
        return {"enabled": True, "subject": "runtime", "allowed_cwd": None}
    return None


class RuntimeKernel:
    """Composition root that wires all runtime services into a Container."""

    def __init__(
        self,
        container: Optional[Container] = None,
        config: Optional[Config] = None,
        real_execution: Optional[dict] = None,
    ) -> None:
        # Fail-closed: refuse to start with an invalid configuration (T065).
        if config is not None:
            require_valid_config(config)
        self.container = container or Container()
        # TASK-222: opt-in real execution. Explicit dict wins; else env override.
        self._real_exec = real_execution or _read_real_exec_env()
        self._wire()

    def _wire(self) -> None:
        c = self.container
        # Core substrate — event bus first so all services can subscribe.
        if not c.is_registered(EventBus):
            c.register(EventBus, EventBus, Lifetime.SINGLETON)
        # TASK-004 services (singletons — shared substrate).
        c.register(ContextStore, ContextStore, Lifetime.SINGLETON)
        c.register(AuditTrail, AuditTrail, Lifetime.SINGLETON)
        c.register(ArtifactStore, ArtifactStore, Lifetime.SINGLETON)
        c.register(PermissionBroker, PermissionBroker, Lifetime.SINGLETON)
        # PolicyEngine MUST share the same broker instance as PermissionBroker
        # — otherwise grants are invisible to policy pre-checks.
        c.register(
            PolicyEngine,
            factory=lambda: PolicyEngine(broker=c.resolve(PermissionBroker)),
            lifetime=Lifetime.SINGLETON,
        )
        # TASK-005 services.
        c.register(Scheduler, Scheduler, Lifetime.SINGLETON)
        c.register(StateStore, StateStore, Lifetime.SINGLETON)
        c.register(ResourcePool, ResourcePool, Lifetime.SINGLETON)
        # TASK-007 services (memory + knowledge).
        c.register(MemoryStore, MemoryStore, Lifetime.SINGLETON)
        c.register(KnowledgeIndex, KnowledgeIndex, Lifetime.SINGLETON)
        # TASK-009 services (capability foundation — 4 singletons).
        c.register(CapabilityRegistry, CapabilityRegistry, Lifetime.SINGLETON)
        c.register(PromptRegistry, PromptRegistry, Lifetime.SINGLETON)
        c.register(SystemCatalog, SystemCatalog, Lifetime.SINGLETON)
        c.register(KnowledgeGraph, KnowledgeGraph, Lifetime.SINGLETON)
        # TASK-014 services (tool + capability router).
        c.register(ToolRegistry, ToolRegistry, Lifetime.SINGLETON)
        # TASK-015 services (skill / plugin execution — runtime layer).
        c.register(SkillRegistry, SkillRegistry, Lifetime.SINGLETON)
        c.register(
            SandboxPool,
            factory=lambda: SandboxPool(max_size=5),
            lifetime=Lifetime.SINGLETON,
        )
        c.register(
            SkillManager,
            factory=lambda: SkillManager(
                registry=c.resolve(SkillRegistry),
                resolver=SkillDependencyResolver(registry=c.resolve(SkillRegistry)),
                sandbox_pool=c.resolve(SandboxPool),
                policy_engine=c.resolve(PolicyEngine),
                permission_broker=c.resolve(PermissionBroker),
                capability_registry=c.resolve(CapabilityRegistry),
                state_store=c.resolve(StateStore),
                artifact_store=c.resolve(ArtifactStore),
                event_bus=c.resolve(EventBus),
            ),
            lifetime=Lifetime.SINGLETON,
        )
        # CapabilityRouter is at runtime layer — resolves Capability → Tool via health/priority/policy
        from .capability_router import CapabilityRouter

        c.register(
            CapabilityRouter,
            factory=lambda: CapabilityRouter(
                tool_registry=c.resolve(ToolRegistry),
                capability_registry=c.resolve(CapabilityRegistry),
                policy_engine=c.resolve(PolicyEngine),
            ),
            lifetime=Lifetime.SINGLETON,
        )
        # Executor is composed with full chain (Policy → Resource → Scheduler → State)
        # per spec §2 chain — no execution path bypasses Policy/Resource.
        c.register(
            Executor,
            factory=lambda: Executor(
                policy=c.resolve(PolicyEngine),
                audit=c.resolve(AuditTrail),
                context_store=c.resolve(ContextStore),
                event_bus=c.resolve(EventBus),
                state_store=c.resolve(StateStore),
                resource_pool=c.resolve(ResourcePool),
                scheduler=c.resolve(Scheduler),
            ),
            lifetime=Lifetime.SINGLETON,
        )
        # TASK-222: real execution support (opt-in, disabled by default).
        re_cfg = self._real_exec
        if re_cfg and re_cfg.get("enabled"):
            from .process import RealToolHandler, SCOPE_MAP
            from .permission import Permission

            _broker = c.resolve(PermissionBroker)
            _subject = re_cfg.get("subject", "runtime")
            _scopes = re_cfg.get(
                "scopes", ["process.execute", "tool:invoke", "filesystem.write"]
            )
            for _s in _scopes:
                _enum = SCOPE_MAP.get(_s)
                if _enum is None:
                    continue
                _broker.grant(_subject, Permission(_enum, re_cfg.get("resource", "*")))
            c.register(
                RealToolHandler,
                factory=lambda: RealToolHandler(
                    broker=c.resolve(PermissionBroker),
                    subject=_subject,
                    allowed_cwd=re_cfg.get("allowed_cwd"),
                ),
                lifetime=Lifetime.SINGLETON,
            )

    # ------------------------------------------------------------------ #
    @property
    def context(self) -> ContextStore:
        return self.container.resolve(ContextStore)

    @property
    def audit(self) -> AuditTrail:
        return self.container.resolve(AuditTrail)

    @property
    def artifacts(self) -> ArtifactStore:
        return self.container.resolve(ArtifactStore)

    @property
    def permissions(self) -> PermissionBroker:
        return self.container.resolve(PermissionBroker)

    @property
    def policy(self) -> PolicyEngine:
        return self.container.resolve(PolicyEngine)

    @property
    def scheduler(self) -> Scheduler:
        return self.container.resolve(Scheduler)

    @property
    def state(self) -> StateStore:
        return self.container.resolve(StateStore)

    @property
    def resources(self) -> ResourcePool:
        return self.container.resolve(ResourcePool)

    @property
    def bus(self) -> EventBus:
        return self.container.resolve(EventBus)

    @property
    def executor(self) -> Executor:
        return self.container.resolve(Executor)

    @property
    def memory(self) -> MemoryStore:
        return self.container.resolve(MemoryStore)

    @property
    def knowledge(self) -> KnowledgeIndex:
        return self.container.resolve(KnowledgeIndex)

    @property
    def capabilities(self) -> CapabilityRegistry:
        return self.container.resolve(CapabilityRegistry)

    @property
    def prompts(self) -> PromptRegistry:
        return self.container.resolve(PromptRegistry)

    @property
    def catalog(self) -> SystemCatalog:
        return self.container.resolve(SystemCatalog)

    @property
    def graph(self) -> KnowledgeGraph:
        return self.container.resolve(KnowledgeGraph)

    @property
    def tools(self) -> ToolRegistry:
        return self.container.resolve(ToolRegistry)

    @property
    def skills(self) -> SkillRegistry:
        return self.container.resolve(SkillRegistry)

    @property
    def sandbox_pool(self) -> SandboxPool:
        return self.container.resolve(SandboxPool)

    @property
    def skill_manager(self) -> SkillManager:
        return self.container.resolve(SkillManager)

    @property
    def router(self) -> Any:
        from .capability_router import CapabilityRouter

        return self.container.resolve(CapabilityRouter)

    @property
    def real_tool_handler(self) -> Any:
        """Resolve the real execution handler (only registered when enabled)."""
        from .process import RealToolHandler

        return self.container.resolve(RealToolHandler)

    def execute_plan(
        self,
        plan: Any,
        *,
        subject: str = "runtime",
        timeout: float = 30.0,
        max_attempts: int = 1,
        cancel_event: Any = None,
    ) -> Any:
        """Execute *plan* via the real tool handler (TASK-222).

        Raises :class:`KernelError` if real execution is not enabled.
        """
        if not (self._real_exec and self._real_exec.get("enabled")):
            raise KernelError(
                "real execution is disabled; set real_execution.enabled=true "
                "in configs/default.yaml or AIOS_REAL_EXECUTION_ENABLED=1"
            )
        handler = self.real_tool_handler
        return self.executor.execute(
            plan,
            handler,
            timeout=timeout,
            max_attempts=max_attempts,
            cancel_event=cancel_event,
        )

    # ------------------------------------------------------------------ #
    def health(self) -> dict:
        """Lightweight health snapshot of the wired services."""
        return {
            "context": len(self.context),
            "audit_events": len(self.audit),
            "artifacts": len(self.artifacts),
            "scheduler_pending": len(self.scheduler),
            "state_checkpoints": len(self.state),
            "resources_registered": len(self.resources._capacity),
            "memory_entries": len(self.memory),
            "memory_active": len(self.memory.list_active()),
            "knowledge_docs": len(self.knowledge),
            "knowledge_chunks": self.knowledge.chunk_count,
            "knowledge_sources": self.knowledge.source_count,
            "capabilities": len(self.capabilities),
            "prompts": len(self.prompts),
            "catalog_entries": len(self.catalog),
            "graph_nodes": self.graph.node_count,
            "graph_edges": self.graph.edge_count,
            "tools": len(self.tools),
            "skills_registered": len(self.skills),
            "sandbox_pool_size": len(self.sandbox_pool),
            "bus_registered": True,
        }
