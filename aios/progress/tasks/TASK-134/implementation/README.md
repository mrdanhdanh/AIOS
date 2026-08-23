# TASK-134 Implementation

File Safety Boundary + Scope Enforcement lives in:

- `aios/coder/filesafety.py` — `FileSafetyBoundary`, `ScopeDecision`, `ScopeStatus`, `FileSafetyError`.
- Tests trong `aios/coder/tests/test_filesafety.py` (8 tests, Test Matrix TASK-134).

Design:
- `FileSafetyBoundary(scope_root)` — root phải tồn tại; resolve `os.path.realpath` để bắt symlink/traversal/absolute-outside escape.
- `check()` fail-closed (T113): escape → DENIED, không silent-allow. `require()` raise `FileSafetyError`.
- Mọi `ScopeDecision` ghi `evidence_id` + `content_hash` (sha256) — provenance (T001 Rule 5).

Integration (import-level, no rewrite):
- `aios.coder.contract` (T125) — agent boundary
- `aios.security` (T113) — safety/security boundary semantics
- `aios.coder.filesafety` (T134) closes M19 (T125→T134). Next: M20 (T135 Execution Contract).
