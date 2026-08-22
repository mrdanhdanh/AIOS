"""Tests for Trust Budget + Autonomy Levels + SAFE-STOP (TASK-102)."""

from aios.autonomy_safety.contracts import AutonomyLevel
from aios.trust_budget.budget import TrustBudgetEngine, TrustScope


def test_action_consumes_budget():
    eng = TrustBudgetEngine()
    eng.create_budget("goal-1", scope=TrustScope.GOAL, level=AutonomyLevel.L3, total=1.0)
    allowed, reason = eng.consume("goal-1", "execute", risk_score=0.4)
    assert allowed is True
    assert reason == "consumed"
    assert eng.get_budget("goal-1").remaining == 0.7  # 1.0 - (0.1 + 0.4*0.5=0.3)


def test_budget_empty_triggers_safe_stop():
    eng = TrustBudgetEngine()
    eng.create_budget("goal-2", scope=TrustScope.GOAL, level=AutonomyLevel.L2, total=0.2)
    # Two consumes of cost 0.1 each (risk 0.0) drain the budget to 0.0.
    eng.consume("goal-2", "read", risk_score=0.0)
    allowed, reason = eng.consume("goal-2", "read", risk_score=0.0)
    assert allowed is True
    assert reason == "consumed_safe_stop"
    assert eng.is_safe_stopped() is True  # SAFE-STOP (T068)


def test_action_exceeding_remaining_blocked():
    eng = TrustBudgetEngine()
    eng.create_budget("goal-3", scope=TrustScope.GOAL, level=AutonomyLevel.L2, total=0.2)
    allowed, reason = eng.consume("goal-3", "execute", risk_score=0.9)
    assert allowed is False
    assert reason == "exceeds_remaining"  # BLOCK (T054/T067)


def test_autonomy_level_couples_budget():
    eng = TrustBudgetEngine()
    low = eng.create_budget("goal-low", level=AutonomyLevel.L0)
    high = eng.create_budget("goal-high", level=AutonomyLevel.L4)
    assert high.total > low.total  # higher autonomy -> larger budget


def test_deterministic_consume():
    eng1 = TrustBudgetEngine()
    eng2 = TrustBudgetEngine()
    b1 = eng1.create_budget("g", level=AutonomyLevel.L3, total=1.0)
    b2 = eng2.create_budget("g", level=AutonomyLevel.L3, total=1.0)
    eng1.consume("g", "execute", risk_score=0.4)
    eng2.consume("g", "execute", risk_score=0.4)
    assert eng1.result_hash(b1) == eng2.result_hash(b2)


def test_budget_evidence_provenance():
    eng = TrustBudgetEngine()
    budget = eng.create_budget("goal-ev", level=AutonomyLevel.L1)
    assert eng.provenance_complete(budget) is True
    assert budget.evidence_ref
