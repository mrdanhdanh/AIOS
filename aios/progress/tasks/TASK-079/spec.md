# TASK-079 — RenderReplay / Deterministic Harness

## Objective
Xây dựng **RenderReplay / Deterministic Harness** — ghi lại (record) một execution run
và phát lại (replay) xác định (deterministic) để tái tạo verdict/behavior nhằm audit và
debug. TASK-079 là record/replay harness, không phải execution engine mới (dựa trên
Harness T030/T032 + Evidence T001 + Integrity T078).

## Scope
**In scope:** `aios/replay/` — Recorder, Replayer, ReplaySession (determinism check +
diff report). Tích hợp Harness + Evidence + Integrity (T078).
**Out of scope:** thay thế runtime; mutate production state; provider/filesystem imports.

## Deliverables
- `aios/replay/replay.py` — Recorder, Replayer, ReplaySession, ReplayError.
- `aios/replay/tests/test_replay.py` — 5 tests (Test Matrix).
- Tích hợp Harness (T030/T032) + Evidence (T001) + Integrity (T078).

## Acceptance Criteria
- Recorder ghi normalized input + evidence snapshot + verifier version/config.
- Replay với cùng input + verifier → cùng verdict (deterministic).
- Replay mismatch → flag non-determinism (không promote).
- Replay không mutate production state.
- Mọi replay có provenance evidence.
- Tích hợp được với Harness + Evidence + Integrity (T078).
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T078 (Verification Integrity) → T079 → T080.
- T030 (verification), T032 (evaluation), T001 (evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `replay` là `unknown` layer; chỉ
  import stdlib + `aios.harness` + `aios.verification_integrity`.
