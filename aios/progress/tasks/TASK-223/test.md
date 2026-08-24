# TASK-223 — Test Plan

## Unit/Integration (`aios/cli/tests/test_planner_agent.py`)
- `test_sample_plan_validates`: file `plan_sample.yaml` (do agent sinh mẫu) → `WorkflowDefinition.from_file` không raise + `validate()` PASS (AC1/AC2).
- `test_sample_plan_executes`: bật `AIOS_REAL_EXECUTION_ENABLED=1` → `aiagent execute plan_sample.yaml` PASS (AC3).
- `test_markdown_plan_validates`: `plan_sample.md` (`- [ ]` lines) → `from_markdown` không raise (fallback).

## Agent/Skill format check
- `test_agent_md_has_frontmatter`: `.github/agents/aios-planner.agent.md` có `name`/`description`/`tools`.
- `test_skill_md_has_frontmatter`: `.github/skills/aios-plan/SKILL.md` có `name`/`description`.

## Architecture
- `python -m pytest aios/governance/architecture -q` → 0 violations (AC6).
