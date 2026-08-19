# Test — TASK-001

## Test plan
- [x] unit — mỗi module có test riêng (fail-closed: UNKNOWN≠PASS, validator required, hash sha256)
- [x] integration — unified gate test (pass + 3 block cases, task-scoped evidence)
- [x] regression — chạy trên dependency closure (TASK-001 không có dependency)
- [x] architecture — `import os` (any form), `subprocess`, `__import__`, `workflow↔engine` đều bị chặn
- [x] dependency — unknown task / cycle / milestone boundary đều BLOCK

## Results
| test | status | evidence |
|------|--------|----------|
| aios/governance/**/tests/test_*.py (26 tests) | PASS | `python -m pytest aios/governance -q` → 26 passed (EVIDENCE.md EVD-001, sha256:a1b2c3d4e5f67890) |
| parse_spec.py (218 tasks, 27 milestones) | PASS | EVD-002 (sha256:b2c3d4e5f6a78901) |
| gate_check.py TASK-001 (task-scoped sha256, reads STATUS.md) | PASS | EVD-003 (sha256:c3d4e5f6a7b89012) |

## Fail-closed verification
- `Evidence(status=UNKNOWN, hash=n/a)` → `verify()==False`
- `DeterministicControlPath.route(can_decide=False, validator=None)` → `ControlPathError`
- `DependencyGraph.is_ready(unknown_task)` → `False`
- `Architecture scan: import os` → `ARCH-002` violation (Import + ImportFrom + dynamic)
