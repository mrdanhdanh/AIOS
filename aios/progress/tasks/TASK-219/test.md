# Test — TASK-219

## How the task is verified
Run the bridge test suite:

```bash
python -m pytest aios/skill/github_bridge/tests/test_bridge.py -q
```

## Test matrix (12 tests)
| Test | Mục đích |
|------|----------|
| `test_parse_skill_md_frontmatter` | Parse `SKILL.md` có frontmatter → name/description/body đúng. |
| `test_parse_skill_md_no_frontmatter` | Parse `SKILL.md` không frontmatter → derive name, body=toàn bộ. |
| `test_discover_capabilities` | Thu thập `tools` từ `agents/openai.yaml`. |
| `test_to_skill_contract_validates` | `to_skill_contract` → `SkillContract.validate()` PASS. |
| `test_to_plugin_manifest_schema` | `to_plugin_manifest` → `PluginManifest.validate()` rỗng. |
| `test_convert_skill_dir_writes_package` | Sinh đủ `skills/<id>/manifest.json` + prompts + SKILL.md + plugin_manifest + catalog + `package_index.json`. |
| `test_convert_then_install_enable` | `SkillManager.install`+`enable` → status `ENABLED`. |
| `test_deterministic_conversion` | Cùng input → cùng bytes manifest (không timestamp). |
| `test_architecture_clean` | `ArchitectureGuard` quét package → không vi phạm. |
| `test_cloned_skill_layout_detection` | Clone `ui-ux-pro-max-skill` → layout `claude`. |
| `test_parse_cloned_skill_package` | Parse package → nhiều sub-skill, có `ui-ux-pro-max`. |
| `test_convert_and_load_cloned_skill` | Convert + install + enable mọi sub-skill qua lifecycle thật. |

## Real-world check
Clone `https://github.com/nextlevelbuilder/ui-ux-pro-max-skill` (layout `claude`) vào `tmp_skill_test/ui-ux-pro-max-skill`, chạy `test_real_skill.py` → 3 passed (layout detection, parse, convert+load mọi sub-skill).

## Layout coverage
- `copilot` (root `SKILL.md`): `test_convert_skill_dir_writes_package`, `test_convert_then_install_enable`, `test_deterministic_conversion`.
- `claude` (`skill.json` + `.claude/skills/*/SKILL.md`): `test_real_skill.py` (3 tests, clone thực tế).

## Result
`12 passed` (9 unit + 3 real-skill; xác nhận tại bước TESTING + thực tế clone).
