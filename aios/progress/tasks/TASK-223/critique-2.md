# TASK-223 — Critique vòng 2

## Xác nhận
- Agent `.github/agents/aios-planner.agent.md` là VS Code agent (không phải `aios/agents/` Python) → ARCH-001..004 không áp dụng, nhưng giữ I/O-free (chỉ sinh text plan). OK.
- Skill `.github/skills/aios-plan/SKILL.md` là plugin ecosystem (M8) → hợp lệ.
- Schema plan.yaml khớp `WorkflowDefinition` (TASK-008) + `command` field (TASK-222). OK.

## Cải tiến
1. Agent phải luôn ghi file `plan.yaml` ra đĩa (dùng tool `write_file` của VS Code) thay vì chỉ in codeblock — để user chạy ngay `aiagent execute plan.yaml`.
2. Skill hướng dẫn: sau khi có plan.yaml → `aiagent execute plan.yaml` (bật `real_execution.enabled: true`).
3. Test (AC5): parse output của agent (hoặc file mẫu) qua `WorkflowDefinition.from_file` để đảm bảo không raise.

## Kết luận
Sẵn sàng IMPLEMENT.
