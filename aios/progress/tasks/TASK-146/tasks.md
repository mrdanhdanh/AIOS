# TASK-146 — Task Breakdown

1. Định nghĩa `Observation` (immutable `observation_id`, `loop_ref`, `execution_ref`, `trace`, `evidence_ref`).
2. `ExecutionObservation.capture` fail-closed: yêu cầu `execution_ref` + `loop_ref` + `evidence_ref`.
3. Redact secret trong trace (T040/T113).
4. `get` + `provenance()` (content_hash, T078).
5. Tests (`test_observation.py`): 7 tests.
6. Chạy pytest + gate_check + full suite.
