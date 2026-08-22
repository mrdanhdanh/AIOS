"""Integration bridges for Kill Switch (TASK-068).

Integrates with Autonomy Governor (T054). Autonomy Safety (T067) and Durable
(T066) are not yet present in this workspace; optional bridges fall back to
local implementations so the package imports cleanly and the kill switch still
works fail-closed.
"""

from __future__ import annotations

from typing import Any, Optional

from aios.autonomy_governor.contracts import AutonomyDecision
from aios.autonomy_governor.governor import ActionContext, AutonomyGovernor

from aios.kill_switch.contracts import HaltScope, HaltViolation
from aios.kill_switch.controller import KillSwitchController
from aios.kill_switch.persistence import DurablePersistence, LocalDurablePersistence


class GovernorHaltBridge:
    """Wraps an ``AutonomyGovernor`` so every gated action respects the kill switch.

    Fail-closed: if the kill switch is halted for the relevant scope, the bridge
    returns ``BLOCK`` without consulting the governor.
    """

    def __init__(self, controller: KillSwitchController, governor: AutonomyGovernor) -> None:
        self._controller = controller
        self._governor = governor

    def gate(self, ctx: ActionContext) -> AutonomyDecision:
        if self._controller.is_halted():
            return AutonomyDecision.BLOCK
        return self._governor.decide(ctx)

    def gate_scoped(
        self, ctx: ActionContext, scope: HaltScope, target_id: str = ""
    ) -> AutonomyDecision:
        if self._controller.is_halted(scope, target_id):
            return AutonomyDecision.BLOCK
        return self._governor.decide(ctx)


def build_durable_persistence() -> DurablePersistence:
    """Return a durable persistence backend.

    Prefers TASK-066 ``aios.durable`` if available; otherwise the local
    in-memory fallback.
    """
    try:
        from aios.durable import DurableStore  # type: ignore  # noqa: F401

        return DurableStore()  # pragma: no cover - not present in this workspace
    except Exception:  # noqa: BLE001
        return LocalDurablePersistence()


def build_safety_bridge(controller: KillSwitchController) -> Any:
    """Return an Autonomy Safety (T067) bridge if available, else a local stub."""
    try:
        from aios.autonomy_safety import SafetyMonitor  # type: ignore  # noqa: F401

        return SafetyMonitor(kill_switch=controller)  # pragma: no cover
    except Exception:  # noqa: BLE001
        return _LocalSafetyStub(controller)


class _LocalSafetyStub:
    """Local stand-in for TASK-067 Autonomy Safety (not yet implemented)."""

    def __init__(self, controller: KillSwitchController) -> None:
        self._controller = controller

    def is_safe(self) -> bool:
        # When halted, the system is in a safe (stopped) state.
        return self._controller.is_halted()
