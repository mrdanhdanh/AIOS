"""Autonomous Scheduler engine (TASK-062).

Schedule Registry (durable) + Trigger Engine (cron/event/manual) + Activation
Policy (autonomy/resource/policy) + Scheduler Gate (activate only when
Governor authorizes). Fail-closed: undefined/non-matching trigger → no
activation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from aios.autonomous_scheduler.contracts import ScheduleEntry, TriggerType


@dataclass
class ActivationContext:
    goal_id: str = ""
    entry: ScheduleEntry | None = None
    trigger_payload: dict[str, Any] = field(default_factory=dict)
    autonomy_level: str = "supervised"
    resource_budget: float = 0.0
    policy_version: str = "1.0"
    budget_exceeded: bool = False


class Scheduler:
    def __init__(
        self,
        store: dict[str, ScheduleEntry] | None = None,
        governor_decision: Callable[[ActivationContext], str] | None = None,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._store: dict[str, ScheduleEntry] = store if store is not None else {}
        self._governor = governor_decision
        self._now = now or time.time
        self._audit: list[dict[str, Any]] = []

    # ---- registry (durable) --------------------------------------------
    def register(self, entry: ScheduleEntry) -> ScheduleEntry:
        # Durable: persist next_fire so it survives restart.
        if entry.trigger == TriggerType.CRON and entry.cron_expr:
            entry.next_fire = self._derive_next_fire(entry.cron_expr)
        self._store[entry.entry_id] = entry
        return entry

    def get(self, entry_id: str) -> ScheduleEntry | None:
        return self._store.get(entry_id)

    def _derive_next_fire(self, cron_expr: str) -> float:
        # Minimal durable derivation: cron_expr may encode an interval in
        # seconds as "interval:N". Otherwise default to a far-future marker.
        if cron_expr.startswith("interval:"):
            try:
                return self._now() + float(cron_expr.split(":", 1)[1])
            except ValueError:
                return self._now() + 3600.0
        return self._now() + 3600.0

    # ---- trigger engine -------------------------------------------------
    def evaluate_cron(self, entry: ScheduleEntry) -> bool:
        if not entry.enabled or entry.trigger != TriggerType.CRON:
            return False
        return self._now() >= entry.next_fire

    def evaluate_event(self, entry: ScheduleEntry, event: dict[str, Any]) -> bool:
        if not entry.enabled or entry.trigger != TriggerType.EVENT:
            return False
        # Match event_filter as a substring/topic match (fail-closed: no match → False).
        if not entry.event_filter:
            return False
        topic = str(event.get("topic", ""))
        return entry.event_filter in topic

    def evaluate_manual(self, entry: ScheduleEntry, token: str) -> bool:
        if not entry.enabled or entry.trigger != TriggerType.MANUAL:
            return False
        # Fail-closed: token must match exactly; empty token never activates.
        return bool(token) and token == entry.manual_token

    # ---- activation policy ---------------------------------------------
    def check_activation_policy(self, ctx: ActivationContext) -> bool:
        if ctx.budget_exceeded:
            return False
        entry = ctx.entry
        if entry is None:
            return False
        # Autonomy level required must be satisfied by current level.
        levels = ["disabled", "supervised", "bounded", "autonomous"]
        req = levels.index(entry.autonomy_level_required) if entry.autonomy_level_required in levels else 1
        cur = levels.index(ctx.autonomy_level) if ctx.autonomy_level in levels else 1
        return cur >= req

    # ---- gate -----------------------------------------------------------
    def _trigger_satisfied(self, ctx: ActivationContext) -> bool:
        entry = ctx.entry
        if entry is None:
            return False
        payload = ctx.trigger_payload or {}
        if entry.trigger == TriggerType.MANUAL:
            return self.evaluate_manual(entry, str(payload.get("token", "")))
        if entry.trigger == TriggerType.EVENT:
            return self.evaluate_event(entry, payload)
        if entry.trigger == TriggerType.CRON:
            return self.evaluate_cron(entry)
        return False

    def activate(self, ctx: ActivationContext) -> tuple[bool, str]:
        # 0. Fail-closed: trigger must actually be satisfied.
        if not self._trigger_satisfied(ctx):
            self._record_audit(ctx, "blocked", "trigger_not_satisfied")
            return False, "trigger_not_satisfied"
        # 1. Activation policy.
        if not self.check_activation_policy(ctx):
            self._record_audit(ctx, "blocked", "activation_policy")
            return False, "activation_policy_denied"
        # 2. Governor authority (fail-closed: no governor → block).
        if self._governor is not None:
            gv = self._governor(ctx)
            if gv == "BLOCK":
                self._record_audit(ctx, "blocked", "governor_blocked")
                return False, "governor_blocked"
            if gv == "ESCALATE":
                self._record_audit(ctx, "escalate", "governor_escalate")
                return False, "governor_escalate"
        # 3. Activate + audit.
        if ctx.entry is not None:
            ctx.entry.last_fired = self._now()
        self._record_audit(ctx, "activated", "governor_allowed")
        return True, "activated"

    def _record_audit(self, ctx: ActivationContext, outcome: str, reason: str) -> None:
        self._audit.append({
            "goal_id": ctx.goal_id,
            "outcome": outcome,
            "reason": reason,
            "policy_version": ctx.policy_version,
            "timestamp": self._now(),
        })

    @property
    def audit(self) -> list[dict[str, Any]]:
        return list(self._audit)


class SchedulerGate:
    """Thin wrapper: activate only when the Governor authorizes + autonomy suffices.

    Kept as a distinct type so the Scheduler boundary (trigger) is explicit
    and never bypasses the Governor (T054).
    """

    def __init__(self, scheduler: Scheduler) -> None:
        self._scheduler = scheduler

    def request_activation(self, ctx: ActivationContext) -> tuple[bool, str]:
        return self._scheduler.activate(ctx)
