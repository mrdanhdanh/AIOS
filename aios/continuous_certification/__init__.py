"""Continuous Certification (TASK-101, M15).

Continuous cert gate: trigger certification on every change (T062/T099), run the
full cert suite (T073 + T087 + T090/T091), gate deploy (PASS -> deploy, FAIL ->
block), cert evidence (provenance).
"""

from aios.continuous_certification.cert import (
    CertGate,
    ContinuousCertEngine,
    ContinuousCertRun,
)

__all__ = [
    "CertGate",
    "ContinuousCertEngine",
    "ContinuousCertRun",
]
