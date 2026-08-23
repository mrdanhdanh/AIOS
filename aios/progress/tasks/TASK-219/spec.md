# TASK-219 — GitHub Skill → AIOS Skill Plugin Bridge

## Objective
Xây **bridge/adapter** chuyển đổi một GitHub Copilot skill (thư mục chứa `SKILL.md` + `scripts/` + `agents/`) thành một **AIOS Skill Plugin** có thể nạp qua lifecycle chuẩn (`SkillManager.install` → `enable`). Tận dụng khung có sẵn `aios/skill` (TASK-015, M2) và `aios/plugin_runtime` (TASK-044, M8) — **không** viết lại runtime. Đóng góp vào năng lực "Third-Party Skill Ingestion" mà không cần mở milestone M27.

## Scope
**In scope:** `aios/skill/github_bridge/` — `parser.py`, `adapter.py`, `converter.py`, `__init__.py`, `tests/test_bridge.py`, `tests/test_real_skill.py`. Tích hợp Skill (T015) + Plugin Runtime (T044) + Architecture Guard (T063) + Ecosystem Registry (T046) + Certification (T049).
**Out of scope:** tự động clone toàn bộ GitHub Marketplace; security sandboxing sâu (thuộc T040/T049); dynamic runtime; provider/filesystem imports trực tiếp.

## Supported skill layouts (QUAN TRỌNG — đọc khi mở session mới)
Bridge hỗ trợ **2 layout** GitHub skill, tự phát hiện qua `detect_skill_layout`:
1. **`copilot`** — single root `SKILL.md` (Copilot/agent-skill chuẩn). → 1 skill package.
2. **`claude`** — `skill.json` (package metadata) + `.claude/skills/<name>/SKILL.md` (multi-sub-skill, ví dụ `ui-ux-pro-max`, `brand`, `design`...). → 1 package chứa N sub-skill, mỗi sub-skill 1 `SkillContract`.

> Thực tế đã validate: clone `https://github.com/nextlevelbuilder/ui-ux-pro-max-skill` (layout `claude`, 7 sub-skill) → convert + `SkillManager.install`+`enable` mọi sub-skill → `ENABLED`. Xem `tests/test_real_skill.py`.
> **Skill đã lưu trữ thực tế:** `skills/ui-ux-pro-max/` (7 sub-skill: banner-design, brand, design, design-system, slides, ui-styling, ui-ux-pro-max), sinh bởi `tools/install_github_skill.py`. Test reload: `tests/test_persisted_skills.py`.
> Nếu sau này gặp skill layout khác (vd Cursor `.cursor/rules`, Windsurf...), mở rộng `detect_skill_layout` + `parse_skill_package` trong `parser.py` — đừng viết lại converter.

## Deliverables
- `aios/skill/github_bridge/parser.py` — `parse_skill_md`, `parse_skill_md_text`, `parse_agent_yaml`, `discover_capabilities`, `SkillParseError`.
- `aios/skill/github_bridge/adapter.py` — `to_skill_contract`, `to_plugin_manifest` (map field + normalize permissions/runtime).
- `aios/skill/github_bridge/converter.py` — `convert_skill_dir` (sinh package deterministic).
- `aios/skill/github_bridge/tests/test_bridge.py` — 9 tests (parse, contract, convert, install+enable, deterministic, architecture).
- Task artifacts + evidence.

## Acceptance Criteria
- Parse `SKILL.md` (có/không frontmatter) → structured data đúng.
- `to_skill_contract` sinh `SkillContract` hợp lệ (`validate()` PASS).
- `convert_skill_dir` sinh package đầy đủ (manifest + prompts + scripts + plugin_manifest + catalog).
- Contract sinh ra có thể `install` + `enable` qua `SkillManager` → status `ENABLED`.
- Cùng input skill + converter → cùng package (deterministic, không timestamp).
- Architecture gate quét package → không vi phạm ARCH-001..004.
- Regression của TASK-047/083/046/049 PASS; không vi phạm invariants.

## Dependencies
- T083 (SkillDistiller) → T219 (M11) → T084 (M12).
- T015 (skill), T044 (plugin runtime), T063 (architecture guard), T046 (ecosystem registry), T049 (certification).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `github_bridge` là `skill` layer; import `aios.skill` (skill, allowed) + `aios.plugin_runtime` (unknown, allowed). Cấm `subprocess`/`os` (ARCH-001).
