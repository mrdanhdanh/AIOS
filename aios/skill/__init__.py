"""Skill / Plugin Execution — M2 P4 (TASK-015).

Skill is an extension, not part of Core. It declares capabilities,
permissions and resources; Runtime/Policy enforces them. Lifecycle is
deterministic, dependency-resolved, persistent and sandbox-isolated.

Layering: ``skill`` layer — contracts/registry/resolver are pure
(stdlib + ``aios.core`` only). Manager and SandboxPool are orchestration
components that integrate with Runtime/Capability/Policy via injection.

Public re-exports for convenience.
"""

from .contracts import (
    SKILL_CONTRACT,
    SkillContract,
    SkillDependency,
    SkillError,
    SkillPersistentState,
    SkillStatus,
    SkillTransition,
    check_skill_contracts,
)
from .registry import SkillRegistry
from .resolver import SkillDependencyResolver, ResolverError
from .sandbox import Sandbox, SandboxPool, SandboxStatus

__all__ = [
    "SKILL_CONTRACT",
    "SkillContract",
    "SkillDependency",
    "SkillError",
    "SkillPersistentState",
    "SkillStatus",
    "SkillTransition",
    "check_skill_contracts",
    "SkillRegistry",
    "SkillDependencyResolver",
    "ResolverError",
    "Sandbox",
    "SandboxPool",
    "SandboxStatus",
]
