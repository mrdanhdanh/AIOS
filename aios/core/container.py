"""Dependency Injection container with singleton / scoped / transient lifetimes.

Thread-safe via a :class:`threading.Lock` on resolution paths.

Example::

    from aios.core.container import Container, Lifetime

    container = Container()
    container.register(Config, Config, Lifetime.SCOPED)

    with container.create_scope() as scope:
        cfg = scope.resolve(Config)
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, TypeVar

__all__ = ["Container", "Lifetime", "Scope", "ContainerError"]

T = TypeVar("T")


class ContainerError(Exception):
    """Raised on DI container errors."""


class Lifetime(Enum):
    """Service lifetime."""

    SINGLETON = "singleton"
    SCOPED = "scoped"
    TRANSIENT = "transient"


class _Registration:
    """Internal registration record."""

    __slots__ = ("service_type", "implementation", "factory", "lifetime")

    def __init__(
        self,
        service_type: type,
        implementation: Optional[type],
        factory: Optional[Callable[..., Any]],
        lifetime: Lifetime,
    ) -> None:
        self.service_type = service_type
        self.implementation = implementation
        self.factory = factory
        self.lifetime = lifetime

    def create(self, scope: "Scope") -> Any:
        if self.factory is not None:
            return self.factory()
        if self.implementation is not None:
            return self.implementation()
        raise ContainerError(
            f"No factory or implementation for {self.service_type.__name__}"
        )


class Scope:
    """Resolution scope — tracks scoped instances."""

    def __init__(self, container: "Container") -> None:
        self._container = container
        self._scoped_instances: Dict[type, Any] = {}
        self._lock = threading.RLock()

    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service by its registered type."""
        return self._container._resolve_in_scope(self, service_type)


class Container:
    """DI container with singleton / scoped / transient lifetimes.

    Thread-safe: resolution is guarded by a lock.
    """

    def __init__(self) -> None:
        self._registrations: Dict[type, _Registration] = {}
        self._singletons: Dict[type, Any] = {}
        # RLock (reentrant) so a factory may resolve other registered
        # services without deadlocking on nested resolution.
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------
    def register(
        self,
        service_type: Type[T],
        implementation: Optional[type] = None,
        lifetime: Lifetime = Lifetime.SINGLETON,
        factory: Optional[Callable[..., Any]] = None,
    ) -> None:
        """Register a service.

        *service_type* is the key (typically an interface or base class).
        *implementation* is the concrete class.  Alternatively, *factory*
        is a callable that produces instances.
        """
        if factory is None and implementation is None:
            raise ContainerError(
                "Either implementation or factory must be provided"
            )
        with self._lock:
            self._registrations[service_type] = _Registration(
                service_type=service_type,
                implementation=implementation,
                factory=factory,
                lifetime=lifetime,
            )

    def unregister(self, service_type: type) -> None:
        """Remove a registration."""
        with self._lock:
            self._registrations.pop(service_type, None)
            self._singletons.pop(service_type, None)

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve from the root (singleton) scope."""
        return self._resolve_in_scope(None, service_type)

    def _resolve_in_scope(
        self, scope: Optional[Scope], service_type: Type[T]
    ) -> T:
        with self._lock:
            reg = self._registrations.get(service_type)
            if reg is None:
                raise ContainerError(
                    f"No registration for {service_type.__name__}"
                )

            if reg.lifetime == Lifetime.SINGLETON:
                if service_type not in self._singletons:
                    self._singletons[service_type] = reg.create(
                        scope or Scope(self)
                    )
                return self._singletons[service_type]  # type: ignore[return-value]

            if reg.lifetime == Lifetime.SCOPED:
                if scope is None:
                    raise ContainerError(
                        f"Scoped service {service_type.__name__} requires a scope"
                    )
                if service_type not in scope._scoped_instances:
                    scope._scoped_instances[service_type] = reg.create(scope)
                return scope._scoped_instances[service_type]  # type: ignore[return-value]

            # TRANSIENT
            return reg.create(scope or Scope(self))  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Scope management
    # ------------------------------------------------------------------
    @contextmanager
    def create_scope(self):
        """Create a new resolution scope."""
        scope = Scope(self)
        try:
            yield scope
        finally:
            scope._scoped_instances.clear()

    # Alias required by M1 canonical spec: container must expose register/resolve/scope
    @contextmanager
    def scope(self):
        """Alias for :meth:`create_scope` (canonical name per TASK-003 spec)."""
        with self.create_scope() as s:
            yield s

    # ------------------------------------------------------------------
    def is_registered(self, service_type: type) -> bool:
        """Return True if *service_type* has a registration."""
        return service_type in self._registrations
