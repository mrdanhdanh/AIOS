# TASK-224 — Planner confirm flow + `work/` directory convention

## Mục tiêu
Cải tiến luồng thực tế AIOS theo phản hồi user:
1. **Confirm trước khi thực thi**: sau khi sinh `plan.yaml`, agent/skill HỎI user có muốn
   chạy không. Chỉ khi user đồng ý mới gọi terminal chạy `aiagent execute`.
2. **Quy ước vị trí file**: tại repo root tạo folder `work/`. Mỗi việc = 1 subfolder
   `YYYYMMDD-tenngan` (vd `20260824-webno1`). `plan.yaml` + mọi source sinh ra đều nằm
   trong folder đó.

## Phạm vi (In scope)
- Cập nhật `.github/agents/aios-planner.agent.md` + `.github/skills/aios-plan/SKILL.md`:
  hỏi confirm + quy ước `work/YYYYMMDD-tenngan/`.
- `aios/cli/workflow_cli.py` `_cmd_execute`: thêm `--work-dir <dir>` (tạo folder nếu chưa có,
  đặt plan vào đó, chạy với `allowed_cwd` = folder đó) + `--yes` (bỏ qua confirm khi gọi từ
  script/agent). Khi không có `--yes` và chạy interactive → in prompt xác nhận (nhưng CLI
  chính thức vẫn để agent hỏi trước khi gọi).
- Test: work-dir tạo đúng folder, plan nằm trong, execute chạy được.

## Phạm vi (Out of scope)
- Không đổi executor (TASK-222) / planner sinh plan (TASK-223).
- Không gọi LLM trong AIOS.

## Acceptance Criteria
| AC | Mô tả | Evidence |
|----|-------|----------|
| AC1 | Agent sinh plan vào `work/YYYYMMDD-tenngan/plan.yaml` | agent.md + test |
| AC2 | Agent HỎI user "thực hiện không?" trước khi chạy | agent.md |
| AC3 | `aiagent execute plan.yaml --work-dir work/20260824-x` tạo folder, chạy, source trong đó | test |
| AC4 | `--yes` bỏ qua confirm (script/agent tự gọi) | test |
| AC5 | Architecture gate 0 violations | arch gate |
| AC6 | Full suite không regress | pytest |

## Quy ước
```
d:\AIOS\work\
  20260824-webno1\
    plan.yaml
    <source sinh ra>
  20260824-helloworld\
    plan.yaml
    ...
```
