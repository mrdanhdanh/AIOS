# Implementation — TASK-079

Module: `aios/replay/`
- `replay.py` — `Recorder`, `Replayer`, `ReplaySession`, `ReplayError`.
- `tests/test_replay.py` — 5 tests (Test Matrix).

Tích hợp: import `aios.harness` (run specs) + `aios.verification_integrity` (integrity
gate) — không rewrite runtime. Replay chỉ đọc recorded normalized inputs.
