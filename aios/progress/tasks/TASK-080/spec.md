# TASK-080 — Visual Evidence + Visual Regression + UI State Contract

## Objective
Thêm **Visual Evidence** cho Harness — capture và so sánh trạng thái UI (screenshot / DOM
state) để phát hiện visual regression, kèm **UI State Contract** định nghĩa trạng thái UI
hợp lệ. TASK-080 là visual evidence extension, không phải UI framework mới (dựa trên
Harness T030/T032 + Evidence T001 + Replay T079).

## Scope
**In scope:** `aios/visual_evidence/` — VisualCapture, UIStateContract, VisualRegression,
VisualEvidence. Tích hợp Harness + Evidence + Replay (T079).
**Out of scope:** thay thế harness; render engine; provider/filesystem imports.

## Deliverables
- `aios/visual_evidence/visual.py` — VisualCapture, UIStateContract, VisualRegression, VisualEvidence, VisualError.
- `aios/visual_evidence/tests/test_visual.py` — 6 tests (Test Matrix).
- Tích hợp Harness + Evidence + Replay (T079).

## Acceptance Criteria
- Visual capture chụp UI state → ui_state_hash (deterministic).
- UI State Contract định nghĩa trạng thái hợp lệ + baseline (approved via evidence).
- Visual regression vượt ngưỡng → flag (không auto-pass).
- Baseline thay đổi qua evidence/approval.
- Mọi visual capture có provenance (T001 Rule 5).
- Cùng UI state + capture config → cùng hash (deterministic).
- Tích hợp được với Harness + Evidence + Replay (T079).
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T079 (RenderReplay) → T080 → T081.
- T030/T032 (harness), T001 (evidence), T079 (replay).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `visual_evidence` là `unknown` layer;
  chỉ import stdlib + `aios.harness` + `aios.replay`.
