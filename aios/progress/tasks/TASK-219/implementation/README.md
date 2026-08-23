# TASK-219 — Implementation

## What was built
A **GitHub Skill → AIOS Skill Plugin bridge** that converts a GitHub Copilot
skill directory (`SKILL.md` + `scripts/` + `agents/`) into an AIOS skill
package loadable through the existing skill lifecycle.

## Location
Real code lives in the main package (scanned by the architecture gate):

- `aios/skill/github_bridge/parser.py` — `parse_skill_md`, `parse_skill_md_text`, `parse_agent_yaml`, `discover_capabilities`, `SkillParseError`.
- `aios/skill/github_bridge/adapter.py` — `to_skill_contract`, `to_plugin_manifest`.
- `aios/skill/github_bridge/converter.py` — `convert_skill_dir` (deterministic package writer).
- `aios/skill/github_bridge/__init__.py` — public API.
- `aios/skill/github_bridge/tests/test_bridge.py` — 9 tests.

## Usage
```python
from aios.skill.github_bridge import convert_skill_dir
from aios.skill.manager import SkillManager

result = convert_skill_dir("/path/to/github-skill", "/out/pkg", skill_id="my-skill")
mgr = SkillManager()
mgr.install(result["contract"], source="git")
mgr.enable("my-skill")  # -> ENABLED
```

## Architecture compliance
- Layer: `skill`. Imports: `aios.skill.contracts` (skill), `aios.plugin_runtime.manifest` (unknown), stdlib. No `subprocess`/`os` (ARCH-001). No upward import (ARCH-004).
- Verified by `test_architecture_clean` (ArchitectureGuard over the package).
