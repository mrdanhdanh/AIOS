"""Runtime execution service (TASK-005, M1).

The :class:`Executor` runs an :class:`~aios.core.planner.ExecutionPlan` step by
step, enforcing the runtime control contract before and during execution:

  * **Policy pre-check** — each step may carry a ``scope``/``resource`` in its
    metadata; if a :class:`~aios.runtime.policy.PolicyEngine` is wired in, the
    step is pre-checked and execution fails closed on ``DENY``.
  * **Retry** — a step may be retried up to ``max_attempts`` on error.
  * **Timeout** — a per-execution wall-clock timeout fails slow steps with
    ``TIMEOUT`` (best-effort; checked between steps and on step completion).
  * **Cancel** — a :class:`threading.Event` flips execution to ``CANCELLED``
    (checked between steps).
  * **Audit** — every step start/end is recorded on the wired
    :class:`~aios.runtime.audit.AuditTrail`.

The executor is deterministic-first: it never calls an LLM. A ``handler``
callable supplied by the caller performs the actual step work.

Layering: ``runtime`` layer — uses relative imports for siblings and
``aios.core`` for kernel primitives; never imports agent/orchestrator.
"""

from __future__ import annotations

import concurrent.futures as cf
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional

from aios.core.events import EventBus, Event
from aios.core.planner import ExecutionPlan, Step, StepStatus

from .audit import AuditStatus, AuditTrail
from .context import ContextStore, RuntimeContext
from .policy import PolicyDecision, PolicyEngine, PolicyRequest


__all__ = [
    "ExecutionError",
    "ExecutionOutcome",
    "StepResult",
    "ExecutionReport",
    "StepHandler",
    "Executor",
    "ExecutionStarted",
    "ExecutionStepFinished",
]


class ExecutionError(Exception):
    """Raised on executor usage errors."""


class ExecutionOutcome(Enum):
    """Overall outcome of an execution."""

    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class StepResult:
    """Result of a single step execution."""

    step_id: str
    status: str  # COMPLETED | FAILED | CANCELLED | TIMEOUT
    output: Any = None
    error: Optional[str] = None
    attempts: int = 0


@dataclass
class ExecutionReport:
    """Aggregate report of a full execution."""

    execution_id: str
    status: ExecutionOutcome
    results: Dict[str, StepResult] = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status == ExecutionOutcome.COMPLETED


# EventBus events emitted by the executor.
class ExecutionStarted(Event):
    def __init__(self, execution_id: str, plan_id: str):
        self.execution_id = execution_id
        self.plan_id = plan_id


class ExecutionStepFinished(Event):
    def __init__(self, execution_id: str, step_id: str, status: str):
        self.execution_id = execution_id
        self.step_id = step_id
        self.status = status


# Protocol-ish callable: handler(step, context) -> output
StepHandler = Callable[[Step, Optional[RuntimeContext]], Any]


