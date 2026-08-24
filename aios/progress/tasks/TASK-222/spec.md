# TASK-222 — AIOS Real Executor + CLI `execute`

## Mục tiêu
Biến AIOS từ "hệ thống tự quản lý" thành "môi trường thực thi task thật" mà **không cần model/LLM và không cần API ngoài** (máy yếu). Copilot/OpenCode (đã có sẵn) đóng vai "não" lập plan; AIOS làm "đôi tay + hàng rào an toàn": thực thi plan qua **real tool executor** (shell/file/git) được **Policy/Permission** kiểm soát, ghi **evidence** chuẩn provenance chain.

## Phạm vi (In scope)
- Real execution trong `aios/runtime/` (shell, git, file write) có Policy/Permission pre-check (fail-closed).
- Subcommand `execute` MỚI trong `aios/cli/workflow_cli.py` (KHÔNG động `run` cũ — DX stability T071).
- Converter `WorkflowDefinition.to_execution_plan()` gán `scope`/`resource` để policy pre-check fire.
- Hỗ trợ plan YAML/JSON và Markdown (`- [ ]` lines).
- Evidence provenance chain đầy đủ (Evidence→Run→Artifact→Task→Requirement).
- Config `real_execution.enabled: false` mặc định (safe default, opt-in).

## Phạm vi (Out of scope)
- Gọi LLM/provider (OpenAI/Ollama/OpenCode API) — bỏ qua vì máy yếu + không API ngoài.
- Sửa `aios/tool/adapters.py` (giữ mock, tránh ARCH-004).
- LangGraph/MockCompiler workflow engine — không đổi.

## Acceptance Criteria
| AC | Mô tả | Evidence |
|----|-------|----------|
| AC1 | `aiagent execute sample.yaml` chạy plan có 1 node shell `echo` + 1 node `git status`, tạo file output | terminal output + artifact |
| AC2 | Step thiếu permission (broker không grant) → DENY fail-closed, không exec | audit/permission test |
| AC3 | `real_execution.enabled: false` → mọi exec bị chặn (safe default) | config test |
| AC4 | Timeout giữa step → subprocess bị kill (cross-platform Windows `CTRL_BREAK_EVENT` / POSIX `killpg`) | unit test |
| AC5 | Evidence provenance chain complete (5 registries) sau run | `get_provenance_chain` |
| AC6 | `python -m pytest aios/governance/architecture -q` → 0 violations | arch gate |
| AC7 | `aiagent execute sample.md --simulate` → chỉ validate, 0 LLM call, không exec | simulate flag |

## Kiến trúc
- `runtime` layer được phép I/O (ARCH-001..004 chỉ cấm agent/worker/skill). Real I/O CHỈ trong `aios/runtime/`.
- `Executor.execute(plan, handler)` đã có policy pre-check (scope/resource) + retry/timeout/cancel/audit.
- `PermissionBroker` bắt đầu rỗng → phải grant từ config khi `real_execution.enabled`.
