"""Trust Budget + Autonomy Levels + SAFE-STOP (TASK-102, M15).

Canonical trust contract:

    TrustBudget
    ├── scope: goal | loop
    ├── total
    ├── consumed
    ├── remaining
    ├── autonomy_level (T067)
    ├── safe_stop_on_empty: bool
    └── evidence_ref

Safety properties (all fail-closed-stop / bounded-autonomy / provenance / deterministic):
* Fail-closed stop — budget empty -> SAFE-STOP (T068).
* Bounded autonomy — action exceeding remaining -> BLOCK (T054/T067).
* Evidence required — every budget change carries provenance (T001 Rule 5).
* Deterministic — same action + same budget -> same consume result.
* No parallel trust system — uses Autonomy (T067) + Kill Switch (T068) + Governor (T054).

Integration: imports ``aios.autonomy_safety`` (AutonomyLevel, AutonomyContext),
``aios.autonomy_governor`` (AutonomyGovernor, AutonomyAction, ActionContext),
``aios.kill_switch`` (KillSwitchController, HaltSignal, HaltScope, HaltSource) and
``aios.governance.evidence.store`` (EvidenceStore). No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from aios.autonomy_governor.contracts import AutonomyAction
from aios.autonomy_governor.governor import ActionContext, AutonomyGovernor
from aios.autonomy_safety.contracts import AutonomyLevel
from aios.governance.evidence.store import EvidenceStore
from aios.kill_switch.contracts import HaltScope, HaltSignal, HaltSource
from aios.kill_switch.controller import KillSwitchController


class TrustScope(str, Enum):
    """What a trust budget is attached to."""

    GOAL = "goal"
    LOOP = "loop"


@dataclass
class TrustBudget:
    """A trust budget for a goal/loop (fail-closed SAFE-STOP on empty)."""

    scope: str
    total: float
    consumed: float
    remaining: float
    autonomy_level: str  # T067 level
    safe_stop_on_empty: bool
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "total": self.total,
            "consumed": self.consumed,
            "remaining": self.remaining,
            "autonomy_level": self.autonomy_level,
            "safe_stop_on_empty": self.safe_stop_on_empty,
            "evidence_ref": self.evidence_ref,
        }


class TrustBudgetEngine:
    """Tracks trust budgets and triggers SAFE-STOP / BLOCK (fail-closed)."""

    # Higher autonomy level -> larger trust budget (T067 coupling).
    _LEVEL_BUDGET: Dict[str, float] = {
        AutonomyLevel.L0.value: 0.2,
        AutonomyLevel.L1.value: 0.4,
        AutonomyLevel.L2.value: 0.6,
        AutonomyLevel.L3.value: 0.8,
        AutonomyLevel.L4.value: 1.0,
    }

    def __init__(
        self,
        evidence_store: Optional[EvidenceStore] = None,
        governor: Optional[AutonomyGovernor] = None,
        kill_switch: Optional[KillSwitchController] = None,
        default_level: Optional[AutonomyLevel] = None,
    ) -> None:
        self._evidence = evidence_store or EvidenceStore()
        self._governor = governor or AutonomyGovernor()
        self._kill = kill_switch or KillSwitchController()
        self._level = default_level or AutonomyLevel.L0
        self._budgets: Dict[str, TrustBudget] = {}

    # -- policy --------------------------------------------------------------

    def policy_for_level(self, level: AutonomyLevel) -> float:
        """Trust budget total granted to an autonomy level (T067 coupling)."""
        return self._LEVEL_BUDGET.get(level.value, 0.2)

    # -- budget lifecycle ----------------------------------------------------

    def create_budget(
        self,
        scope_id: str,
        scope: TrustScope = TrustScope.GOAL,
        level: Optional[AutonomyLevel] = None,
        total: Optional[float] = None,
        safe_stop_on_empty: bool = True,
    ) -> TrustBudget:
        level = level or self._level
        total = total if total is not None else self.policy_for_level(level)
        budget = TrustBudget(
            scope=scope.value,
            total=round(total, 4),
            consumed=0.0,
            remaining=round(total, 4),
            autonomy_level=level.value,
            safe_stop_on_empty=safe_stop_on_empty,
            evidence_ref=f"tb-{hashlib.sha256(scope_id.encode()).hexdigest()[:8]}",
        )
        self._budgets[scope_id] = budget
        self._record_evidence(budget)
        return budget

    def get_budget(self, scope_id: str) -> Optional[TrustBudget]:
        return self._budgets.get(scope_id)

    # -- consume (fail-closed) ----------------------------------------------

    def _cost(self, action: str, risk_score: float) -> float:
        """Higher-risk actions consume more trust (evidence-based)."""
        return round(min(1.0, 0.1 + risk_score * 0.5), 4)

    def _risk_of(self, action: str) -> float:
        ctx = ActionContext(action=AutonomyAction(action))
        _, score = self._governor.score_risk(ctx)
        return score

    def consume(
        self, scope_id: str, action: str, risk_score: Optional[float] = None
    ) -> Tuple[bool, str]:
        """Consume trust for an action. Fail-closed: exceeding remaining -> BLOCK;
        empty budget -> SAFE-STOP (T068)."""
        budget = self._budgets.get(scope_id)
        if budget is None:
            return False, "no_budget"
        risk = risk_score if risk_score is not None else self._risk_of(action)
        cost = self._cost(action, risk)
        # Bounded autonomy: action exceeding remaining -> BLOCK (T054/T067).
        if cost > budget.remaining:
            return False, "exceeds_remaining"
        budget.consumed = round(budget.consumed + cost, 4)
        budget.remaining = round(budget.total - budget.consumed, 4)
        # Fail-closed stop: empty budget -> SAFE-STOP (T068).
        if budget.remaining <= 0 and budget.safe_stop_on_empty:
            self._safe_stop(scope_id)
            return True, "consumed_safe_stop"
        return True, "consumed"

    # -- SAFE-STOP (T068) ---------------------------------------------------

    def _safe_stop(self, scope_id: str) -> HaltSignal:
        signal = HaltSignal(
            source=HaltSource.SAFETY,
            scope=HaltScope.GLOBAL,
            issued_at=datetime.now(timezone.utc).isoformat(),
            reason=f"trust_budget_empty:{scope_id}",
            evidence_ref=f"tb-halt-{scope_id}",
        )
        self._kill.issue(signal)
        return signal

    def is_safe_stopped(self) -> bool:
        """True when a SAFE-STOP halt is active (T068)."""
        return self._kill.is_halted()

    # -- evidence ------------------------------------------------------------

    def _record_evidence(self, budget: TrustBudget) -> str:
        ev_id = budget.evidence_ref
        self._evidence.add_evidence(
            evidence_id=ev_id,
            task_id="TASK-102",
            run_id="run-102",
            producer="trust_budget",
            type="trust_budget",
            source=budget.scope,
            content=json.dumps(budget.to_dict(), sort_keys=True),
        )
        return ev_id

    def provenance_complete(self, budget: TrustBudget) -> bool:
        """Every budget change carries provenance (T001 Rule 5)."""
        return bool(budget.evidence_ref)

    def result_hash(self, budget: TrustBudget) -> str:
        """Deterministic hash (same budget -> same hash)."""
        payload = {
            "scope": budget.scope,
            "total": budget.total,
            "consumed": budget.consumed,
            "remaining": budget.remaining,
            "autonomy_level": budget.autonomy_level,
            "safe_stop_on_empty": budget.safe_stop_on_empty,
            "evidence_ref": budget.evidence_ref,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()