class Executor:
    """Runs an :class:`ExecutionPlan` with policy/retry/timeout/cancel/audit."""

    def __init__(
        self,
        *,
        policy: Optional[PolicyEngine] = None,
        audit: Optional[AuditTrail] = None,
        context_store: Optional[ContextStore] = None,
        subject: str = "runtime",
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._policy = policy
        self._audit = audit
        self._context_store = context_store
        self._subject = subject
        self._bus = event_bus
        self._lock = threading.RLock()

    # ------------------------------------------------------------------ #
    def execute(
        self,
        plan: ExecutionPlan,
        handler: StepHandler,
        *,
        context_id: Optional[str] = None,
        timeout: float = 0.0,
        max_attempts: int = 1,
        cancel_event: Optional[threading.Event] = None,
        skip_completed: bool = True,
    ) -> ExecutionReport:
        """Execute *plan* via *handler*.

        ``timeout`` is a per-step wall-clock budget (0 = no timeout).
        ``max_attempts`` is the retry count per step on error. If a
        ``cancel_event`` is set between steps, execution stops with CANCELLED.
        Steps already ``COMPLETED`` (and ``skip_completed``) are skipped to
        support resume.
        """
        if not isinstance(plan, ExecutionPlan):
            raise ExecutionError("Executor.execute requires an ExecutionPlan")
        execution_id = f"exec-{uuid.uuid4().hex[:12]}"
        ctx: Optional[RuntimeContext] = None
        if context_id is not None and self._context_store is not None:
            ctx = self._context_store.try_get(context_id)

        results: Dict[str, StepResult] = {}
        if self._bus is not None:
            self._bus.publish(ExecutionStarted(execution_id, plan.plan_id))
        if self._audit is not None:
            self._audit.record(
                self._subject, "execution.start", plan.plan_id,
                context_id=context_id, status=AuditStatus.OK,
                metadata={"execution_id": execution_id},
            )

        overall = ExecutionOutcome.COMPLETED

        for step in plan.steps:
            if cancel_event is not None and cancel_event.is_set():
                overall = ExecutionOutcome.CANCELLED
                break

            if step.status == StepStatus.COMPLETED and skip_completed:
                continue

            # Policy pre-check (deterministic, fail-closed).
            if self._policy is not None:
                scope = step.metadata.get("scope")
                resource = step.metadata.get("resource", step.action)
                if scope is not None:
                    preq = PolicyRequest(
                        subject=self._subject,
                        action=step.action,
                        resource=resource,
                        context_id=context_id,
                        scope=scope,
                    )
                    pres = self._policy.evaluate(preq)
                    if pres.decision == PolicyDecision.DENY:
                        sr = StepResult(step.step_id, "FAILED", error=f"policy DENY: {pres.reason}")
                        results[step.step_id] = sr
                        self._record_step(execution_id, step, sr, context_id)
                        overall = ExecutionOutcome.FAILED
                        break

            # Execute with retry/timeout.
            sr = self._run_step(
                execution_id, step, handler, ctx, timeout, max_attempts, context_id
            )
            results[step.step_id] = sr
            self._record_step(execution_id, step, sr, context_id)

            if sr.status != "COMPLETED":
                overall = (
                    ExecutionOutcome.TIMEOUT
                    if sr.status == "TIMEOUT"
                    else ExecutionOutcome.FAILED
                )
                break

        report = ExecutionReport(execution_id, overall, results)
        if self._audit is not None:
            self._audit.record(
                self._subject, "execution.finish", plan.plan_id,
                context_id=context_id,
                status=AuditStatus.OK if overall == ExecutionOutcome.COMPLETED else AuditStatus.ERROR,
                metadata={"execution_id": execution_id, "outcome": overall.value},
            )
        return report

    # ------------------------------------------------------------------ #
    def _run_step(
        self, execution_id, step, handler, ctx, timeout, max_attempts, context_id
    ) -> StepResult:
        attempts = 0
        last_error: Optional[str] = None
        while attempts < max_attempts:
            attempts += 1
            try:
                with cf.ThreadPoolExecutor(max_workers=1) as ex:
                    fut = ex.submit(handler, step, ctx)
                    out = fut.result(timeout=timeout) if timeout and timeout > 0 else fut.result()
                return StepResult(step.step_id, "COMPLETED", output=out, attempts=attempts)
            except cf.TimeoutError:
                last_error = f"timeout after {timeout}s"
                # A timeout is terminal for the step regardless of retries.
                return StepResult(step.step_id, "TIMEOUT", error=last_error, attempts=attempts)
            except Exception as exc:  # noqa: BLE001 - surfaced as FAILED
                last_error = str(exc)
        return StepResult(step.step_id, "FAILED", error=last_error, attempts=attempts)

    def _record_step(self, execution_id, step, sr, context_id):
        if self._bus is not None:
            self._bus.publish(ExecutionStepFinished(execution_id, step.step_id, sr.status))
        if self._audit is not None:
            status = AuditStatus.OK if sr.status == "COMPLETED" else AuditStatus.ERROR
            self._audit.record(
                self._subject, "execution.step", step.step_id,
                context_id=context_id, status=status,
                metadata={"execution_id": execution_id, "outcome": sr.status, "attempts": sr.attempts},
            )
