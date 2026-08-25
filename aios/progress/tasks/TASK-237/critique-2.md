# TASK-237 — Critique 2

## Thiếu sót
- Cần đảm bảo đủ 14 planes (Goals/Executions/Agents/Plans/Coding/Evidence/Verification/Autonomy/Resources/Policies/Artifacts/Failures/Recovery/SystemHealth).

## Rủi ro
- Thiếu plane → frontend render thiếu state.

## Đề xuất
- `ControlCenterAggregator.PLANES` liệt kê đủ 14; test assert `plane_count == 14`.
- Router test assert mọi plane có mặt trong response.
