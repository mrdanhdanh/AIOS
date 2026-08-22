"""Autonomy Level Registry (TASK-067).

Assigns and retrieves the autonomy level per goal/loop. Raising a level
requires a policy (and, for the highest levels, an explicit human-approval
flag). Silent elevation is rejected — this is the core control that prevents
unbounded autonomy creep.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from aios.autonomy_safety.contracts import AutonomyContext, AutonomyLevel


# Levels that require explicit human approval to reach.
_HUMAN_APPROVAL_REQUIRED = {AutonomyLevel.L3, AutonomyLevel.L4}


@dataclass
class LevelPolicy:
    """Policy governing a level change.

    ``requires_human_approval`` must be set for levels that demand human sign-off
    (L3/L4). ``justification`` and ``approved_by`` provide provenance.
    """

    requires_human_approval: bool = False
    justification: str = ""
    approved_by: str = ""


class AutonomyLevelRegistry:
    """Maps goal/loop keys to their ``AutonomyContext`` (and thus level)."""

    def __init__(self) -> None:
        self._contexts: dict[str, AutonomyContext] = {}

    def assign(self, key: str, context: AutonomyContext) -> None:
        """Assign an autonomy context (with its level) to a goal/loop key."""
        self._contexts[key] = context

    def get(self, key: str) -> Optional[AutonomyContext]:
        return self._contexts.get(key)

    def keys(self) -> list[str]:
        return list(self._contexts.keys())

    def raise_level(
        self,
        key: str,
        target: AutonomyLevel,
        policy: Optional[LevelPolicy] = None,
    ) -> bool:
        """Raise the autonomy level for ``key``.

        Rejects silent elevation: a ``policy`` must be supplied, and if the
        target level requires human approval the policy must carry the approval
        flag. Returns ``True`` on success, ``False`` if rejected.
        """
        ctx = self._contexts.get(key)
        if ctx is None:
            return False
        # Silent elevation rejected: no policy provided.
        if policy is None:
            return False
        # Target requires human approval but policy lacks it.
        if target in _HUMAN_APPROVAL_REQUIRED and not policy.requires_human_approval:
            return False
        # Apply the (validated) level change.
        ctx.level = target
        return True

    def lower_level(self, key: str, target: AutonomyLevel) -> bool:
        """Lower the autonomy level for ``key`` (always permitted)."""
        ctx = self._contexts.get(key)
        if ctx is None:
            return False
        if target.rank < ctx.level.rank:
            ctx.level = target
            return True
        return False
