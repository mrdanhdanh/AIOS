# TASK-219 — Breakdown

1. **Parser** (`parser.py`)
   - `parse_skill_md_text` / `parse_skill_md`: tách YAML frontmatter (`name`, `description`) + body.
   - `parse_agent_yaml`: đọc `agents/*.yaml`.
   - `discover_capabilities`: thu thập `tools`/`capabilities` từ agent defs.
   - `SkillParseError` (fail-closed).

2. **Adapter** (`adapter.py`)
   - `to_skill_contract`: map → `SkillContract` (normalize permissions/runtime, resources chứa độ dài instructions).
   - `to_plugin_manifest`: sinh `PluginManifest` schema-compatible.

3. **Converter** (`converter.py`)
   - `convert_skill_dir`: sinh `manifest.json` (bỏ timestamp), `prompts/instructions.md`, copy `scripts/`, copy `SKILL.md`, `plugin_manifest.json`, `catalog/skill-<id>.json`. Deterministic.

4. **Package init** (`__init__.py`): export public API.

5. **Tests** (`tests/test_bridge.py`): 9 tests bao phủ parse/contract/convert/install+enable/deterministic/architecture.

6. **Evidence & docs**: task artifacts, cập nhật master spec (Amendment TASK-219), PLAN/LOG/STATS.

7. **Governance**: chạy `gate_check.py --task TASK-219` + `pytest aios -q` (regression closure).
