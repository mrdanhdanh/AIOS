"""Failure-Corpus Improvement Engine (TASK-100, M15).

Corpus-driven improvement: collect failures from Detect (T094) + Autonomous
Harness Loop (T099), maintain a versioned + deduplicated corpus, run gap
analysis (T090) and propose improvements for harness/detection/remediation.
"""

from aios.failure_corpus.corpus import (
    CorpusEntry,
    FailureCorpus,
    FailureCorpusEngine,
    FailureSource,
)

__all__ = [
    "CorpusEntry",
    "FailureCorpus",
    "FailureCorpusEngine",
    "FailureSource",
]
