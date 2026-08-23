# TASK-147 — Task Breakdown

1. Định nghĩa `FailureTaxonomy` (SYNTAX/RUNTIME/LOGIC/TIMEOUT/RESOURCE/NETWORK/UNKNOWN) + `CONFIDENCE_THRESHOLD`.
2. `FailureClass` (immutable `class_id`, `observation_ref`, `taxonomy_label`, `confidence`, `evidence_ref`).
3. `FailureClassifier.classify` fail-closed: yêu cầu observation có provenance (T001 Rule 5).
4. Confidence < threshold → UNKNOWN (không promote, T078).
5. `is_promotable` + `provenance()` (content_hash).
6. Tests (`test_classification.py`): 7 tests.
7. Chạy pytest + gate_check + full suite.
