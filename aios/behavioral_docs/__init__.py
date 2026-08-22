"""Behavioral Spec + ADR-0008 (TASK-093, M13).

Documentation + ADR review/validation for the M13 behavioral/harness chain
(T089-T092). Built on Docs (``docs/``) and DX (T071).

Layering: ``unknown`` (infra) layer — stdlib + ``pathlib`` only. No provider/
filesystem/agent imports beyond stdlib path resolution.
"""

from aios.behavioral_docs.docs import (
    BehavioralDoc,
    BehavioralDocReviewer,
    DocReviewResult,
    DocStatus,
)

__all__ = [
    "DocStatus",
    "BehavioralDoc",
    "DocReviewResult",
    "BehavioralDocReviewer",
]
