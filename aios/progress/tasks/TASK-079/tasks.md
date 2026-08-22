# Task Breakdown — TASK-079

- [x] Recorder.record (normalized inputs + evidence snapshot + verifier version/config → recorded_inputs_hash).
- [x] ReplaySession dataclass (original_run_id, hashes, verdicts, matches_original).
- [x] Replayer.replay (deterministic re-run via evaluator, no mutation).
- [x] Non-determinism flag (replay != original).
- [x] Tests 5 cases (Test Matrix).
- [x] Tích hợp Harness + Evidence + Integrity (import-level).
