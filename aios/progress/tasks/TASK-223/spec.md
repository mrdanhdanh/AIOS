# TASK-223 — AIOS Planner Agent + Skill (nhận lệnh → plan.yaml)

## Mục tiêu
Đóng vòng lặp thực tế: người dùng ra lệnh (bằng tiếng Việt) → một **agent/skill** tiếp nhận, phân tích, và sinh ra file `plan.yaml` chuẩn `WorkflowDefinition` (có `command` ở mỗi node) → user chạy `aiagent execute plan.yaml` (TASK-222) để AIOS tự thực thi. Không cần LLM trong AIOS, không API ngoài — "não" là Copilot/OpenCode, AIOS làm "đôi tay".

## Phạm vi (In scope)
- Agent `.github/agents/aios-planner.agent.md` — chuyên trách nhận yêu cầu, sinh `plan.yaml` (I/O-free, chỉ text).
- Skill `.github/skills/aios-plan/SKILL.md` — slash command `/aios-plan <yêu cầu>` hướng dẫn format plan + gọi `aiagent execute`.
- Template plan mẫu + test xác thực agent sinh plan hợp lệ (validate qua `WorkflowDefinition.from_file`).

## Phạm vi (Out of scope)
- Không sửa runtime/executor (đã xong ở TASK-222).
- Không gọi LLM trong AIOS (agent chạy trên Copilot/OpenCode).

## Acceptance Criteria
| AC | Mô tả | Evidence |
|----|-------|----------|
| AC1 | Agent sinh `plan.yaml` có `workflow.name/version/nodes[].command/permissions` | file + validate |
| AC2 | `aiagent validate plan.yaml` (TASK-008) PASS với plan do agent sinh | terminal |
| AC3 | Plan có thể chạy qua `aiagent execute plan.yaml` (TASK-222) | integration |
| AC4 | Skill `/aios-plan` hướng dẫn đúng format + link TASK-222 | SKILL.md |
| AC5 | Test tự động: agent prompt sinh plan → `WorkflowDefinition.from_file` không raise | test |
| AC6 | Architecture gate 0 violations (agent/skill không import runtime internals) | arch gate |

## Schema plan.yaml (chuẩn WorkflowDefinition, TASK-222)
```yaml
workflow:
  name: <tên>
  version: 0.1.0
  permissions: [process.execute]
  nodes:
    - id: step-1
      type: task
      command: echo "..."      # lệnh shell/git thật
    - id: step-2
      type: task
      command: git status
```
