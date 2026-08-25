# TASK-230 — Test Report

## Tests (mới)
- `test_resolver_resolves_declared_and_registered`: resolve `code_read` → `["tool-x"]`.
- `test_resolver_fails_when_not_declared`: không khai báo → CoderAgentError.
- `test_resolver_fails_when_not_registered`: không đăng ký → CoderAgentError.

## Kết quả
```
python -m pytest aios/coder/tests/test_coder.py -q
15 passed
```
## Architecture gate: 124 passed.
