"""Compatibility Conformance (TASK-087, M12).

A conformance harness that confirms an AIOS 1.x build conforms to the
compatibility baseline (T084) and the backward-compat guarantee (T086), then
emits an evidence-backed conformance report. Built on Certification (T073),
Contract Freeze (T064), Version Baseline (T084) and Backward Compatibility
(T086).

Fail-closed: one check FAIL -> the build is NOT conformant. Deterministic: same
build + same suite -> same result. Evidence: the report carries full provenance.
"""

from aios.conformance.conformance import (
    ConformanceCheck,
    ConformanceReport,
    ConformanceRunner,
)

__all__ = [
    "ConformanceCheck",
    "ConformanceReport",
    "ConformanceRunner",
]
