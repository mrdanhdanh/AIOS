"""Self-Evolution Lifecycle (TASK-238, M35).

Promotion pipeline that lets AIOS evolve itself WITHOUT ever self-modifying
directly:

    Proposal -> Experiment -> Harness -> Independent -> Policy -> Regression
            -> Promote (artifact ONLY, never a code change)

Every step reuses the already-shipped modules:
    * aios.agents.self_improver   (SelfImproverAgent -> ImprovementProposal)
    * aios.autonomous_experimentation (ExperimentController -> PromotionDecision)
    * aios.independent_harness     (independent verification)
    * aios.governance.regression   (regression gate)
    * aios.kill_switch / policy    (hard guards)

Safety properties (all fail-closed / provenance / deterministic / no self-modify):
* Fail-closed — any missing evidence / failed gate -> REJECTED, never promote.
* No self-modify — the Promote step emits a PromotionDecision artifact only;
  it NEVER writes to the aios/ tree or calls production capabilities directly.
* Provenance — every phase records a trace (T001 Rule 5).
* Deterministic — same inputs -> same report.
* No parallel evolution system — orchestrates existing modules only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Optional

from aios.agents.self_improver import ImprovementProposal, SelfImproverAgent
from aios.autonomous_experimentation.contracts import (
    Experiment,
    ExperimentStatus,
    MetricSpec,
    PromotionDecision,
)
from aios.autonomous_experimentation.controller import ExperimentController


class EvolutionPhase(str, Enum):
    """Lifecycle phases (fail-closed progression)."""

    IDLE = "idle"
    PROPOSAL = "proposal"
    EXPERIMENT = "experiment"
    INDEPENDENT = "independent"
    POLICY = "policy"
    REGRESSION = "regression"
    PROMOTED = "promoted"
    REJECTED = "rejected"


@dataclass
class SelfEvolutionReport:
    """Fail-closed, provenance-carrying result of one evolution run."""

    evolution_id: str
    phase: EvolutionPhase
    proposal: Optional[ImprovementProposal] = None
    experiment: Optional[Experiment] = None
    independent_verdict: str = ""
    policy_pass: bool = False
    regression_pass: bool = False
    decision: Optional[PromotionDecision] = None
    promoted: bool = False
    trace: List[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evolution_id": self.evolution_id,
            "phase": self.phase.value,
            "proposal_title": self.proposal.title if self.proposal else "",
            "experiment_id": self.experiment.experiment_id if self.experiment else "",
            "independent_verdict": self.independent_verdict,
            "policy_pass": self.policy_pass,
            "regression_pass": self.regression_pass,
            "promoted": self.promoted,
            "decision": self.decision.to_dict() if self.decision else None,
            "trace": list(self.trace),
        }


class SelfEvolutionLifecycle:
    """Orchestrates the self-evolution promotion pipeline (M35, TASK-238).

    Deterministic: same inputs -> same report.
    Fail-closed: any missing evidence / failed gate -> REJECTED.
    No self-modify: Promote emits a PromotionDecision artifact only.
    """

    def __init__(
        self,
        self_improver: Optional[SelfImproverAgent] = None,
        experiment_controller: Optional[ExperimentController] = None,
    ) -> None:
        self._improver = self_improver
        self._exp = experiment_controller or ExperimentController()

    # -- public API -----------------------------------------------------------

    def run(
        self,
        proposal: Optional[ImprovementProposal] = None,
        hypothesis: str = "",
        baseline_ref: str = "",
        baseline_version: str = "",
        candidate_ref: str = "",
        candidate_version: str = "",
        scenario_ref: str = "",
        metric_spec: Optional[List[MetricSpec]] = None,
        policy_scope: str = "",
        evidence_ref: str = "",
        baseline_result: Optional[dict[str, Any]] = None,
        candidate_result: Optional[dict[str, Any]] = None,
        policy_pass: bool = False,
        independent_result: Optional[dict[str, Any]] = None,
        regression_pass: bool = False,
    ) -> SelfEvolutionReport:
        """Drive the full self-evolution pipeline (fail-closed, no self-modify)."""
        evolution_id = f"evo-{hashlib_sha256((hypothesis or 'x') + candidate_ref + evidence_ref)}"
        trace: List[str] = []

        # 1. Proposal (fail-closed: no proposal -> no evolution).
        if proposal is None and self._improver is not None:
            proposal = self._improver.propose_next()
        if proposal is None:
            trace.append("rejected:no_proposal")
            return SelfEvolutionReport(
                evolution_id=evolution_id, phase=EvolutionPhase.PROPOSAL, trace=trace
            )
        trace.append(f"proposal:{proposal.title}")

        # 2. Experiment (propose -> authorize -> run under Harness only).
        exp, err = self._exp.propose(
            hypothesis=hypothesis or proposal.rationale,
            baseline_ref=baseline_ref,
            baseline_version=baseline_version,
            candidate_ref=candidate_ref,
            candidate_version=candidate_version,
            scenario_ref=scenario_ref,
            metric_spec=metric_spec or [],
            policy_scope=policy_scope,
            evidence_ref=evidence_ref,
        )
        if exp is None:
            trace.append(f"rejected:experiment_propose:{err}")
            return SelfEvolutionReport(
                evolution_id=evolution_id,
                phase=EvolutionPhase.EXPERIMENT,
                proposal=proposal,
                trace=trace,
            )
        self._exp.authorize(exp)
        self._exp.run(exp)
        trace.append(f"experiment:{exp.experiment_id}:{exp.status.value}")

        # 3. Independent verification (verify-the-verifier, fail-closed).
        indep_verdict = (independent_result or {}).get("verdict", "inconclusive")
        if indep_verdict != "pass":
            trace.append(f"rejected:independent:{indep_verdict}")
            return SelfEvolutionReport(
                evolution_id=evolution_id,
                phase=EvolutionPhase.INDEPENDENT,
                proposal=proposal,
                experiment=exp,
                independent_verdict=indep_verdict,
                trace=trace,
            )
        trace.append("independent:pass")

        # 4. Policy gate.
        if not policy_pass:
            trace.append("rejected:policy")
            return SelfEvolutionReport(
                evolution_id=evolution_id,
                phase=EvolutionPhase.POLICY,
                proposal=proposal,
                experiment=exp,
                independent_verdict=indep_verdict,
                policy_pass=False,
                trace=trace,
            )
        trace.append("policy:pass")

        # 5. Regression gate (fail-closed: no green regression -> reject).
        if not regression_pass:
            trace.append("rejected:regression")
            return SelfEvolutionReport(
                evolution_id=evolution_id,
                phase=EvolutionPhase.REGRESSION,
                proposal=proposal,
                experiment=exp,
                independent_verdict=indep_verdict,
                policy_pass=True,
                regression_pass=False,
                trace=trace,
            )
        trace.append("regression:pass")

        # 6. Promote — artifact ONLY, never a code change (no self-modify).
        decision = self._exp.evaluate(
            exp,
            baseline_result or {},
            candidate_result or {},
            policy_pass=True,
        )
        promoted = decision.decision == "PROMOTION_READY"
        trace.append(f"promote:{decision.decision}")
        return SelfEvolutionReport(
            evolution_id=evolution_id,
            phase=EvolutionPhase.PROMOTED if promoted else EvolutionPhase.REJECTED,
            proposal=proposal,
            experiment=exp,
            independent_verdict=indep_verdict,
            policy_pass=True,
            regression_pass=True,
            decision=decision,
            promoted=promoted,
            trace=trace,
        )


def hashlib_sha256(text: str) -> str:
    """Deterministic short hash helper."""
    import hashlib

    return hashlib.sha256(text.encode()).hexdigest()[:8]
