"""Safe-Stop policy (TASK-067).

On a boundary violation, emit a fail-closed ``SAFE_STOP`` signal. If a Kill
Switch (T068) hook is provided it is invoked with the signal; otherwise the
``SafeStopSignal`` type defined in ``contracts`` is the canonical fail-closed
signal. Integration points with T055 (Recovery) and T061 (Stuck) are provided
so a safe-stop aligns with the existing recovery/stuck vocabularies.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from aios.autonomous_recovery.contracts import RecoveryStrategy
from aios.stuck_detection.contracts import StuckSignal
from aios.autonomy_safety.contracts import (
    AutonomyContext,
    SafeStopSignal,
    SafetyDecision,
)


class SafeStopPolicy:
    """Fail-closed safe-stop emitter.

    Parameters
    ----------
    kill_switch:
        Optional hook ``Callable[[SafeStopSignal], Any]`` supplied by the Kill
        Switch (T068) once available. If it raises, the stop still stands
        (fail-closed) — the signal is always recorded.
    """

    def __init__(
        self,
        kill_switch: Optional[Callable[[SafeStopSignal], Any]] = None,
    ) -> None:
        self._kill_switch = kill_switch
        self._last_signal: Optional[SafeStopSignal] = None

    def trigger(
        self,
        context: AutonomyContext,
        action: str,
        reason: str,
        goal: str = "",
        loop: str = "",
    ) -> SafeStopSignal:
        """Emit a fail-closed SAFE_STOP signal for a boundary violation."""
        signal = SafeStopSignal(
            goal=goal,
            loop=loop,
            reason=reason,
            violated_action=action,
            context_level=context.level.value,
            evidence_ref=context.evidence_ref,
        )
        self._last_signal = signal
        if self._kill_switch is not None:
            try:
                self._kill_switch(signal)
            except Exception:
                # Fail-closed: even if the kill switch hook errors, the signal
                # is recorded and the stop stands.
                pass
        return signal

    def recovery_strategy(self) -> RecoveryStrategy:
        """The recovery strategy a safe-stop maps to (T055 alignment)."""
        return RecoveryStrategy.SAFE_STOP

    def from_stuck_signal(
        self,
        context: AutonomyContext,
        signal: StuckSignal,
        goal: str = "",
        loop: str = "",
    ) -> SafeStopSignal:
        """Trigger safe-stop from a detected stuck signal (T061 integration)."""
        return self.trigger(
            context=context,
            action=f"stuck:{signal.kind.value}",
            reason=f"stuck_detected:{signal.kind.value}:{signal.severity.value}",
            goal=goal,
            loop=loop,
        )

    @property
    def last_signal(self) -> Optional[SafeStopSignal]:
        return self._last_signal
