# TASK-223 — Critique vòng 1

## Thiếu sót
1. **Format command**: agent cần biết `command` là shell thật (TASK-222 chạy qua `subprocess`). Phải nhấn mạnh mỗi node = 1 lệnh thực thi, không dùng placeholder.
2. **Safety**: agent không được sinh lệnh nguy hiểm (`rm -rf /`...) — TASK-222 đã có deny-list nhưng agent nên tự tránh.
3. **Markdown fallback**: nếu user thích `- [ ]` thì agent cũng sinh được `.md` (TASK-222 `from_markdown` hỗ trợ).
4. **Permissions**: mọi node shell/git cần `permissions: [process.execute]` để policy pre-check pass (AC2/AC3).

## Rủi ro
- Agent là text-only → không validate plan trước khi trả. Cần test (AC5) xác thực output parse được.
- Agent nằm ở `.github/agents` (VS Code layer) — không thuộc `aios/agents` nên không bị ARCH-001..004, nhưng vẫn nên giữ I/O-free (chỉ sinh text).

## Đề xuất
- Tạo cả agent (picker) + skill (slash) để user linh hoạt.
- Thêm ví dụ plan mẫu trong skill để agent copy-format.
