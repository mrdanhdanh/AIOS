# Implementation — TASK-002 (Monorepo + aios_core Scaffold)

Real artifacts for this task:

- `aios_core.py` — re-export của `aios.core` scaffold (Rule 3 compliant: không import
  os/pathlib/subprocess/provider trực tiếp).
- `test_aios_core.py` — pytest cho artifact (path resolution dùng string-only, không os/pathlib).

Deliverable thực tế nằm ở `aios/core/`, `aios/runtime/`, `aios/harness/` (skeleton packages).
Mọi PASS claim được ghi nhận trong `../EVIDENCE.md` (E-001).
