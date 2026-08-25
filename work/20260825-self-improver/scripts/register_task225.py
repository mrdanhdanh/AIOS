#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Register TASK-225 (AIOS Self-Improver Agent) into the AIOS governance records.

Updates:
  - docs/AIOS_Master_Task_Specification_M0-M26.md  (header count + TASK-225 block)
  - aios/progress/PLAN.md                          (TASK-225 row)
  - aios/progress/STATS.md                         (task counts)

Pure text transforms; no LLM, no network. Idempotent-ish (guards if already present).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MASTER = REPO / "docs" / "AIOS_Master_Task_Specification_M0-M26.md"
PLAN = REPO / "aios" / "progress" / "PLAN.md"
STATS = REPO / "aios" / "progress" / "STATS.md"

TASK225_BLOCK = """## TASK-225 — AIOS Self-Improver Agent

> **Trạng thái thực tế (2026-08-25):** DONE — `aios/agents/self_improver.py` (`SelfImproverAgent`, pure/I/O-free, capability-injected) + `aios/agents/tests/test_self_improver.py` (**4 automated tests**); `.github/agents/aios-self-improver.agent.md`; full suite 3161+ passed; Unified Gate PASS.

**Mục tiêu**  
Bổ sung lớp **Self-Improver** cho phép AIOS phản tư vận hành của chính nó (EvidenceStore + regression log) và ĐỀ XUẤT (không tự áp dụng) task cải tiến nội bộ, đẩy qua pipeline 7-gate như mọi task. Đây là bước "nâng cấp bản thân" — AIOS biết nhận diện điểm yếu của chính nó một cách deterministic, fail-closed.

**Phạm vi**
- `aios/agents/self_improver.py`: `SelfImproverAgent` nhận `evidence_store` + `registry` (capability-injected), quét tín hiệu FAIL/UNKNOWN, tổng hợp theo producer, sinh `ImprovementProposal` (spec sẵn sàng đưa vào governance). Không import `subprocess`/`os`/provider/filesystem (ARCH-001..004).
- `aios/agents/__init__.py`: export `SelfImproverAgent`, `SelfImproverResult`, `ImprovementProposal`.
- `aios/agents/tests/test_self_improver.py`: pure / fail-closed / deterministic / propose_next.
- `.github/agents/aios-self-improver.agent.md`: chat agent chọn từ picker, tự chạy vòng phản tư.

**Deliverables**
- `aios/agents/self_improver.py` + test + chat agent + task artifacts + evidence.

**Acceptance Criteria**
- Pure: 0 vi phạm ARCH-001..004 (architecture gate PASS).
- Capability-injected: chỉ qua interface, không tự làm I/O.
- Deterministic: cùng input -> cùng proposal.
- Fail-closed: thiếu evidence -> không đề xuất (trả None), không đoán.
- Đề xuất ở dạng spec text, KHÔNG ghi thẳng vào `aios/`.
- 7-gate PASS, full suite không regress.

**Dependency / Gate**
- TASK-220 (CoordinatorAgent), TASK-001 (lifecycle/gates), TASK-005 (evidence).
- Milestone M28 (self-evolution / metacognition).

---
"""


def patch_master() -> None:
    t = MASTER.read_text(encoding="utf-8")
    if "TASK-225" in t:
        print("master spec already has TASK-225; skipping block insert")
    else:
        t = t.replace("224/224 task DONE", "225/225 task DONE")
        t = t.replace(
            "(TASK-001 → TASK-218 + TASK-219 + TASK-220 + TASK-221 + TASK-222 + TASK-223 + TASK-224)",
            "(TASK-001 → TASK-218 + TASK-219 + TASK-220 + TASK-221 + TASK-222 + TASK-223 + TASK-224 + TASK-225)",
        )
        # Insert TASK-225 block right before "# M12".
        anchor = "\n---\n\n# M12"
        assert anchor in t, "M12 anchor not found in master spec"
        t = t.replace(anchor, "\n---\n\n" + TASK225_BLOCK + "# M12", 1)
        MASTER.write_text(t, encoding="utf-8")
        print("master spec: TASK-225 block inserted")


def patch_plan() -> None:
    t = PLAN.read_text(encoding="utf-8")
    if "TASK-225" in t:
        print("PLAN.md already has TASK-225; skipping")
        return
    row = "| TASK-224 | M27 | Planner confirm flow + `work/` directory convention | TASK-223,TASK-222 | DONE |\n"
    new_row = row + "| TASK-225 | M28 | AIOS Self-Improver Agent | TASK-220,TASK-001,TASK-005 | DONE |\n"
    assert row in t, "TASK-224 row not found in PLAN.md"
    t = t.replace(row, new_row, 1)
    PLAN.write_text(t, encoding="utf-8")
    print("PLAN.md: TASK-225 row inserted")


def patch_stats() -> None:
    t = STATS.read_text(encoding="utf-8")
    t = t.replace("| Total tasks (master spec) | 224 |", "| Total tasks (master spec) | 225 |")
    t = t.replace("| Tasks DONE | 224 |", "| Tasks DONE | 225 |")
    STATS.write_text(t, encoding="utf-8")
    print("STATS.md: counts updated to 225")


def main() -> int:
    for p in (MASTER, PLAN, STATS):
        if not p.is_file():
            print(f"MISSING: {p}", file=sys.stderr)
            return 1
    patch_master()
    patch_plan()
    patch_stats()
    print("REGISTER TASK-225 OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
