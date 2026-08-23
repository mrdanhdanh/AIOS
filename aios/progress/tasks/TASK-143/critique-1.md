# TASK-143 — Critique 1

## Missing / risky sections
- `secure_run` phải check `sandbox.is_usable` (T136/T040) + policy enforce (T138).
- `replay` phải so sánh original vs replayed output -> mismatch raise (fail-closed, T078).
- `ReplayRun.replay_deterministic` phải phản ánh kết quả.

## Risks
- Nếu replay mismatch mà không detect -> mất determinism guarantee (T030).
- Nếu chạy ngoài sandbox -> vi phạm T040.

## Verdict
SPEC acceptable; cần sandbox-only + fail-closed replay.
