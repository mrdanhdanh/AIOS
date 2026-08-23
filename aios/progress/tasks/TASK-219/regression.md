# Regression — TASK-219

## Scope
Chạy regression của dependency closure trước khi đóng task:
- TASK-015 (Plugin/Skill Execution) — `aios/skill/`
- TASK-044 (Plugin Runtime) — `aios/plugin_runtime/`
- TASK-046 (Ecosystem Registry)
- TASK-047 (Developer Kit)
- TASK-049 (Certification)
- TASK-083 (SkillDistiller)
- TASK-063 (Architecture Guard)

## Command
```bash
python -m pytest aios -q
python -m pytest aios/governance/architecture -q
python aios/governance/cli/gate_check.py --task TASK-219
```

## Result
- `pytest aios/skill/github_bridge aios/governance/architecture -q` → **136 passed** (gồm 12 bridge tests + 3 real-skill tests).
- `pytest aios/skill aios/plugin_runtime -q` → **188 passed** (closure T015/T044).
- Architecture gate → no violations (bridge ở `skill` layer compliant).
- `gate_check.py --task TASK-219` → lifecycle artifacts đủ + architecture PASS.
- Thực tế: clone `ui-ux-pro-max-skill` (layout `claude`, 7 sub-skill) → convert + install + enable mọi sub-skill thành công.

## Verdict
Regression PASS. Không vi phạm invariant. Bridge hỗ trợ cả 2 layout (`copilot` + `claude`). Task có thể đóng (DONE) và commit theo Quy tắc 8.
