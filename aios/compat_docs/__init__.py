"""Docs & ADR — Compatibility (TASK-088, M12).

Documentation + ADR for the compatibility chain (T084-T087). This module is a
*documentation review/validation* helper (not new runtime code): it checks that
the compatibility docs cover the full chain, that the ADR records its rationale,
that docs are not stale against the DONE implementations, and that references
resolve (no 404). Built on Docs (``docs/``) and DX (T071).

Coverage: docs must cover T084-T087. ADR integrity: rationale required. No stale
doc: status PUBLISHED + provenance link. Deterministic: same content -> same
review result.
"""

from aios.compat_docs.docs import (
    CompatDoc,
    CompatDocReviewer,
    DocReviewResult,
    REQUIRED_COVERED_TASKS,
)

__all__ = [
    "CompatDoc",
    "CompatDocReviewer",
    "DocReviewResult",
    "REQUIRED_COVERED_TASKS",
]
