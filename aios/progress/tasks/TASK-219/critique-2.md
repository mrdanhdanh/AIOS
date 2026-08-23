# Critique 2 — TASK-219

## Validation of critique 1 fixes
- Frontmatter thiếu → đã xử lý trong `parse_skill_md_text` (test `test_parse_skill_md_no_frontmatter` PASS).
- Catalog schema → đã định nghĩa và test (`test_convert_skill_dir_writes_package` PASS).
- ARCH-001/004 → code chỉ import `aios.skill.contracts`, `aios.plugin_runtime.manifest`, stdlib → test `test_architecture_clean` quét package = PASS.
- Determinism → đã loại timestamp; test `test_deterministic_conversion` PASS.

## Additional concerns
- **Permission mapping**: Copilot skill thường không khai báo permission rõ ràng. Bridge map hint → `ALLOWED_PERMISSIONS`; nếu không map được thì bỏ qua (fail-closed an toàn). Đã test `to_skill_contract_validates` (permissions rỗng vẫn hợp lệ).
- **Entrypoint**: nếu skill không có `scripts/*.py`, entrypoint = `""` (hợp lệ theo `_ENTRYPOINT_RE`). Test xác nhận.
- **Capability discovery**: chỉ lấy từ `agents/*.yaml` (`tools`/`capabilities`). Nếu thiếu, `required_capabilities=[]` → enable vẫn PASS (không capability registry).

## Verdict
Spec đủ điều kiện implement. Không còn gap chặn. Có thể chuyển sang BREAKDOWN.
