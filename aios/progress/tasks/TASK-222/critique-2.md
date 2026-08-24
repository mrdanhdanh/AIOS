# TASK-222 — Critique vòng 2

## Xác nhận
- ARCH-004 compliant: `RealToolHandler` ở `aios/runtime/process.py` import `subprocess`/`os` hợp lệ (runtime layer). Không đặt real I/O trong `aios/tool/adapters.py` (tránh ARCH-004 skip-layer).
- Policy pre-check đã có sẵn trong `Executor.execute` (L290-330) → tái dùng, không viết lại.
- `PermissionBroker`/`PolicyEngine` chia sẻ cùng instance qua kernel → grant có hiệu lực.

## Cải tiến
1. Thêm dry-run log (audit) trước mỗi exec để debug mà không chạy thật.
2. `to_execution_plan` map workflow permission string → `PermissionScope` enum (process.execute→EXECUTE, tool:invoke→TOOL_INVOKE, filesystem.write→WRITE, ...).
3. CLI `execute` đọc `configs/default.yaml` `real_execution` section; nếu tắt → từ chối rõ ràng (AC3).
4. Evidence: mỗi step sinh 1 `Evidence` (type=step_output, source=node_id, content_hash=sha256(output)) để provenance chain complete (AC5).

## Kết luận
Sẵn sàng IMPLEMENT. Rủi ro security đã được giảm bằng safe-default + sandbox `allowed_cwd`.
