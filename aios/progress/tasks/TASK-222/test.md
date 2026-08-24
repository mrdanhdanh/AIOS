# TASK-222 — Test Plan

## Unit (`aios/runtime/tests/test_process.py`)
- `test_real_handler_runs_echo`: grant EXECUTE → chạy `echo hello` → output chứa "hello".
- `test_real_handler_denied_without_grant`: broker rỗng → `PermissionError` (AC2).
- `test_real_handler_timeout_kills_process`: chạy `python -c "import time; time.sleep(10)"` timeout=1 → `cf.TimeoutError` → step TIMEOUT, process bị kill (AC4).
- `test_scope_map`: `SCOPE_MAP` map đúng string→PermissionScope.

## Integration (`aios/cli/tests/test_execute.py`)
- Tạo `sample.yaml` (1 node `echo`, 1 node `git status`), bật `real_execution` qua env, chạy `aiagent execute sample.yaml` → PASS, artifact tạo.
- `aiagent execute sample.md --simulate` → 0 exec, in node list (AC7).
- `real_execution` tắt → `aiagent execute` trả exit 2 (AC3).

## Evidence (`aios/governance/evidence`)
- `test_execution_evidence_chain`: sau run, `get_provenance_chain` trả `complete=True` (AC5).

## Architecture
- `python -m pytest aios/governance/architecture -q` → 0 violations (AC6).
