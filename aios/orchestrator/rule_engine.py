"""Rule Engine — deterministic rules over NormalizedRequest (TASK-010).

Returns SUFFICIENT (with plan) or INSUFFICIENT (escalate). Never calls LLM.

Layering: orchestrator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .execution_plan import ExecutionPlan, PlanNode

__all__ = ["RuleDecision", "RuleEngine", "RuleEngineError"]


class RuleEngineError(Exception):
    pass


@dataclass
class RuleDecision:
    """Outcome of rule evaluation."""

    status: str  # SUFFICIENT | INSUFFICIENT
    plan: Optional[ExecutionPlan] = None
    reason: str = ""
    matched_rule: Optional[str] = None
    intent: str = ""

    def is_sufficient(self) -> bool:
        return self.status == "SUFFICIENT"


# Deterministic intents that RuleEngine can handle without LLM/workflow
KNOWN_INTENTS: Dict[str, Dict[str, str]] = {
    "status": {"capability": "system.status", "reason": "matched deterministic rule: status"},
    "health": {"capability": "system.health", "reason": "matched deterministic rule: health"},
    "help": {"capability": "system.help", "reason": "matched deterministic rule: help"},
    "list_tasks": {"capability": "task.list", "reason": "matched deterministic rule: list_tasks"},
    "list_skills": {"capability": "skill.list", "reason": "matched deterministic rule: list_skills"},
    "review_code": {"capability": "code.review", "reason": "matched deterministic rule: review_code"},
    "diagnose_runtime": {"capability": "runtime.diagnose", "reason": "matched deterministic rule: diagnose_runtime"},
    "run_tests": {"capability": "test.run", "reason": "matched deterministic rule: run_tests"},
}


class RuleEngine:
    """Stage 2: deterministic rules over the normalized request."""

    KNOWN_INTENTS = set(KNOWN_INTENTS.keys())

    def decide(self, nr) -> RuleDecision:
        intent = getattr(nr, "intent", "") or ""
        intent = intent.strip().lower()
        if intent in KNOWN_INTENTS:
            info = KNOWN_INTENTS[intent]
            plan = ExecutionPlan(plan_id=f"rule-{intent}", metadata={"source": "rule_engine", "intent": intent})
            plan.add_node(PlanNode(id=f"step-{intent}", capability=info["capability"], description=f"handle:{intent}"))
            return RuleDecision(
                status="SUFFICIENT",
                plan=plan,
                reason=info["reason"],
                matched_rule=intent,
                intent=intent,
            )
        return RuleDecision(
            status="INSUFFICIENT",
            reason="no deterministic rule matched the intent",
            intent=intent,
        )
