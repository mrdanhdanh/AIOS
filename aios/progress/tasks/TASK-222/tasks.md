# TASK-222 — Task Breakdown

- [x] T1: Tạo `aios/runtime/process.py` + `RealToolHandler` (subprocess, timeout, killpg cross-platform, permission re-check)
- [x] T2: `PermissionBroker` grant từ `real_execution` config (kernel._wire)
- [x] T3: Wire `RealToolHandler` + `Kernel.execute_plan()` trong `kernel.py`
- [x] T4: Converter `WorkflowDefinition.to_execution_plan()` + `command` field + `from_markdown()`
- [x] T5: Subcommand `execute` trong `workflow_cli.py` (parse YAML/JSON/md, evidence)
- [x] T6: Markdown plan parser (`- [ ]` → nodes)
- [x] T7: Tạo task folder TASK-222 (spec/critique×2/tasks/review/impl/test/eval/regression)
- [x] T8: Unit tests `RealToolHandler` (mock subprocess, timeout/killpg, deny)
- [x] T9: Integration `aiagent execute sample.yaml` + evidence provenance
- [x] T10: Architecture gate 0 violations + `gate_check.py --task TASK-222` PASS
- [x] T11: Cập nhật `AGENTS.md` (xóa "M6 harness placeholder") + `progress/PLAN.md`/`LOG.md`/`STATS.md`
- [x] T12: Quy tắc 8 Auto-COMMIT (commit ngay trong phiên)
