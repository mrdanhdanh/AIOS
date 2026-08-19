"""AIOS core package — contracts, config, logging, metadata, healthcheck.

Public API (TASK-002 + TASK-003)::

    from aios.core.config import Config, ConfigError
    from aios.core.logging import setup_logging, get_logger
    from aios.core.metadata import PackageMetadata, BuildInfo
    from aios.core.healthcheck import HealthCheck, HealthResult, HealthStatus
    from aios.core.version import SemVer, VersionError
    from aios.core.contracts import Contract, ContractError, check_compatibility
    from aios.core.container import Container, Lifetime, Scope, ContainerError
    from aios.core.events import EventBus, Event
    from aios.core.planner import ExecutionPlan, Step, StepStatus, PlanError

Layering: ``agent -> orchestrator -> runtime -> capability -> tool``.
"""

from .config import Config, ConfigError
from .metadata import PackageMetadata, BuildInfo
from .healthcheck import HealthCheck, HealthResult, HealthStatus
from .version import SemVer, VersionError
from .contracts import Contract, ContractError, check_compatibility
from .container import Container, Lifetime, Scope, ContainerError
from .events import EventBus, Event
from .planner import ExecutionPlan, Step, StepStatus, PlanError

__all__ = [
    "Config",
    "ConfigError",
    "PackageMetadata",
    "BuildInfo",
    "HealthCheck",
    "HealthResult",
    "HealthStatus",
    "SemVer",
    "VersionError",
    "Contract",
    "ContractError",
    "check_compatibility",
    "Container",
    "Lifetime",
    "Scope",
    "ContainerError",
    "EventBus",
    "Event",
    "ExecutionPlan",
    "Step",
    "StepStatus",
    "PlanError",
]
