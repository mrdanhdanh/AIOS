"""aios.verification — M22 Verification Harness.

Ten deterministic, fail-closed, provenance-bearing verifiers that compose into
a CodingCertificate + VerificationHarness. Each verifier is an independent
capability (unknown/infra layer) with its own immutable result type.
"""

from __future__ import annotations

from aios.verification._common import (
    VerificationError,
    _hash,
    _now,
    redact_secret,
)
from aios.verification.requirement_evidence import (
    EvidenceLink,
    MappingReport,
    Requirement,
    RequirementEvidenceMapper,
)
from aios.verification.test_adequacy import (
    AdequacyReport,
    MutationSuite,
    TestAdequacyAnalyzer,
)
from aios.verification.behavioral import (
    BehaviorReport,
    BehaviorSpec,
    BehavioralVerifier,
)
from aios.verification.contract import (
    Contract,
    ContractReport,
    ContractVerifier,
)
from aios.verification.regression import (
    RegressionCheck,
    RegressionReport,
    RegressionVerifier,
)
from aios.verification.security import (
    SecurityReport,
    SecurityScan,
    SecurityVerifier,
)
from aios.verification.performance import (
    PerfBudget,
    PerfReport,
    PerformanceVerifier,
)
from aios.verification.replay_flaky import (
    FlakyReport,
    ReplayFlakyDetector,
    ReplayRun,
)
from aios.verification.evidence_collector import (
    CollectedEvidence,
    EvidenceCollector,
    IntegrityReport,
)
from aios.verification.trust_certificate import (
    CodingCertificate,
    TrustEvaluator,
    TrustReport,
    VerificationHarness,
)

__all__ = [
    "VerificationError",
    "_hash",
    "_now",
    "redact_secret",
    "RequirementEvidenceMapper",
    "Requirement",
    "EvidenceLink",
    "MappingReport",
    "TestAdequacyAnalyzer",
    "MutationSuite",
    "AdequacyReport",
    "BehavioralVerifier",
    "BehaviorSpec",
    "BehaviorReport",
    "ContractVerifier",
    "Contract",
    "ContractReport",
    "RegressionVerifier",
    "RegressionCheck",
    "RegressionReport",
    "SecurityVerifier",
    "SecurityScan",
    "SecurityReport",
    "PerformanceVerifier",
    "PerfBudget",
    "PerfReport",
    "ReplayFlakyDetector",
    "ReplayRun",
    "FlakyReport",
    "EvidenceCollector",
    "CollectedEvidence",
    "IntegrityReport",
    "TrustEvaluator",
    "CodingCertificate",
    "TrustReport",
    "VerificationHarness",
]
