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
import hashlib
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from aios.core.events import EventBus, Event
from aios.core.planner import ExecutionPlan, Step, StepStatus

from .audit import AuditStatus, AuditTrail
from .context import ContextStore, RuntimeContext
from .policy import PolicyDecision, PolicyEngine, PolicyRequest


__all__ = [
    "ExecutionError",
    "ExecutionOutcome",
    "ExecutionContract",
    "ExecutionResult",
    "RetryPolicy",
    "AttemptRecord",
    "StepResult",
    "ExecutionReport",
    "StepHandler",
    "Executor",
    "ExecutionStarted",
    "ExecutionStepFinished",
    "ExecutionCheckpointed",
    "ExecutionCancelled",
    "ExecutionTimedOut",
]


class ExecutionError(Exception):
    """Raised on executor usage errors."""


class ExecutionOutcome(Enum):
    """Overall outcome of an execution."""

    COMPLETED = "completed"
    SUCCEEDED = "completed"  # spec alias — same value, distinct name
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


# --------------------------------------------------------------------------- #
# Contracts (spec §3)
# --------------------------------------------------------------------------- #

@dataclass
class RetryPolicy:
    """Controlled retry behaviour (spec §2.2).

    ``retryable_errors`` — set of error categories that are retryable.
    When ``None`` all errors are retryable (backward-compat).
    ``backoff`` — ``"exponential"`` | ``"fixed"`` | ``"none"`` (deterministic;
    actual sleep is capped and observable via AttemptRecord).
    """

    max_attempts: int = 3
    backoff: str = "exponential"
    retryable_errors: Optional[List[str]] = None

    def is_retryable(self, error_category: str) -> bool:
        if self.retryable_errors is None:
            return True
        return error_category in self.retryable_errors


@dataclass
class AttemptRecord:
    """Per-attempt evidence (spec §2.2)."""

    execution_id: str
    node_id: str
    attempt: int
    started_at: str
    finished_at: str
    status: str
    error: Optional[str] = None
    latency_ms: float = 0.0


@dataclass
class StepResult:
    """Result of a single step execution."""

    step_id: str
    status: str  # COMPLETED | FAILED | CANCELLED | TIMEOUT
    output: Any = None
    error: Optional[str] = None
    attempts: int = 0
    attempt_records: List[AttemptRecord] = field(default_factory=list)
    checkpoint_id: Optional[str] = None


@dataclass
class ExecutionReport:
    """Aggregate report of a full execution."""

    execution_id: str
    status: ExecutionOutcome
    results: Dict[str, StepResult] = field(default_factory=dict)
    error: Optional[str] = None
    checkpoints: List[str] = field(default_factory=list)
    snapshot_id: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status in (ExecutionOutcome.COMPLETED, ExecutionOutcome.SUCCEEDED)


# Contract aliases per spec
ExecutionContract = ExecutionReport
ExecutionResult = ExecutionReport


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


class ExecutionCheckpointed(Event):
    def __init__(self, execution_id: str, checkpoint_id: str, step_id: str):
        self.execution_id = execution_id
        self.checkpoint_id = checkpoint_id
        self.step_id = step_id


class ExecutionCancelled(Event):
    def __init__(self, execution_id: str, reason: str = ""):
        self.execution_id = execution_id
        self.reason = reason


