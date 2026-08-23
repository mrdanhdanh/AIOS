"""aios.quality_gate — M24 Governance & Quality.

Ten deterministic, fail-closed, provenance-bearing governance components that
compose into a Quality Dashboard + Governance Harness. Each component is an
independent capability (unknown/infra layer) with its own immutable result type.
"""

from __future__ import annotations

from aios.quality_gate._common import QualityGateError, _hash, _now, redact_secret
from aios.quality_gate.gate_states import GateCheck, GateReport, QualityGate
from aios.quality_gate.risk_model import RiskAsset, RiskModel, RiskReport
from aios.quality_gate.policy_engine import Policy, PolicyEngine, PolicyReport
from aios.quality_gate.exception_management import ExceptionManager, ExceptionReport, ExceptionRequest
from aios.quality_gate.quality_debt import DebtItem, DebtReport, QualityDebtTracker
from aios.quality_gate.release_gate import ReleaseCriterion, ReleaseGate, ReleaseReport
from aios.quality_gate.ledger import (
    GovernanceLedger,
    LedgerEntry,
    LedgerReport,
    ProvenanceEdge,
    ProvenanceGraph,
)
from aios.quality_gate.trust_lifecycle import (
    TrustCertificate,
    TrustLifecycle,
    TrustReport,
)
from aios.quality_gate.approval_workflow import (
    ApprovalReport,
    ApprovalRequest,
    ApprovalWorkflow,
)
from aios.quality_gate.dashboard import (
    DashboardReport,
    GovernanceHarness,
    GovernanceHarnessReport,
    QualityDashboard,
)
