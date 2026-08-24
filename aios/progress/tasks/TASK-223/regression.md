# TASK-223 — Regression

## Local CI
- `python aios/governance/cli/gate_check.py --task TASK-223` → PASS (7-gate AND).
- `python -m pytest aios -q` → toàn bộ xanh (không break TASK-222).

## Không break
- `.github/agents/aios-coordinator.agent.md` không đổi behavior.
- `aiagent execute` (TASK-222) không đổi.

## Blocked?
- `blocked=False` nếu tất cả gate PASS.
