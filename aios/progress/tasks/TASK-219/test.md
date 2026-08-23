# Test — TASK-219

## How the task is verified
Run the bridge test suite:

```bash
python -m pytest aios/skill/github_bridge/tests/test_bridge.py -q
```

## Test matrix (9 tests)
| Test | Mục đích |
|------|----------|
| `test_parse_skill_md_frontmatter` | Parse `SKILL.md` có frontmatter → name/description/body đúng. |
| `test_parse_skill_md_no_frontmatter` | Parse `SKILL.md` không frontmatter → derive name, body=toàn bộ. |
| `test_discover_capabilities` | Thu thập `tools` từ `agents/openai.yaml`. |
| `test_to_skill_contract_validates` | `to_skill_contract` → `SkillContract.validate()` PASS. |
| `test_to_plugin_manifest_schema` | `to_plugin_manifest` → `PluginManifest.validate()` rỗng. |
| `test_convert_skill_dir_writes_package` | Sinh đủ manifest/prompts/scripts/plugin_manifest/catalog. |
| `test_convert_then_install_enable` | `SkillManager.install`+`enable` → status `ENABLED`. |
| `test_deterministic_conversion` | Cùng input → cùng bytes manifest (không timestamp). |
| `test_architecture_clean` | `ArchitectureGuard` quét package → không vi phạm. |

## Result
`9 passed` (xác nhận tại bước TESTING).
