"""Improvement Advisor — creates proposals from evaluation evidence.

AC-022-05: Improvement Advisor creates proposals from evidence.
AC-022-06: Proposals don't bypass Policy.
AC-022-08: Orchestrator doesn't become God Object.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from aios.orchestrator.v2.evaluator import EvaluationRecord


class ProposalPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ImprovementProposal:
    """A proposed improvement based on evaluation evidence."""

    proposal_id: str
    title: str
    description: str
    priority: ProposalPriority
    evidence: list[str] = field(default_factory=list)
    source_execution_id: str = ""
    requires_policy_approval: bool = True
    implemented: bool = False
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "evidence": self.evidence,
            "source_execution_id": self.source_execution_id,
            "requires_policy_approval": self.requires_policy_approval,
            "implemented": self.implemented,
            "created_at": self.created_at,
        }


class ImprovementAdvisor:
    """Creates improvement proposals from evaluation evidence.

    AC-022-05: Proposals from evidence.
    AC-022-06: Proposals don't bypass Policy.
    AC-022-08: Not a God Object — only advises.
    """

    def __init__(self) -> None:
        self._proposals: list[ImprovementProposal] = []
        self._counter: int = 0

    def analyze(self, record: EvaluationRecord) -> ImprovementProposal | None:
        """Analyze an evaluation record and create a proposal if warranted."""
        # High latency → suggest optimization
        if record.latency_ms > 5000:
            return self._create_proposal(
                title="Optimize execution latency",
                description=f"Execution {record.execution_id} took {record.latency_ms:.0f}ms",
                priority=ProposalPriority.MEDIUM,
                evidence=[f"latency_ms={record.latency_ms}"],
                source_execution_id=record.execution_id,
            )

        # Policy violations → critical
        if record.policy_violations > 0:
            return self._create_proposal(
                title="Address policy violations",
                description=f"Execution had {record.policy_violations} policy violations",
                priority=ProposalPriority.HIGH,
                evidence=[f"policy_violations={record.policy_violations}"],
                source_execution_id=record.execution_id,
            )

        # High cost → suggest cost reduction
        if record.cost > 1.0:
            return self._create_proposal(
                title="Reduce execution cost",
                description=f"Execution cost ${record.cost:.2f}",
                priority=ProposalPriority.LOW,
                evidence=[f"cost={record.cost}"],
                source_execution_id=record.execution_id,
            )

        return None

    def analyze_batch(self, records: list[EvaluationRecord]) -> list[ImprovementProposal]:
        """Analyze multiple evaluation records."""
        proposals = []
        for record in records:
            proposal = self.analyze(record)
            if proposal:
                proposals.append(proposal)
        return proposals

    def _create_proposal(self, **kwargs: Any) -> ImprovementProposal:
        self._counter += 1
        proposal = ImprovementProposal(
            proposal_id=f"proposal-{self._counter:04d}",
            **kwargs,
        )
        self._proposals.append(proposal)
        return proposal

    def list_proposals(self) -> list[ImprovementProposal]:
        return list(self._proposals)

    def get_proposal(self, proposal_id: str) -> ImprovementProposal | None:
        for p in self._proposals:
            if p.proposal_id == proposal_id:
                return p
        return None
