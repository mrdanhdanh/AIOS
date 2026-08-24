# TASK-222 — Critique vòng 1

## Thiếu sót
1. **Sandbox chi tiết**: plan chưa giới hạn `cwd` và deny-list lệnh nguy hiểm (`rm -rf /`, `format`). Cần thêm trong `RealToolHandler` (cho phép cấu hình `allowed_cwd` + danh sách từ chối).
2. **Markdown plan schema**: chưa rõ `- [ ]` map sang node như thế nào khi có tham số. Cần ví dụ mẫu rõ ràng.
3. **Cross-platform kill**: Windows không có `os.getpgid` → phải dùng `CREATE_NEW_PROCESS_GROUP` + `CTRL_BREAK_EVENT`. Đã note trong implementation.
4. **Broker rỗng mặc định**: nếu quên grant → exec luôn DENY. Đã cover bằng AC3 (safe default tắt).

## Rủi ro
- Real shell exec là high-risk → phải tắt mặc định (`enabled: false`) và chỉ bật tường minh.
- `Executor` chỉ check cancel/timeout GIỮA các step → step đang chạy không bị cancel giữa chừng; killpg xử lý timeout, cancel xử lý giữa step (chấp nhận cho MVP).

## Đề xuất
- Tách `RealToolHandler` thành module riêng `aios/runtime/process.py` để dễ test (đã làm).
- Converter nằm trong `aios/runtime/workflow/definition.py` để tái dùng bởi harness.
