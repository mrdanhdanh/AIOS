"""Kill Switch controller (TASK-068).

Broadcasts a ``HaltSignal`` to every active execution context (loop/goal) and
enforces the halt fail-closed:

* The authoritative halted state is set BEFORE broadcasting, so ``begin_action``
  blocks any new action immediately — even if a layer later tries to skip.
* After broadcast the controller audits each context's compliance
  (``is_halted()``). A context that ignores the halt is recorded as a
  ``HaltViolation`` and the whole ``issue`` fails closed.
* In-flight work is gracefully drained and persisted (durable) before stopping.
* Every halt writes audit evidence with full provenance.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from aios.kill_switch.audit import AuditLog
from aios.kill_switch.contracts import (
    DrainResult,
    ExecutionContext,
    HaltResult,
    HaltSignal,
    HaltScope,
    HaltState,
    HaltViolation,
)
from aios.kill_switch.persistence import DurablePersistence, LocalDurablePersistence


class KillSwitchController:
    def __init__(
        self,
        evidence_store: Any = None,
        persistence: Optional[DurablePersistence] = None,
        audit: Optional[AuditLog] = None,
    ) -> None:
        self._contexts: Dict[str, ExecutionContext] = {}
        self._halted_global: bool = False
        self._scoped_halts: List[HaltSignal] = []
        self._halt_states: List[HaltState] = []
        self._violations: List[HaltViolation] = []
        self._processed: Dict[str, HaltResult] = {}
        self._persistence = persistence or LocalDurablePersistence()
        self._audit = audit or AuditLog(evidence_store=evidence_store)

    # ---- registry ----------------------------------------------------- #
    def register(self, context: ExecutionContext) -> None:
        self._contexts[context.context_id] = context

    def unregister(self, context_id: str) -> None:
        self._contexts.pop(context_id, None)

    def active_contexts(self) -> List[str]:
        return list(self._contexts.keys())

    # ---- authoritative halt query (fail-closed) ----------------------- #
    def is_halted(self, scope: HaltScope = HaltScope.GLOBAL, target_id: str = "") -> bool:
        if self._halted_global:
            return True
        for sig in self._scoped_halts:
            if sig.scope == HaltScope.GLOBAL:
                return True
            if sig.scope == scope and (not sig.target_id or sig.target_id == target_id):
                return True
        return False

    # ---- issue halt --------------------------------------------------- #
    def issue(self, signal: HaltSignal) -> HaltResult:
        # Deterministic / idempotent: same signal -> same result, no re-broadcast.
        if signal.signal_id in self._processed:
            return self._processed[signal.signal_id]

        affected = self._affected_contexts(signal)

        # Mark halted authoritatively FIRST (fail-closed): blocks new actions
        # even if a layer later tries to skip the halt.
        if signal.scope == HaltScope.GLOBAL:
            self._halted_global = True
        else:
            self._scoped_halts.append(signal)

        violations: List[str] = []

        # Broadcast on_halt (fail-closed: any error is a violation).
        for cid in affected:
            ctx = self._contexts[cid]
            try:
                ctx.on_halt(signal)
            except Exception as exc:  # noqa: BLE001
                msg = f"{cid}: on_halt raised {exc!r}"
                violations.append(msg)
                self._violations.append(HaltViolation(msg))
            # Compliance: the context must report halted.
            try:
                if not ctx.is_halted():
                    msg = f"{cid}: did not halt (skip detected)"
                    violations.append(msg)
                    self._violations.append(HaltViolation(msg))
            except Exception as exc:  # noqa: BLE001
                msg = f"{cid}: is_halted raised {exc!r}"
                violations.append(msg)
                self._violations.append(HaltViolation(msg))

        # Graceful drain + persist in-flight state (durable).
        drained: List[str] = []
        for cid in affected:
            ctx = self._contexts[cid]
            try:
                res = ctx.drain()
                if isinstance(res, DrainResult) and res.drained:
                    self._persistence.persist(cid, res.state or {})
                    drained.append(cid)
                if isinstance(res, DrainResult) and res.error:
                    violations.append(f"{cid}: drain error {res.error}")
            except Exception as exc:  # noqa: BLE001
                violations.append(f"{cid}: drain raised {exc!r}")

        # Audit evidence (provenance).
        evidence_ref = self._audit.record_halt(signal, affected, drained)
        signal.evidence_ref = evidence_ref

        halted_at = datetime.now(timezone.utc).isoformat()
        state = HaltState(
            signal=signal,
            affected_contexts=affected,
            drained_contexts=drained,
            halted_at=halted_at,
            evidence_ref=evidence_ref,
        )
        self._halt_states.append(state)

        result = HaltResult(
            signal_id=signal.signal_id,
            halted=True,
            affected_contexts=affected,
            drained_contexts=drained,
            evidence_ref=evidence_ref,
            violations=list(violations),
        )
        self._processed[signal.signal_id] = result

        if violations:
            raise HaltViolation("halt not enforced fail-closed: " + "; ".join(violations))
        return result

    def _affected_contexts(self, signal: HaltSignal) -> List[str]:
        if signal.scope == HaltScope.GLOBAL:
            return list(self._contexts.keys())
        out: List[str] = []
        for cid, ctx in self._contexts.items():
            if signal.scope == HaltScope.GOAL and ctx.context_type == "goal":
                if not signal.target_id or cid == signal.target_id:
                    out.append(cid)
            elif signal.scope == HaltScope.LOOP and ctx.context_type == "loop":
                if not signal.target_id or cid == signal.target_id:
                    out.append(cid)
        return out

    # ---- action gate (fail-closed) ------------------------------------ #
    def begin_action(
        self,
        context_id: str,
        scope: HaltScope = HaltScope.GLOBAL,
        target_id: str = "",
    ) -> None:
        """Fail-closed gate: any layer MUST call this before starting a new
        action. Raises ``HaltViolation`` if the relevant scope is halted."""
        if self.is_halted(scope, target_id or context_id):
            raise HaltViolation(
                f"action blocked: scope {scope.value} halted (context={context_id})"
            )

    # ---- queries ------------------------------------------------------ #
    def halt_states(self) -> List[HaltState]:
        return list(self._halt_states)

    def violations(self) -> List[HaltViolation]:
        return list(self._violations)

    def persistence(self) -> DurablePersistence:
        return self._persistence
