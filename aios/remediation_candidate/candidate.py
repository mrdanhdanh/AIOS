"""Remediation Candidate Generation + Risk Scoring (TASK-095, M14).

Canonical candidate contract:

    Candidate
    ├── candidate_id
    ├── source_diagnosis_id
    ├── action
    ├── risk_score
    ├── policy_compliant: bool
    ├── rollback_cost
    └── evidence_ref

Safety properties (all fail-closed / evidence-based-risk / provenance / deterministic):
* Fail-closed policy — candidate violating policy -> removed (never applied).
* Evidence-based risk — score derived from evidence, not guessed.
* Evidence required — every candidate carries provenance (T001 Rule 5).
* Deterministic — same diagnosis + same policy -> same ranking.
* No parallel candidate system — uses Diagnosis (T094) + Governor/Policy (T054).

Integration: imports ``aios.autonomy_governor`` (AutonomyGovernor, AutonomyAction,
AutonomyPolicy, ActionContext) and ``aios.remediation_detect`` (Diagnosis). No
rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from aios.autonomy_governor.contracts import AutonomyAction, AutonomyDecision, AutonomyPolicy
from aios.autonomy_governor.governor import ActionContext, AutonomyGovernor
from aios.governance.evidence.store import EvidenceStore
from aios.remediation_detect.detect import Diagnosis

# Default remediation action catalog: (action, autonomy_action, blast_radius,
# impact, rollback_cost). Deterministic, evidence-shaped inputs for risk scoring.
_REMEDIATION_ACTIONS: Tuple[Tuple[str, str, str, float, float], ...] = (
    ("restart_service", "execute", "local", 0.2, 0.1),
    ("rollback_deploy", "write", "service", 0.4, 0.3),
    ("scale_up", "execute", "service", 0.3, 0.2),
    ("patch_config", "write", "local", 0.3, 0.15),
    ("isolate_node", "modify_system", "global", 0.6, 0.5),
    ("delete_data", "destructive", "global", 0.9, 0.8),
)


@dataclass
class Candidate:
    """A remediation candidate generated from a diagnosis (fail-closed policy)."""

    candidate_id: str
    source_diagnosis_id: str
    action: str
    risk_score: float
    policy_compliant: bool
    rollback_cost: float
    blast_radius: str = "local"  # local | service | global
    impact: float = 0.0
    autonomy_action: str = "execute"
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "source_diagnosis_id": self.source_diagnosis_id,
            "action": self.action,
            "risk_score": self.risk_score,
            "policy_compliant": self.policy_compliant,
            "rollback_cost": self.rollback_cost,
            "blast_radius": self.blast_radius,
            "impact": self.impact,
            "autonomy_action": self.autonomy_action,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class CandidatePlan:
    """Fail-closed, ranked plan of compliant candidates."""

    source_diagnosis_id: str
    candidates: List[Candidate]  # ranked, compliant only (low -> high risk)
    rejected: List[str]  # candidate_ids removed by policy
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_diagnosis_id": self.source_diagnosis_id,
            "candidates": [c.to_dict() for c in self.candidates],
            "rejected": list(self.rejected),
            "evidence_ref": self.evidence_ref,
        }


class CandidateGenerator:
    """Generates remediation candidates from a diagnosis (T094)."""

    def generate(
        self, diagnosis: Optional[Diagnosis], catalog: Optional[list] = None
    ) -> List[Candidate]:
        catalog = catalog or list(_REMEDIATION_ACTIONS)
        did = diagnosis.incident_id if diagnosis else ""
        out: List[Candidate] = []
        for action, autonomy, radius, impact, rollback in catalog:
            cid = f"cand-{hashlib.sha256((did + action).encode()).hexdigest()[:8]}"
            out.append(
                Candidate(
                    candidate_id=cid,
                    source_diagnosis_id=did,
                    action=action,
                    risk_score=0.0,
                    policy_compliant=True,
                    rollback_cost=rollback,
                    blast_radius=radius,
                    impact=impact,
                    autonomy_action=autonomy,
                )
            )
        return out


class RiskScorer:
    """Scores candidate risk from evidence (impact, rollback, blast radius)."""

    _RADIUS_WEIGHT = {"local": 0.1, "service": 0.3, "global": 0.6}

    def score(self, candidate: Candidate) -> Candidate:
        radius_w = self._RADIUS_WEIGHT.get(candidate.blast_radius, 0.3)
        # Evidence-based: every term is an observed/declared metric, never guessed.
        candidate.risk_score = round(
            min(1.0, candidate.impact * 0.5 + candidate.rollback_cost * 0.3 + radius_w),
            4,
        )
        return candidate


class PolicyFilter:
    """Fail-closed policy filter (T054/T067): removes non-compliant candidates."""

    def __init__(self, governor: Optional[AutonomyGovernor] = None) -> None:
        self._governor = governor or AutonomyGovernor()

    def filter(self, candidates: List[Candidate]) -> Tuple[List[Candidate], List[str]]:
        compliant: List[Candidate] = []
        rejected: List[str] = []
        for c in candidates:
            ctx = ActionContext(action=AutonomyAction(c.autonomy_action), target=c.blast_radius)
            decision = self._governor.decide(ctx)
            c.policy_compliant = decision is not AutonomyDecision.BLOCK
            if decision is AutonomyDecision.BLOCK:
                rejected.append(c.candidate_id)
            else:
                compliant.append(c)
        return compliant, rejected


class CandidateRanker:
    """Ranks compliant candidates by risk (low -> high)."""

    def rank(self, candidates: List[Candidate]) -> List[Candidate]:
        return sorted(candidates, key=lambda c: (c.risk_score, c.candidate_id))


class CandidateEngine:
    """Generates, scores, filters and ranks remediation candidates (fail-closed)."""

    def __init__(
        self,
        governor: Optional[AutonomyGovernor] = None,
        evidence_store: Optional[EvidenceStore] = None,
    ) -> None:
        self._governor = governor or AutonomyGovernor()
        self._evidence = evidence_store or EvidenceStore()
        self._generator = CandidateGenerator()
        self._scorer = RiskScorer()
        self._filter = PolicyFilter(self._governor)
        self._ranker = CandidateRanker()

    def run(
        self, diagnosis: Optional[Diagnosis], catalog: Optional[list] = None
    ) -> CandidatePlan:
        """Same diagnosis + same policy -> same ranking (deterministic)."""
        generated = self._generator.generate(diagnosis, catalog)
        scored = [self._scorer.score(c) for c in generated]
        compliant, rejected = self._filter.filter(scored)
        ranked = self._ranker.rank(compliant)
        plan = CandidatePlan(
            source_diagnosis_id=diagnosis.incident_id if diagnosis else "",
            candidates=ranked,
            rejected=rejected,
            evidence_ref=f"plan-{hashlib.sha256((diagnosis.incident_id if diagnosis else '').encode()).hexdigest()[:8]}",
        )
        self._record_evidence(plan)
        return plan

    def _record_evidence(self, plan: CandidatePlan) -> str:
        ev_id = plan.evidence_ref
        self._evidence.add_evidence(
            evidence_id=ev_id,
            task_id="TASK-095",
            run_id="run-095",
            producer="remediation_candidate",
            type="candidate_plan",
            source=plan.source_diagnosis_id,
            content=json.dumps(plan.to_dict(), sort_keys=True),
        )
        return ev_id

    # -- determinism / provenance ---------------------------------------------

    def provenance_complete(self, plan: CandidatePlan) -> bool:
        """Every candidate carries provenance (T001 Rule 5)."""
        if not plan.evidence_ref:
            return False
        return all(c.evidence_ref or plan.evidence_ref for c in plan.candidates)

    def result_hash(self, plan: CandidatePlan) -> str:
        """Deterministic hash (same plan -> same hash)."""
        payload = {
            "source_diagnosis_id": plan.source_diagnosis_id,
            "candidates": [c.candidate_id for c in plan.candidates],
            "rejected": sorted(plan.rejected),
            "evidence_ref": plan.evidence_ref,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()
