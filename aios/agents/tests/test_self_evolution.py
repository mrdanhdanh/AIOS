"""Tests for SelfEvolutionLifecycle (TASK-238, M35)."""
from __future__ import annotations

from aios.agents.self_evolution import (
    EvolutionPhase,
    SelfEvolutionLifecycle,
)
from aios.agents.self_improver import ImprovementProposal
from aios.autonomous_experimentation.contracts import MetricSpec


def _proposal() -> ImprovementProposal:
    return ImprovementProposal(
        title="harden runtime",
        rationale="recurring failures",
        target_module="aios.runtime",
        proposed_spec="# spec",
        confidence=0.8,
        source_signals=["e1:FAIL"],
    )


def _metrics() -> list[MetricSpec]:
    return [MetricSpec(name="quality", direction="increase", threshold=0.1)]


def test_lifecycle_promotes_when_all_gates_pass():
    life = SelfEvolutionLifecycle()
    report = life.run(
        proposal=_proposal(),
        baseline_ref="b",
        baseline_version="v1",
        candidate_ref="c",
        candidate_version="v2",
        scenario_ref="s",
        metric_spec=_metrics(),
        baseline_result={"quality": 0.5},
        candidate_result={"quality": 0.9, "verdict": "pass"},
        policy_pass=True,
        independent_result={"verdict": "pass"},
        regression_pass=True,
    )
    assert report.phase is EvolutionPhase.PROMOTED
    assert report.promoted is True
    assert report.decision is not None
    assert report.decision.decision == "PROMOTION_READY"
    # No self-modify: only an artifact (PromotionDecision) is produced.
    assert report.experiment is not None


def test_lifecycle_rejects_without_proposal():
    life = SelfEvolutionLifecycle()  # no self_improver -> no proposal
    report = life.run()
    assert report.phase is EvolutionPhase.PROPOSAL
    assert report.promoted is False


def test_lifecycle_rejects_on_failed_independent():
    life = SelfEvolutionLifecycle()
    report = life.run(
        proposal=_proposal(),
        baseline_ref="b",
        baseline_version="v1",
        candidate_ref="c",
        candidate_version="v2",
        scenario_ref="s",
        metric_spec=_metrics(),
        policy_pass=True,
        independent_result={"verdict": "inconclusive"},
        regression_pass=True,
    )
    assert report.phase is EvolutionPhase.INDEPENDENT
    assert report.promoted is False


def test_lifecycle_rejects_on_failed_regression():
    life = SelfEvolutionLifecycle()
    report = life.run(
        proposal=_proposal(),
        baseline_ref="b",
        baseline_version="v1",
        candidate_ref="c",
        candidate_version="v2",
        scenario_ref="s",
        metric_spec=_metrics(),
        policy_pass=True,
        independent_result={"verdict": "pass"},
        regression_pass=False,
    )
    assert report.phase is EvolutionPhase.REGRESSION
    assert report.promoted is False


def test_lifecycle_deterministic_same_inputs():
    kw = dict(
        proposal=_proposal(),
        baseline_ref="b",
        baseline_version="v1",
        candidate_ref="c",
        candidate_version="v2",
        scenario_ref="s",
        metric_spec=_metrics(),
        baseline_result={"quality": 0.5},
        candidate_result={"quality": 0.9, "verdict": "pass"},
        policy_pass=True,
        independent_result={"verdict": "pass"},
        regression_pass=True,
    )
    r1 = SelfEvolutionLifecycle().run(**kw)
    r2 = SelfEvolutionLifecycle().run(**kw)
    assert r1.evolution_id == r2.evolution_id
    assert r1.phase == r2.phase
    assert r1.promoted == r2.promoted
