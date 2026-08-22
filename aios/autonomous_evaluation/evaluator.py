"""Autonomous Evaluation engine (TASK-060).

Three distinct tiers (no Governor second):
- StepEvaluator: outcome reached? (Harness T030/T032)
- DecisionMapper: with this verdict, what is the logical next decision? (Decision Policy)
- LoopGate: is the agent *allowed* to execute that decision? (Governor T054)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from aios.autonomous_evaluation.contracts import (
    Decision,
    DecisionPolicy,
    EvaluationRecord,
)
from aios.harness.evaluation import EvalVerdict


class StepEvaluator:
    """Evaluates a single step via Harness verdicts (reuse T030/T032)."""

    def evaluate(
        self,
        step_id: str,
        metrics: list[dict[str, Any]],
        evidence_ref: str = "",
        harness_evaluate: Callable[[str, list[dict]], EvalVerdict] | None = None,
    ) -> EvalVerdict:
        # Missing evidence → INCONCLUSIVE (fail-closed, Rule 5).
        if not evidence_ref:
            return EvalVerdict.INCONCLUSIVE
        if harness_evaluate is not None:
            return harness_evaluate(step_id, metrics)
        # Deterministic default evaluator from metrics.
        if not metrics:
            return EvalVerdict.INCONCLUSIVE
        for m in metrics:
            if m.get("is_hard") and float(m.get("value", 0)) < float(m.get("threshold", 0)):
                return EvalVerdict.FAIL
        if any(float(m.get("value", 0)) < float(m.get("threshold", 0)) for m in metrics):
            return EvalVerdict.WARNING
        return EvalVerdict.PASS


class DecisionMapper:
    """Maps EvalVerdict → decision candidate via Decision Policy (not 1:1)."""

    def __init__(self, policy: DecisionPolicy | None = None) -> None:
        self._policy = policy or DecisionPolicy()

    def map(
        self,
        verdict: EvalVerdict,
        context: dict[str, Any] | None = None,
    ) -> Decision:
        ctx = context or {}
        if verdict == EvalVerdict.PASS:
            return self._policy.pass_decision
        if verdict == EvalVerdict.FAIL:
            return self._policy.fail_decision
        if verdict == EvalVerdict.WARNING:
            # Policy-driven: resolve by warning conditions, never hard-code.
            for cond, dec in self._policy.warning_conditions.items():
                if ctx.get(cond):
                    return dec
            # Default warning handling: revise if degradation, else continue.
            if ctx.get("quality_degradation") or ctx.get("cost_overrun"):
                return Decision.REVISE
            return Decision.CONTINUE
        # INCONCLUSIVE / UNKNOWN -> never promote; policy-driven escalation.
        for cond, dec in self._policy.inconclusive_conditions.items():
            if ctx.get(cond):
                return dec
        return Decision.ESCALATE


class LoopGate:
    """Executes a decision only when the Governor authorizes + autonomy suffices."""

    def __init__(
        self,
        governor_decision: Callable[[Decision, dict], str] | None = None,
    ) -> None:
        self._governor = governor_decision  # (decision, ctx) -> ALLOW/BLOCK/ESCALATE

    def gate(
        self,
        decision: Decision,
        context: dict[str, Any] | None = None,
    ) -> tuple[Decision, str]:
        ctx = context or {}
        # Autonomy budget exceeded -> BLOCK regardless of decision.
        if ctx.get("budget_exceeded"):
            return Decision.BLOCK, "budget_exceeded"
        if self._governor is not None:
            gv = self._governor(decision, ctx)
            if gv == "BLOCK":
                return Decision.BLOCK, "governor_blocked"
            if gv == "ESCALATE":
                return Decision.ESCALATE, "governor_escalate"
        return decision, "allowed"


def evaluate_step(
    step_id: str,
    metrics: list[dict[str, Any]],
    evidence_ref: str,
    policy: DecisionPolicy | None = None,
    context: dict[str, Any] | None = None,
    governor: Callable[[Decision, dict], str] | None = None,
    harness_evaluate: Callable[[str, list[dict]], EvalVerdict] | None = None,
) -> EvaluationRecord:
    """End-to-end: evaluate → map → gate (Evaluation ≠ Decision ≠ Governor)."""
    ev = StepEvaluator().evaluate(step_id, metrics, evidence_ref, harness_evaluate)
    decision = DecisionMapper(policy).map(ev, context)
    final, gov = LoopGate(governor).gate(decision, context)
    rec = EvaluationRecord(
        step_id=step_id,
        verdict=ev.value,
        decision_candidate=decision,
        governor_verdict=gov,
        evidence_ref=evidence_ref,
        metrics={m.get("name", "m"): m.get("value") for m in metrics},
    )
    rec.decision_candidate = final
    return rec
