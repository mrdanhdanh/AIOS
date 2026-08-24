# TASK-224 Implementation Summary

## Files changed
1. `.github/agents/aios-planner.agent.md` — hỏi confirm + quy ước `work/YYYYMMDD-tenngan/`.
2. `.github/skills/aios-plan/SKILL.md` — tương tự.
3. `aios/cli/workflow_cli.py` — `_cmd_execute` thêm `--work-dir <dir>` (mkdir -p, đặt plan
   vào, chạy với allowed_cwd=dir) + `--yes` (bỏ qua confirm).
4. `aios/cli/tests/test_execute_workdir.py` — tests AC3/AC4.

## Usage
```bash
# Agent sinh plan vào work/20260824-webno1/plan.yaml, hỏi "thực hiện không?"
# User yes -> agent gọi:
aiagent execute work/20260824-webno1/plan.yaml --work-dir work/20260824-webno1 --yes
```
