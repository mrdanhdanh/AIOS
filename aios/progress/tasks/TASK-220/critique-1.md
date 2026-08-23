# Critique 1 — TASK-220

## Findings
- Spec thiếu định nghĩa rõ `CoordinationResult` phải trả những field nào → bổ sung `steps`, `artifacts`, `approved`, `closed`.
- Chưa nêu rõ key artifact dùng bare name (`spec.md`) hay prefixed (`TASK-xxx/spec.md`) → cần khớp với `Reviewer.REQUIRED_BEFORE_IMPL` (bare names).
- Chưa mention `review.md` — `STATE_ARTIFACTS["REVIEWED"]` đòi `review.md`, nên coordinator hoặc orchestrator context phải có file này để `close_if_gate_passes` thành công.

## Verdict
REVISE — bổ sung các điểm trên trước implement.
