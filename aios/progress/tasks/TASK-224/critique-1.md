# TASK-224 — Critique vòng 1

## Thiếu sót
1. **Confirm flow**: agent phải dừng lại hỏi user, KHÔNG tự gọi terminal. CLI `execute` có
   `--yes` để agent/script tự gọi không bị kẹt prompt.
2. **Work dir**: cần hàm tạo `work/YYYYMMDD-tenngan` (date từ `datetime.now`). Tên ngắn do
   user/agent đặt (slug của yêu cầu). CLI nhận `--work-dir` absolute hoặc relative to repo.
3. **allowed_cwd**: khi chạy trong work-dir, `RealToolHandler` phải confine cwd vào folder đó
   (đã có logic `allowed_cwd` trong TASK-222) → an toàn hơn (lệnh không tràn ra ngoài repo).
4. **Plan path**: agent ghi plan vào work-dir, rồi gọi `aiagent execute <work-dir>/plan.yaml
   --work-dir <work-dir> --yes`.

## Rủi ro
- Nếu work-dir chưa tồn tại → CLI phải tạo (mkdir -p). Covered.
- Agent hỏi confirm nhưng user im lặng → agent chờ, không tự chạy. Đúng thiết kế.

## Đề xuất
- Thêm helper `resolve_work_dir(name)` trong CLI hoặc agent sinh sẵn path đầy đủ.
- Test dùng tmp_path giả lập work-dir.
