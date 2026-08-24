# TASK-224 — Critique vòng 2

## Xác nhận
- Agent/skill ở `.github/` (VS Code layer) → ARCH-001..004 không áp dụng. OK.
- `--work-dir` + `allowed_cwd` tái dùng logic TASK-222 (RealToolHandler sandbox). OK.
- `--yes` flag không phá DX stability (thêm param mới, không đổi behavior mặc định). OK.

## Cải tiến
1. CLI: nếu `--work-dir` given → `plan_path` mặc định là `<work-dir>/plan.yaml` nếu arg là dir.
2. Agent: sau sinh plan, in prompt "Thực hiện plan này? (yes/no)" và CHỈ gọi terminal khi user yes.
3. Test: verify folder được tạo + plan inside + execute result.

## Kết luận
Sẵn sàng IMPLEMENT.
