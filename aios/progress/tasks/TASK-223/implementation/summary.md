# TASK-223 Implementation Summary

## Files changed
1. `.github/agents/aios-planner.agent.md` (NEW)
   - Agent chuyên trách: nhận yêu cầu (VN) → phân tích → sinh `plan.yaml` chuẩn WorkflowDefinition (mỗi node 1 `command` shell/git thật) → ghi file qua tool `write_file` → hướng dẫn `aiagent execute`.
   - I/O-free về mặt AIOS layering (chỉ text + ghi file plan).

2. `.github/skills/aios-plan/SKILL.md` (NEW)
   - Slash `/aios-plan <yêu cầu>` — hướng dẫn format plan.yaml + link TASK-222 (`aiagent execute`).
   - Kèm ví dụ plan mẫu.

3. `aios/cli/tests/test_planner_agent.py` (NEW)
   - AC5: plan mẫu validate + execute được.

## Usage (vòng lặp thực tế)
```bash
# 1. User gõ yêu cầu cho AIOS Planner agent (hoặc /aios-plan "tạo file hello.txt")
# 2. Agent sinh plan.yaml
# 3. Bật real_execution (configs/default.yaml: enabled: true)
aiagent execute plan.yaml
```
