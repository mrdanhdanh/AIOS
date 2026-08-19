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

from .artifact import ArtifactStore
from .audit import AuditTrail
from .context import ContextStore
from .execution import Executor
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
        # TASK-004 services (singletons — shared substrate).
        c.register(ContextStore, ContextStore, Lifetime.SINGLETON)
        c.register(AuditTrail, AuditTrail, Lifetime.SINGLETON)
        c.register(ArtifactStore, ArtifactStore, Lifetime.SINGLETON)
        c.register(PermissionBroker, PermissionBroker, Lifetime.SINGLETON)
        c.register(PolicyEngine, PolicyEngine, Lifetime.SINGLETON)
        # TASK-005 services.
        c.register(Scheduler, Scheduler, Lifetime.SINGLETON)
        c.register(StateStore, StateStore, Lifetime.SINGLETON)
        c.register(ResourcePool, ResourcePool, Lifetime.SINGLETON)
        # Executor depends on the wired policy/audit/context services.
        c.register(
            Executor,
            factory=lambda: Executor(
                policy=c.resolve(PolicyEngine),
                audit=c.resolve(AuditTrail),
                context_store=c.resolve(ContextStore),
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
    def executor(self) -> Executor:
        return self.container.resolve(Executor)

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
        }
