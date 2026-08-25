# TASK-228 — Critique 2

## Phản hồi critique-1
- Đồng thuận: chuẩn hóa `policy_ref`/`permission`/`evidence_ref` trong metadata.
- Đồng thuận: round-trip lossless cho `id`/`command`/`cwd`/`permissions`.

## Bổ sung
- Cần đảm bảo `to_execution_plan` không phá tương thích ngược với T222 (Executor vẫn đọc `scope`/`resource`/`command`/`cwd`/`timeout` từ metadata) → giữ nguyên các key cũ, chỉ thêm key mới.
- `from_execution_plan` phải không raise nếu `metadata` thiếu key mới (fail-soft, default `process.execute`).

## Kết luận
Spec đủ điều kiện implement. Không block.
