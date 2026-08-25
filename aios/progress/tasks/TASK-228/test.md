# TASK-228 — Test Report

## Unit tests (mới)
- `test_to_execution_plan_carries_governance_fields`: verify `contract`/`policy_ref`/`permissions` trong plan metadata; `permission`/`evidence_ref`/`cwd`/`tool_type` trong step metadata.
- `test_execution_plan_round_trip_lossless`: verify `from_execution_plan` giữ name/version/permissions/nodes; re-convert lossless cho id/command.

## Kết quả
```
python -m pytest aios/runtime/tests/test_workflow.py -q -k "execution_plan or round_trip"
.. 2 passed
```

## Architecture gate
```
python -m pytest aios/governance/architecture -q
124 passed
```

## Full suite regression
Đang chạy (xem evaluation.md).
