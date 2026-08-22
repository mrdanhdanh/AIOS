# Implementation — TASK-080

Module: `aios/visual_evidence/`
- `visual.py` — `VisualCapture`, `UIStateContract`, `VisualRegression`, `VisualEvidence`, `VisualError`.
- `tests/test_visual.py` — 6 tests (Test Matrix).

Tích hợp: import `aios.harness` (run specs) + `aios.replay` (replay visual baseline) —
không rewrite harness. Visual evidence gắn provenance qua `evidence_ref`.
