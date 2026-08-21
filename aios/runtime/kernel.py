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

from typing import Optional

from aios.core.container import Container, Lifetime
from aios.core.events import EventBus

from aios.capability.capability import CapabilityRegistry
from aios.capability.catalog import SystemCatalog
from aios.capability.graph import KnowledgeGraph
from aios.capability.prompt import PromptRegistry

from aios.tool.registry import ToolRegistry

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


class RuntimeKernel:
    """Composition root that wires all runtime services into a Container."""

    def __init__(self, container: Optional[Container] = None) -> None:
        self.container = container or Container()
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
    def router(self) -> Any:
        from .capability_router import CapabilityRouter

        return self.container.resolve(CapabilityRouter)

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
            "bus_registered": True,
        }
