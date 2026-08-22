# Test — TASK-084

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| breaking change | MAJOR + ADR + deprecation | PASS |
| compatible change | MINOR | PASS |
| fix | PATCH | PASS |
| deprecated không báo trước | bị chặn | PASS |
| cùng change type | cùng bump (deterministic) | PASS |
| version policy evidence | provenance đầy đủ | PASS |
| matrix 1.0 ↔ 1.x | compatible | PASS |
| bump_version | đúng SemVer | PASS |
| baseline_hash | deterministic | PASS |

`python -m pytest aios/versioning -q` → 9 passed.
