"""Kill Switch — emergency stop (TASK-068).

Global halt mechanism, fail-closed. Integrates with Autonomy Governor (T054)
and (optionally) Autonomy Safety (T067) / Durable (T066) when present in the
workspace. No layer may ignore or skip a halt signal.
"""

from __future__ import annotations

from aios.kill_switch.contracts import (
    DrainResult,
    ExecutionContext,
    HaltResult,
    HaltSignal,
    HaltSource,
    HaltState,
    HaltScope,
    HaltViolation,
)
from aios.kill_switch.controller import KillSwitchController
from aios.kill_switch.audit import AuditLog
from aios.kill_switch.persistence import (
    DurablePersistence,
    LocalDurablePersistence,
)
from aios.kill_switch.integration import (
    GovernorHaltBridge,
    build_durable_persistence,
    build_safety_bridge,
)

__all__ = [
    "DrainResult",
    "ExecutionContext",
    "HaltResult",
    "HaltSignal",
    "HaltSource",
    "HaltState",
    "HaltScope",
    "HaltViolation",
    "KillSwitchController",
    "AuditLog",
    "DurablePersistence",
    "LocalDurablePersistence",
    "GovernorHaltBridge",
    "build_durable_persistence",
    "build_safety_bridge",
]
