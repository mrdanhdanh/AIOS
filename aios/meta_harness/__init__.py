"""Meta-Harness / Verify-the-Verifier (TASK-091, M13).

Known-answer + mutation tests over the harness, with verifier integrity (T078).
Built on Harness (T030/T032), Integrity (T078) and Coverage (T090).

Layering: ``unknown`` (infra) layer — stdlib + ``aios.harness`` +
``aios.verification_integrity`` + ``aios.harness_coverage`` only. No provider/
filesystem/agent imports.
"""

from aios.meta_harness.meta import (
    MetaCheck,
    MetaHarness,
    MetaResult,
    MetaVerdict,
)

__all__ = [
    "MetaVerdict",
    "MetaCheck",
    "MetaResult",
    "MetaHarness",
]