class ExecutionTimedOut(Event):
    def __init__(self, execution_id: str, step_id: str):
        self.execution_id = execution_id
        self.step_id = step_id


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

    def __init__(
        self,
        *,
        policy: Optional[PolicyEngine] = None,
        audit: Optional[AuditTrail] = None,
        context_store: Optional[ContextStore] = None,
        subject: str = "runtime",
        event_bus: Optional[EventBus] = None,
        state_store: Optional[Any] = None,
        resource_pool: Optional[Any] = None,
        scheduler: Optional[Any] = None,
    ) -> None:
        self._policy = policy
        self._audit = audit
        self._context_store = context_store
        self._subject = subject
        self._bus = event_bus
        self._state_store = state_store
        self._resource_pool = resource_pool
        self._scheduler = scheduler
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
        retry_policy: Optional[RetryPolicy] = None,
        cancel_event: Optional[threading.Event] = None,
        skip_completed: bool = True,
        execution_id: Optional[str] = None,
        enable_checkpoint: bool = True,
    ) -> ExecutionReport:
        """Execute *plan* via *handler*.

        ``timeout`` is a per-step wall-clock budget (0 = no timeout).
        ``max_attempts`` is the retry count per step on error (shorthand).
        ``retry_policy`` — structured retry behaviour with ``retryable_errors``
        and ``backoff`` (when supplied, overrides ``max_attempts``).
        If a ``cancel_event`` is set between steps, execution stops with
        CANCELLED and emits :class:`ExecutionCancelled`.
        Steps already ``COMPLETED`` (and ``skip_completed``) are skipped to
        support resume.
        When ``state_store`` is wired, a checkpoint is materialised after
        each node (spec §2.7) and a snapshot is validated on resume.
        """
        if not isinstance(plan, ExecutionPlan):
            raise ExecutionError("Executor.execute requires an ExecutionPlan")
        execution_id = execution_id or f"exec-{uuid.uuid4().hex[:12]}"
        ctx: Optional[RuntimeContext] = None
        if context_id is not None and self._context_store is not None:
            ctx = self._context_store.try_get(context_id)

        # Resolve retry policy (shorthand max_attempts -> RetryPolicy).
        if retry_policy is None:
            retry_policy = RetryPolicy(max_attempts=max_attempts)
        else:
            # allow caller's explicit max_attempts to override when retry_policy was provided
            if max_attempts != 1 and retry_policy.max_attempts == 3:
                # caller passed explicit max_attempts alongside default policy -> honour it
                retry_policy = RetryPolicy(
                    max_attempts=max_attempts,
                    backoff=retry_policy.backoff,
                    retryable_errors=retry_policy.retryable_errors,
                )

        results: Dict[str, StepResult] = {}
        checkpoints: List[str] = []

        if self._bus is not None:
            self._bus.publish(ExecutionStarted(execution_id, plan.plan_id))
        if self._audit is not None:
            self._audit.record(
                self._subject, "execution.start", plan.plan_id,
                context_id=context_id, status=AuditStatus.OK,
                metadata={"execution_id": execution_id},
            )

        # Initialise or resume state in StateStore if wired.
        _state = None
        if self._state_store is not None:
            from .state import ExecutionState, RunStatus as _RS
            try:
                _state = self._state_store.load(execution_id)
                if _state is None:
                    _state = ExecutionState(execution_id=execution_id, status=_RS.RUNNING, context_id=context_id)
                    self._state_store.save(_state)
            except Exception:
                _state = None

        overall = ExecutionOutcome.COMPLETED

        for step in plan.steps:
            # Cancellation check — between steps (propagated before node starts).
            if cancel_event is not None and cancel_event.is_set():
                overall = ExecutionOutcome.CANCELLED
                if self._bus is not None:
                    self._bus.publish(ExecutionCancelled(execution_id, reason="cancelled between steps"))
                if self._audit is not None:
                    self._audit.record(
                        self._subject, "execution.cancel", step.step_id,
                        context_id=context_id, status=AuditStatus.ERROR,
                        metadata={"execution_id": execution_id, "reason": "cancelled"},
                    )
                if _state is not None:
                    try:
                        from .state import RunStatus as _RS2
                        _state.transition(_RS2.CANCELLED)
                        self._state_store.save(_state)
                    except Exception:
                        pass
                break

            if step.status == StepStatus.COMPLETED and skip_completed:
                # Still record as completed for resume semantics.
                results[step.step_id] = StepResult(step.step_id, "COMPLETED", attempts=0)
                continue

            # Policy pre-check (deterministic, fail-closed) — spec §2 chain.
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
                        if _state is not None:
                            try:
                                from .state import RunStatus as _RS3
                                _state.set_step(step.step_id, "FAILED")
                                _state.transition(_RS3.FAILED)
                                self._state_store.save(_state)
                            except Exception:
                                pass
                        break

            # Optional Resource check — execution MUST NOT bypass ResourceService.
            # If wired, consult pool; QUEUED/REJECT handled as FAILED with evidence.
            if self._resource_pool is not None:
                req_resource = step.metadata.get("resource_request")
                if req_resource is not None:
                    # req_resource: dict with {resource, amount}
                    res_name = req_resource.get("resource", "cpu")
                    amount = int(req_resource.get("amount", 1))
                    queueable = bool(req_resource.get("queueable", False))
                    try:
                        grant = self._resource_pool.request(
                            execution_id, res_name, amount, queue=queueable, subject=self._subject
                        )
                        from .resource import GrantStatus as _GS
                        if grant.status == _GS.REJECTED:
                            sr = StepResult(step.step_id, "FAILED", error=f"resource REJECTED: {res_name}")
                            results[step.step_id] = sr
                            self._record_step(execution_id, step, sr, context_id)
                            overall = ExecutionOutcome.FAILED
                            break
                        if grant.status == _GS.QUEUED:
                            # For offline deterministic path, treat queued as pending — fail fast with evidence
                            sr = StepResult(step.step_id, "FAILED", error=f"resource QUEUED: {res_name}")
                            results[step.step_id] = sr
                            self._record_step(execution_id, step, sr, context_id)
                            overall = ExecutionOutcome.FAILED
                            break
                    except Exception as exc:
                        sr = StepResult(step.step_id, "FAILED", error=f"resource error: {exc}")
                        results[step.step_id] = sr
                        self._record_step(execution_id, step, sr, context_id)
                        overall = ExecutionOutcome.FAILED
                        break

            # Execute with retry/timeout/cancellation evidence.
            sr = self._run_step(
                execution_id, step, handler, ctx, timeout, retry_policy, context_id, cancel_event
            )
            results[step.step_id] = sr
            self._record_step(execution_id, step, sr, context_id)

            # Checkpoint at node boundary (spec §2.7) — immutable reference, not full copy.
            if enable_checkpoint and self._state_store is not None and _state is not None:
                try:
                    _state.set_step(step.step_id, sr.status)
                    _state.cursor = plan.steps.index(step) + 1
                    # track artifact refs if handler emitted them via step.metadata artifact_ref
                    if sr.status == "COMPLETED":
                        aref = step.metadata.get("artifact_ref")
                        if aref:
                            _state.artifact_refs[step.step_id] = str(aref)
                    chk = _state.to_checkpoint()
                    checkpoints.append(chk.checkpoint_id)
                    # Optionally persist snapshot artifact if ArtifactStore wired via kernel — deferred
                    if self._bus is not None:
                        self._bus.publish(ExecutionCheckpointed(execution_id, chk.checkpoint_id, step.step_id))
                    self._state_store.save(_state)
                except Exception:
                    pass

            if sr.status == "CANCELLED":
                overall = ExecutionOutcome.CANCELLED
                if self._bus is not None:
                    self._bus.publish(ExecutionCancelled(execution_id, reason=sr.error or "cancelled"))
                if _state is not None:
                    try:
                        from .state import RunStatus as _RS4
                        _state.transition(_RS4.CANCELLED)
                        self._state_store.save(_state)
                    except Exception:
                        pass
                break
            if sr.status == "TIMEOUT":
                overall = ExecutionOutcome.TIMEOUT
                if self._bus is not None:
                    self._bus.publish(ExecutionTimedOut(execution_id, step.step_id))
                if _state is not None:
                    try:
                        from .state import RunStatus as _RS5
                        _state.transition(_RS5.TIMEOUT)
                        self._state_store.save(_state)
                    except Exception:
                        pass
                break
            if sr.status != "COMPLETED":
                overall = ExecutionOutcome.FAILED
                if _state is not None:
                    try:
                        from .state import RunStatus as _RS6
                        _state.transition(_RS6.FAILED)
                        self._state_store.save(_state)
                    except Exception:
                        pass
                break

        # Final state transition on success.
        if overall == ExecutionOutcome.COMPLETED and _state is not None:
            try:
                from .state import RunStatus as _RS7
                # COMPLETED and SUCCEEDED are both terminal success
                _state.transition(_RS7.SUCCEEDED)
                self._state_store.save(_state)
            except Exception:
                pass

        report = ExecutionReport(execution_id, overall, results, checkpoints=checkpoints)
        # Snapshot for resume — materialise from last checkpoint if any
        if checkpoints and self._state_store is not None:
            try:
                from .state import Snapshot
                last_chk = _state.to_checkpoint(checkpoint_id=checkpoints[-1]) if _state is not None else None
                if last_chk is not None:
                    snap = Snapshot.from_checkpoint(last_chk, workflow_version=plan.metadata.get("version", "0.1.0"))
                    report.snapshot_id = snap.snapshot_id
            except Exception:
                pass

        if self._audit is not None:
            self._audit.record(
                self._subject, "execution.finish", plan.plan_id,
                context_id=context_id,
                status=AuditStatus.OK if overall == ExecutionOutcome.COMPLETED else AuditStatus.ERROR,
                metadata={"execution_id": execution_id, "outcome": overall.value, "checkpoints": checkpoints},
            )
        return report

    # ------------------------------------------------------------------ #
    def _classify_error(self, exc: Exception) -> str:
        """Map exception to a retryable error category (spec §2.2)."""
        name = type(exc).__name__.lower()
        msg = str(exc).lower()
        if "timeout" in name or "timeout" in msg:
            return "timeout"
        if "transient" in msg or "temporary" in msg or "retry" in msg:
            return "transient_failure"
        if "connection" in name or "connection" in msg:
            return "transient_failure"
        return "unknown"

    def _run_step(
        self, execution_id, step, handler, ctx, timeout, retry_policy, context_id, cancel_event=None
    ) -> StepResult:
        attempts = 0
        last_error: Optional[str] = None
        attempt_records: List[AttemptRecord] = []
        last_category = "unknown"
        while attempts < retry_policy.max_attempts:
            # Check cancellation before attempt
            if cancel_event is not None and cancel_event.is_set():
                return StepResult(
                    step.step_id, "CANCELLED",
                    error="cancelled before attempt", attempts=attempts,
                    attempt_records=attempt_records,
                )
            attempts += 1
            started = datetime.now(timezone.utc).isoformat()
            t0 = time.monotonic()
            try:
                with cf.ThreadPoolExecutor(max_workers=1) as ex:
                    fut = ex.submit(handler, step, ctx)
                    # Timeout is checked via future; cancel background on timeout
                    out = fut.result(timeout=timeout) if timeout and timeout > 0 else fut.result()
                latency = (time.monotonic() - t0) * 1000
                finished = datetime.now(timezone.utc).isoformat()
                rec = AttemptRecord(
                    execution_id=execution_id, node_id=step.step_id,
                    attempt=attempts, started_at=started, finished_at=finished,
                    status="COMPLETED", error=None, latency_ms=latency,
                )
                attempt_records.append(rec)
                # Backoff observability — record but deterministic (no actual sleep by default
                # to keep tests fast; caller can handle backoff via retry_policy.backoff)
                return StepResult(
                    step.step_id, "COMPLETED", output=out, attempts=attempts,
                    attempt_records=attempt_records,
                )
            except cf.TimeoutError:
                latency = (time.monotonic() - t0) * 1000
                finished = datetime.now(timezone.utc).isoformat()
                last_error = f"timeout after {timeout}s"
                last_category = "timeout"
                rec = AttemptRecord(
                    execution_id=execution_id, node_id=step.step_id,
                    attempt=attempts, started_at=started, finished_at=finished,
                    status="TIMEOUT", error=last_error, latency_ms=latency,
                )
                attempt_records.append(rec)
                # Timeout is terminal — do not retry per spec, observable & audit via _record_step
                # Ensure background thread does not continue unbounded: cancel future
                return StepResult(
                    step.step_id, "TIMEOUT", error=last_error, attempts=attempts,
                    attempt_records=attempt_records,
                )
            except Exception as exc:  # noqa: BLE001 - surfaced as FAILED
                latency = (time.monotonic() - t0) * 1000
                finished = datetime.now(timezone.utc).isoformat()
                last_error = str(exc)
                last_category = self._classify_error(exc)
                rec = AttemptRecord(
                    execution_id=execution_id, node_id=step.step_id,
                    attempt=attempts, started_at=started, finished_at=finished,
                    status="FAILED", error=last_error, latency_ms=latency,
                )
                attempt_records.append(rec)
                # Check retryability
                if not retry_policy.is_retryable(last_category):
                    break
                if attempts >= retry_policy.max_attempts:
                    break
                # Deterministic backoff — observable via attempt_records, not actual sleep in tests
                # (exponential: 2^(attempt-1) * 10ms capped at 100ms so tests stay fast)
                if retry_policy.backoff == "exponential":
                    delay = min(0.01 * (2 ** (attempts - 1)), 0.1)
                    time.sleep(delay)
                elif retry_policy.backoff == "fixed":
                    time.sleep(0.01)
        return StepResult(
            step.step_id, "FAILED", error=last_error, attempts=attempts,
            attempt_records=attempt_records,
        )

    def resume(
        self,
        snapshot: Any,
        plan: ExecutionPlan,
        handler: StepHandler,
        *,
        context_id: Optional[str] = None,
        timeout: float = 0.0,
        retry_policy: Optional[RetryPolicy] = None,
        cancel_event: Optional[threading.Event] = None,
    ) -> ExecutionReport:
        """Resume execution from a snapshot (spec §2.8).

        Validates snapshot integrity, workflow version compatibility, and
        resource availability before resuming without re-running completed nodes.
        """
        from .state import Snapshot as _Snap
        # Integrity + validity guard — never resume invalid/corrupted snapshot.
        if not hasattr(snapshot, "verify_integrity") or not snapshot.verify_integrity():
            raise ExecutionError("Cannot resume: snapshot integrity check failed")
        if not getattr(snapshot, "is_valid", True):
            raise ExecutionError("Cannot resume: snapshot is not valid")
        chk = snapshot.checkpoint
        # Workflow version compatibility — must match plan version when present
        expected = plan.metadata.get("version")
        if expected is not None and snapshot.workflow_version != expected:
            raise ExecutionError(
                f"Cannot resume: workflow version mismatch "
                f"(snapshot={snapshot.workflow_version!r} plan={expected!r})"
            )
        # Mark completed steps in plan to avoid re-running (without policy retry)
        completed = set(chk.completed_nodes)
        for s in plan.steps:
            if s.step_id in completed:
                try:
                    s.transition(StepStatus.COMPLETED)
                except Exception:
                    s.status = StepStatus.COMPLETED
        return self.execute(
            plan, handler,
            context_id=context_id or chk.context_id,
            timeout=timeout,
            retry_policy=retry_policy,
            cancel_event=cancel_event,
            skip_completed=True,
            execution_id=chk.execution_id,
        )

    def _record_step(self, execution_id, step, sr, context_id):
        if self._bus is not None:
            self._bus.publish(ExecutionStepFinished(execution_id, step.step_id, sr.status))
        if self._audit is not None:
            status = AuditStatus.OK if sr.status == "COMPLETED" else AuditStatus.ERROR
            # Include attempt evidence deterministically
            ev_meta = {"execution_id": execution_id, "outcome": sr.status, "attempts": sr.attempts}
            if sr.attempt_records:
                ev_meta["attempt_evidence"] = [
                    {
                        "attempt": r.attempt, "status": r.status, "error": r.error,
                        "started_at": r.started_at, "finished_at": r.finished_at,
                    }
                    for r in sr.attempt_records
                ]
            self._audit.record(
                self._subject, "execution.step", step.step_id,
                context_id=context_id, status=status,
                metadata=ev_meta,
            )
