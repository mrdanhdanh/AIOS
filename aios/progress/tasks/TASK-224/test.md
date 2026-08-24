# TASK-224 — Test Plan

## Integration (`aios/cli/tests/test_execute_workdir.py`)
- `test_workdir_created_and_plan_inside`: `--work-dir <tmp>/20260824-x` → folder tạo, plan copy vào, execute PASS.
- `test_workdir_confines_cwd`: lệnh `cd` ra ngoài work-dir bị PermissionError (sandbox).
- `test_yes_flag`: `--yes` chạy không prompt (AC4).

## Agent/Skill
- `test_agent_md_mentions_work_dir`: agent.md chứa "work/" + "xác nhận"/"thực hiện không".
- `test_skill_md_mentions_work_dir`: skill.md chứa "work/".

## Architecture
- `python -m pytest aios/governance/architecture -q` → 0 violations.
