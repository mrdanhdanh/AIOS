# TASK-228 — Breakdown

## Sub-tasks
1. **T228.1** — Mở rộng `to_execution_plan` thêm `policy_ref`/`permission`/`evidence_ref` vào step + plan metadata (giữ tương thích ngược T222).
2. **T228.2** — Thêm `WorkflowDefinition.from_execution_plan` (converter 2 chiều, lossless cho id/command/cwd/permissions).
3. **T228.3** — Thêm test: governance fields present + round-trip lossless.
4. **T228.4** — Chạy architecture gate + pytest; đảm bảo full suite không regress.

## Phân công (agent-injected, pure)
- `aios/runtime/workflow/definition.py`: T228.1, T228.2
- `aios/runtime/tests/test_workflow.py`: T228.3
- Verification: `pytest aios/governance/architecture` + `pytest aios/runtime/tests/test_workflow.py`
