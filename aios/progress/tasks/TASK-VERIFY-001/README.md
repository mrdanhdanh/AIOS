# TASK-VERIFY-001 — Reference / Documentation Task

This task folder is **intentionally kept** as a living reference for the standard
AIOS job workflow. It was created from `aios/progress/tasks/_TEMPLATE` and driven
end-to-end through `aiagent task TASK-VERIFY-001`, proving that:

- The full governance pipeline runs: `spec → critique×2 → breakdown → review → orchestrate`.
- The 7 governance gates (lifecycle · architecture · registry · dependency ·
  evidence · test_evaluate · regression) pass.
- The `orchestrate` step uses the **real** `Orchestrator` and closes the task to `DONE`
  when all mandatory artifacts are present and the unified gate passes.
- A durable log is written to `work/20260825-job-verify/logs/task-TASK-VERIFY-001-*.json`.

## How to reproduce

```bash
# From repo root
python work/20260825-job-verify/scripts/run_task.py TASK-VERIFY-001 \
    --job-dir work/20260825-job-verify/logs
# or via the CLI entry point
aiagent task TASK-VERIFY-001 --job-dir work/20260825-job-verify/logs
```

## Layout

This folder follows the standard lifecycle artifact layout
(`STATE_ARTIFACTS`): `spec.md`, `critique-1.md`, `critique-2.md`, `tasks.md`,
`review.md`, `implementation/`, `test.md`, `evaluation.md`, `REGRESSION.md`.

> Note: this is a documentation artifact, not a scheduled deliverable. Do not
> deprecate or reuse its ID for production work.
