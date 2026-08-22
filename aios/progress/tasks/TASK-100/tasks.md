# Task Breakdown — TASK-100

- [x] FailureSource enum (T094 | T099).
- [x] CorpusEntry dataclass (failure_id, source, symptom, root_cause, covered_by_harness, version, content_hash, evidence_ref).
- [x] FailureCorpus.add (versioned, deduplicated by content_hash).
- [x] FailureCorpus.gaps (fail-closed gap report).
- [x] FailureCorpus.propose_improvements (harness/detection/remediation).
- [x] FailureCorpus.analysis_hash (deterministic).
- [x] FailureCorpusEngine.collect_from_diagnosis (T094).
- [x] FailureCorpusEngine.collect_from_loop (T099).
- [x] FailureCorpusEngine._record_evidence (T001 provenance).
- [x] FailureCorpusEngine.provenance_complete.
- [x] Tests 6 cases (Test Matrix).
- [x] Tích hợp Detect + Loop + Coverage + Evidence (import-level).
