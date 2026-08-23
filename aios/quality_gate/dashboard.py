"""TASK-184 — Quality Dashboard + Governance Harness (M24).

Capstone integrating the M24 governance components into a single dashboard
report and a governance harness that runs them together.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.quality_gate._common import QualityGateError, _hash
from aios.quality_gate.gate_states import GateReport, QualityGate
from aios.quality_gate.risk_model import RiskAsset, RiskModel
from aios.quality_gate.policy_engine import PolicyEngine
from aios.quality_gate.release_gate import ReleaseGate


@dataclass(frozen=True)
class DashboardReport:
    report_id: str
    components: int
    summary: str


@dataclass(frozen=True)
class GovernanceHarnessReport:
    report_id: str
    gate: str
    risk: str
    policy: str
    release: str


class QualityDashboard:
    """Aggregate component reports into a dashboard summary."""

    def aggregate(self, reports: List[object]) -> DashboardReport:
        if reports is None:
            raise QualityGateError("reports must be provided")
        count = len(reports)
        summary = "OK" if count > 0 else "EMPTY"
        report_id = _hash(f"{count}|{summary}")
        return DashboardReport(report_id=report_id, components=count, summary=summary)


class GovernanceHarness:
    """Run the M24 governance components together on a subject."""

    def run(self, subject: str) -> GovernanceHarnessReport:
        if not subject:
            raise QualityGateError("subject must be non-empty")
        gate = QualityGate(subject)
        g_report = gate.evaluate([])
        risk = RiskModel().classify(RiskAsset(asset_id=subject, likelihood="POSSIBLE", impact="MODERATE"))
        policy = PolicyEngine("BALANCED").evaluate(subject, [])
        release = ReleaseGate().evaluate([])
        report_id = _hash(f"{subject}|{g_report.state}|{risk.level}|{policy.decision}|{release.decision}")
        return GovernanceHarnessReport(
            report_id=report_id,
            gate=g_report.state,
            risk=risk.level,
            policy=policy.decision,
            release=release.decision,
        )
