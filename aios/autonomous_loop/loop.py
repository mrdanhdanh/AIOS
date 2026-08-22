"""Autonomous Loop engine (TASK-053).

Coordinates a closed control loop over autonomous primitives. The controller
only *orchestrates*; it never directly executes tools or runtime operations.
All side-effecting steps are delegated to injected collaborators (actor /
observer / evaluator) that themselves go through Policy/Permission/Runtime.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from aios.autonomous_loop.contracts import (
    AutonomousCycle,
    CandidateLearning,
    CycleStatus,
    Decision,
    StopCondition,
)


@dataclass
class LoopConfig:
    max_iterations: int = 20
    max_cost: float = 1.0
    max_runtime_seconds: float = 1800.0
    max_failures: int = 5
    no_progress_threshold: int = 3


@dataclass
class CycleResult:
    cycle: AutonomousCycle
    learning: CandidateLearning | None = None
    observation: dict[str, Any] | None = None
    evaluation: dict[str, Any] | None = None


class LoopController:
    """Drives the autonomous cycle lifecycle."""

    def __init__(
        self,
        observer: Callable[[AutonomousCycle], dict[str, Any]],
        actor: Callable[[AutonomousCycle, dict[str, Any]], dict[str, Any]],
        evaluator: Callable[[AutonomousCycle, dict[str, Any]], dict[str, Any]],
        planner: Any = None,
        world_model: Any = None,
        config: LoopConfig | None = None,
    ) -> None:
        self._observer = observer
        self._actor = actor
        self._evaluator = evaluator
        self._planner = planner
        self._world_model = world_model
        self._config = config or LoopConfig()
        self._cycles: list[AutonomousCycle] = []
        self._total_cost: float = 0.0
        self._total_failures: int = 0

    def run(self, goal_id: str, context: dict[str, Any] | None = None) -> list[AutonomousCycle]:
        context = context or {}
        parent_id = ""
        start = time.time()
        no_progress_streak = 0
        last_progress = 0.0
        while True:
            cycle = self._run_one(goal_id, parent_id, context)
            self._cycles.append(cycle)
            parent_id = cycle.cycle_id

            if cycle.status == CycleStatus.STOPPED or cycle.decision == Decision.STOP:
                break
            if cycle.status == CycleStatus.COMPLETED:
                break
            if cycle.status == CycleStatus.FAILED:
                break

            # Stop-condition checks (deterministic). Use loop-level
            # accumulators, not per-cycle values.
            if cycle.iteration >= self._config.max_iterations:
                cycle.status = CycleStatus.STOPPED
                cycle.stop_condition = StopCondition.MAX_ITERATIONS
                break
            if self._total_cost > self._config.max_cost:
                cycle.status = CycleStatus.STOPPED
                cycle.stop_condition = StopCondition.MAX_COST
                break
            if time.time() - start > self._config.max_runtime_seconds:
                cycle.status = CycleStatus.STOPPED
                cycle.stop_condition = StopCondition.MAX_RUNTIME
                break
            if self._total_failures >= self._config.max_failures:
                cycle.status = CycleStatus.STOPPED
                cycle.stop_condition = StopCondition.REPEATED_FAILURE
                break
            if cycle.progress > last_progress + 1e-9:
                last_progress = cycle.progress
                no_progress_streak = 0
            else:
                no_progress_streak += 1
                if no_progress_streak >= self._config.no_progress_threshold:
                    cycle.status = CycleStatus.STOPPED
                    cycle.stop_condition = StopCondition.NO_PROGRESS
                    break
            if cycle.decision == Decision.WAIT:
                cycle.status = CycleStatus.WAITING
                break
        return self._cycles

    def _run_one(self, goal_id: str, parent_id: str, context: dict[str, Any]) -> AutonomousCycle:
        cycle = AutonomousCycle(goal_id=goal_id, parent_cycle_id=parent_id)
        cycle.iteration = len(self._cycles) + 1
        cycle.status = CycleStatus.OBSERVING
        observation = self._observer(cycle)
        cycle.observation_ref = observation.get("observation_id", "")

        cycle.status = CycleStatus.PLANNING
        # Planning is delegated to the planner if available; otherwise the
        # controller reuses the context plan.
        if self._planner is not None and "plan" in context:
            pass  # planner invoked by caller-supplied actor path

        cycle.status = CycleStatus.VALIDATING
        # Validation is the responsibility of the planner/validator; the loop
        # only proceeds if the actor accepts the step.

        cycle.status = CycleStatus.ACTING
        execution = self._actor(cycle, context)
        cycle.execution_ref = execution.get("execution_id", "")
        if execution.get("failed"):
            cycle.failures += 1
            self._total_failures += 1
        self._total_cost += float(execution.get("cost", 0.0))
        cycle.cost = self._total_cost

        cycle.status = CycleStatus.OBSERVING
        post_observation = self._observer(cycle)
        cycle.progress = post_observation.get("progress", cycle.progress)
        cycle.cost += float(execution.get("cost", 0.0))

        cycle.status = CycleStatus.EVALUATING
        evaluation = self._evaluator(cycle, execution)
        cycle.evaluation_ref = evaluation.get("evaluation_id", "")
        verdict = evaluation.get("verdict", "inconclusive")

        cycle.status = CycleStatus.LEARNING
        learning = CandidateLearning(
            goal_id=goal_id,
            observation=post_observation,
            lesson=evaluation.get("lesson", ""),
        )
        # Candidate only — never auto-promoted (spec §2.5).

        cycle.status = CycleStatus.DECIDING
        decision = self._decide(cycle, verdict, evaluation)
        cycle.decision = decision
        if decision == Decision.REPLAN:
            cycle.status = CycleStatus.REPLANNING
        elif decision == Decision.STOP:
            cycle.status = CycleStatus.STOPPED
            if evaluation.get("policy_denied"):
                cycle.stop_condition = StopCondition.POLICY_DENIED
            elif evaluation.get("safety_block"):
                cycle.stop_condition = StopCondition.SAFETY_BLOCK
            else:
                cycle.stop_condition = StopCondition.GOAL_COMPLETED
        elif decision == Decision.CONTINUE:
            if cycle.progress >= 1.0:
                cycle.status = CycleStatus.COMPLETED
                cycle.stop_condition = StopCondition.GOAL_COMPLETED
        cycle.completed_at = time.time()
        return cycle

    def _decide(self, cycle: AutonomousCycle, verdict: str, evaluation: dict[str, Any]) -> Decision:
        if evaluation.get("policy_denied") or evaluation.get("safety_block"):
            return Decision.STOP
        if verdict == "pass":
            return Decision.CONTINUE
        if verdict == "fail":
            return Decision.REPLAN if cycle.failures < self._config.max_failures else Decision.STOP
        if verdict == "warning":
            return Decision.CONTINUE if evaluation.get("minor") else Decision.REPLAN
        # inconclusive / unknown -> do not auto-promote; wait for human/replan
        return Decision.WAIT if evaluation.get("await_input") else Decision.REPLAN

    @property
    def cycles(self) -> list[AutonomousCycle]:
        return list(self._cycles)


class AutonomousLoop(LoopController):
    """Public entry point for the autonomous control loop (alias)."""

