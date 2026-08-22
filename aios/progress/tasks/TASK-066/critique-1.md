# TASK-066 — Critique 1

## Strengths
- Phạm vi rõ: durability + recovery, không redesign loop.
- Tái sử dụng runtime state store (T065) và recovery contracts (T055) thay vì tạo store song song.
- Fail-closed rõ ràng: resume chỉ từ verified checkpoint, raise nếu không có.

## Risks / Gaps
- `created_at` dùng `datetime.now()` có thể gây non-determinism nếu test không pin timestamp — cần test dùng timestamp cố định.
- `state_hash` lấy từ `to_checkpoint().content_hash` của runtime sẽ khác nhau giữa 2 lần gọi (vì `created_at` của checkpoint được mint mới). Cần derive từ nguồn stable (`ExecutionState.to_dict()`).
- Cần đảm bảo architecture guard không fail: `aios/durable/` phải là layer `unknown` (không chứa keyword layer).

## Required revisions
- Đổi `state_hash` thành derive từ `ExecutionState.to_dict()` (stable) qua helper `runtime_state_hash`.
- Test determinism dùng timestamp cố định và `checkpoint_id` cố định.
- Xác nhận không import `aios.agents` ở bất kỳ module nào trong `aios/durable/`.
