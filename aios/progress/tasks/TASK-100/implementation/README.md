# TASK-100 Implementation

Failure-Corpus Improvement Engine lives in `aios/failure_corpus/`:

- `aios/failure_corpus/corpus.py` — `CorpusEntry`, `FailureCorpus`, `FailureCorpusEngine`.
- `aios/failure_corpus/tests/test_corpus.py` — 6 corpus tests (Test Matrix).

Integration (import-level, no rewrite):
- `aios.remediation_detect` (Diagnosis) — T094
- `aios.autonomous_harness_loop` (HarnessLoopRun) — T099
- `aios.harness_coverage` (CoverageMap, Readiness) — T090
- `aios.verification_integrity` (sha256) — T078
- `aios.governance.evidence.store` (EvidenceStore) — T001 Rule 5
