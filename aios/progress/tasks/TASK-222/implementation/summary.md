# TASK-222 Implementation Summary

## Files changed
1. `aios/runtime/process.py` (NEW)
   - `RealToolHandler` — `StepHandler` chạy lệnh thật qua `subprocess`, timeout + killpg cross-platform (Windows `CTRL_BREAK_EVENT` / POSIX `killpg`), re-check `PermissionBroker` trước exec.
   - `SCOPE_MAP` — map config scope string → `PermissionScope`.
   - `load_real_execution_config()` — đọc `configs/default.yaml` `real_execution` section.
   - `record_execution_evidence()` — ghi provenance chain (Requirement→Task→Artifact→Run→Evidence).

2. `aios/runtime/workflow/definition.py` (MODIFY)
   - `WorkflowNode.command` field (optional, backward compatible).
   - `WorkflowDefinition.to_execution_plan()` — nodes → `ExecutionPlan` steps (gán scope/resource/command/cwd/timeout).
   - `WorkflowDefinition.from_markdown()` — parse `- [ ]` lines thành nodes.

3. `aios/runtime/kernel.py` (MODIFY)
   - `RuntimeKernel(real_execution=...)` param + `_read_real_exec_env()`.
   - `_wire()` grant `PermissionBroker` + register `RealToolHandler` khi enabled.
   - `execute_plan()` + `real_tool_handler` property.

4. `aios/cli/workflow_cli.py` (MODIFY)
   - Subcommand `execute` (`--simulate`, `--timeout`).

5. `configs/default.yaml` (MODIFY)
   - Thêm `real_execution:` section (`enabled: false` mặc định).

## Usage
```bash
# Bật real execution (opt-in)
# configs/default.yaml: real_execution.enabled: true
aiagent execute plan.yaml          # chạy thật
aiagent execute plan.md --simulate # chỉ validate, 0 LLM, 0 exec
```
