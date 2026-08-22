"""SkillDistiller + Static Deploy (TASK-083, M11).

Distills a workflow / agent behavior into a reusable Skill (with a clear
contract, T064 1.0) and packages it as a self-contained static package that
can be deployed without a dynamic runtime. Built on ``aios.skill`` (T015) +
Devkit (T071) + Contract (T064) + Architecture guard (T063).

Layering: ``unknown`` (infra) layer — stdlib + ``aios.governance.architecture``
+ ``aios.skill`` + ``aios.devkit`` only.
"""

from __future__ import annotations

from .distiller import (
    DistilledSkill,
    SkillDistiller,
    StaticPackage,
    StaticDeploy,
    DistillerError,
)

__all__ = [
    "DistilledSkill",
    "SkillDistiller",
    "StaticPackage",
    "StaticDeploy",
    "DistillerError",
]
