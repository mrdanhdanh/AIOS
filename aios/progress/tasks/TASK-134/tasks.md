# Breakdown — TASK-134

1. `aios/coder/filesafety.py` — `FileSafetyBoundary` (scope root, realpath resolve).
2. `check()` fail-closed: traversal/absolute-outside/symlink escape → DENIED (T113).
3. `require()` raise khi denied; constructor reject nếu root không tồn tại.
4. `ScopeDecision` — `evidence_id` + `content_hash` (T001 Rule 5).
5. Tests (8) theo Test Matrix TASK-134 + architecture guard.
6. Tích hợp: T125→T133 -> T134 (đóng M19).
