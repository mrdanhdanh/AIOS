# Critique 1 — TASK-219

## Missing spec sections
- Chưa nêu rõ hành vi khi `SKILL.md` thiếu frontmatter (đã bổ sung: derive name từ filename, body = toàn bộ nội dung).
- Chưa định nghĩa schema `catalog/skill-<id>.json` (đã bổ sung: `kind`, `skill_id`, `name`, `version`, `source`, `manifest_path`, `plugin_manifest_path`).

## Risks
- **ARCH-001**: bridge nằm ở `skill` layer, cấm `subprocess`/`os`. Converter dùng `pathlib` + `shutil` (stdlib, unknown) — OK. Clone repo GitHub do caller/CLI ngoài layer đảm nhiệm.
- **ARCH-004**: import `aios.plugin_runtime.manifest` → classify là `unknown` (không phải `runtime`), nằm trong allow-list của `skill` → không vi phạm.
- **Determinism**: `SkillContract` sinh `created_at`/`updated_at` = now → package ghi đĩa không deterministic. Đã xử lý: converter loại bỏ 2 trường này trước khi ghi `manifest.json`.

## Suggestions
- Thêm test install+enable thật qua `SkillManager` (offline, không inject service) để chứng minh lifecycle.
- Giữ converter thuần (pure) để dễ test và tái sử dụng.
