"""aios.adversarial — M23 Adversarial Evaluation Harness.

Ten deterministic, fail-closed, provenance-bearing adversarial evaluators that
probe the verification harness for weaknesses. Each attacker is an independent
capability (unknown/infra layer) with its own immutable result type.
"""

from __future__ import annotations

from aios.adversarial._common import (
    AdversarialError,
    _hash,
    _now,
    redact_secret,
)
from aios.adversarial.adversarial_evaluation import (
    AdversarialEvaluationHarness,
    AdversarialReport,
    AttackResult,
)
from aios.adversarial.evidence_attackers import (
    EvidenceAttack,
    EvidenceAttackResult,
    EvidenceAttacker,
)
from aios.adversarial.test_weakness_attackers import (
    TestWeaknessAttack,
    TestWeaknessAttacker,
    TestWeaknessResult,
)
from aios.adversarial.requirement_scope_attackers import (
    RequirementScopeAttack,
    RequirementScopeAttacker,
    RequirementScopeResult,
)
from aios.adversarial.certificate_attackers import (
    CertificateAttack,
    CertificateAttacker,
    CertificateResult,
)
from aios.adversarial.prompt_injection import (
    PromptInjectionTester,
    PromptInjectionAttack,
    PromptInjectionResult,
    UntrustedArtifactIsolation,
    ArtifactIsolationAttack,
    ArtifactIsolationResult,
)
from aios.adversarial.execution_integrity_attackers import (
    ExecutionIntegrityAttack,
    ExecutionIntegrityAttacker,
    ExecutionIntegrityResult,
)
from aios.adversarial.environment_dependency_attackers import (
    EnvironmentDependencyAttack,
    EnvironmentDependencyAttacker,
    EnvironmentDependencyResult,
)
from aios.adversarial.boundary_attackers import (
    BoundaryAttack,
    BoundaryAttacker,
    BoundaryResult,
)
from aios.adversarial.collusion_detector import (
    AttackCorpusRegression,
    CollusionDetector,
    CollusionReport,
    ResilienceReport,
)

__all__ = [
    "AdversarialError",
    "_hash",
    "_now",
    "redact_secret",
    "AdversarialEvaluationHarness",
    "AdversarialReport",
    "AttackResult",
    "EvidenceAttacker",
    "EvidenceAttack",
    "EvidenceAttackResult",
    "TestWeaknessAttacker",
    "TestWeaknessAttack",
    "TestWeaknessResult",
    "RequirementScopeAttacker",
    "RequirementScopeAttack",
    "RequirementScopeResult",
    "CertificateAttacker",
    "CertificateAttack",
    "CertificateResult",
    "PromptInjectionTester",
    "PromptInjectionAttack",
    "PromptInjectionResult",
    "UntrustedArtifactIsolation",
    "ArtifactIsolationAttack",
    "ArtifactIsolationResult",
    "ExecutionIntegrityAttacker",
    "ExecutionIntegrityAttack",
    "ExecutionIntegrityResult",
    "EnvironmentDependencyAttacker",
    "EnvironmentDependencyAttack",
    "EnvironmentDependencyResult",
    "BoundaryAttacker",
    "BoundaryAttack",
    "BoundaryResult",
    "CollusionDetector",
    "CollusionReport",
    "ResilienceReport",
    "AttackCorpusRegression",
]
