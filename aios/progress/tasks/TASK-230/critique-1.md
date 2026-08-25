# TASK-230 — Critique 1

## Thiếu sót
- Spec chưa nêu rõ `CapabilityContract.capability_id` phải khớp `^[a-zA-Z][a-zA-Z0-9_]*$` (không có dấu chấm) → test dùng `code.read` sẽ raise `CapabilityError`.
- Chưa chỉ định resolver fail-closed khi capability không thuộc contract (ARCH-004: inject only).

## Rủi ro
- Nếu resolver cho phép capability không khai báo → vi phạm ARCH-004.

## Đề xuất
- Resolver phải check `contract.can_inject` TRƯỚC rồi mới check registry.
- Test dùng id hợp lệ (`code_read`).
