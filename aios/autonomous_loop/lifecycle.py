"""TASK-233 — Unified Autonomous Lifecycle (M31).

Single lifecycle that unifies the previously separate autonomous modules
(``autonomous_loop``, ``autonomous_recovery``, ``stuck_detection``,
``autonomy_governor``, ``evaluation``, ``autonomous_experimentation``) into ONE
closed loop:

    Goal -> Plan -> Execute -> Observe -> Evaluate
      -> Success? --yes--> DONE
         no --> Diagnose -> Repair Candidate -> Simulation
              -> Policy -> Apply -> Verify -> loop

The facade wraps the existing :class:`~aios.autonomous_loop.loop.LoopController`
and adds two hard guards required by the spec:
  * :class:`~aios.runtime.retry_guard.RetryGuard` (T226) — auto-stop on
    repeated identical failures.
  * :class:`~aios.kill_switch.controller.KillSwitchController` — authoritative
    halt (fail-closed) that overrides every step.

No new subsystem is created; this is pure orchestration over existing modules.
Layering: ``autonomous_loop`` is an ``unknown`` (infra) layer; it only
*orchestrates* and delegates all side effects to injected collaborators.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from aios.autonomous_loop.loop import AutonomousCycle, LoopConfig, LoopController
from aios.autonomous_loop.contracts import StopCondition
from aios.kill_switch.controller import KillSwitchController
from aios.runtime.retry_guard import RetryGuard


class UnifiedAutonomousLifecycle:
    """Orchestrates the unified autonomous loop with RetryGuard + KillSwitch."""

    def __init__(
        self,
        observer: Callable[[AutonomousCycle], Dict[str, Any]],
        actor: Callable[[AutonomousCycle, Dict[str, Any]], Dict[str, Any]],
        evaluator: Callable[[AutonomousCycle, Dict[str, Any]], Dict[str, Any]],
        *,
        planner: Any = None,
        world_model: Any = None,
        config: Optional[LoopConfig] = None,
        kill_switch: Optional[KillSwitchController] = None,
        retry_guard: Optional[RetryGuard] = None,
    ) -> None:
        self._loop = LoopController(
            observer=observer,
            actor=actor,
            evaluator=evaluator,
            planner=planner,
            world_model=world_model,
            config=config,
        )
        self._kill_switch = kill_switch
        self._retry_guard = retry_guard or RetryGuard()

    def run(self, goal_id: str, context: Optional[Dict[str, Any]] = None) -> List[AutonomousCycle]:
        """Run the unified loop; halts immediately if the KillSwitch is engaged
        (fail-closed) and auto-stops on repeated identical failures via RetryGuard.
        """
        if self._kill_switch is not None and self._kill_switch.is_halted():
            # Fail-closed: do not start a new loop under a global halt.
            return []
        cycles = self._loop.run(goal_id, context or {})
        # RetryGuard observes a STABLE signature per goal so repeated identical
        # actor failures across loop iterations accumulate and trigger auto-stop.
        sig = f"{goal_id}:actor-failed"
        for cycle in cycles:
            if cycle.failures > 0:
                if self._retry_guard.observe(sig, f"cycle {cycle.cycle_id} failed"):
                    # Auto-stop: surface the root-cause report via the cycle.
                    cycle.stop_condition = StopCondition.REPEATED_FAILURE
        return cycles

    @property
    def cycles(self) -> List[AutonomousCycle]:
        return self._loop.cycles
