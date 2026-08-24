# TASK-224 — Regression

## Local CI
- `gate_check.py --task TASK-224` → PASS.
- `python -m pytest aios -q` → xanh (không break TASK-222/223).

## Không break
- `aiagent execute` cũ (không --work-dir) vẫn chạy bình thường (backward compatible).
- Agent/skill cũ vẫn hợp lệ.

## Blocked?
- `blocked=False` nếu gate PASS.
