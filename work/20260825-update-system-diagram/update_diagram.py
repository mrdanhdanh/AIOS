# -*- coding: utf-8 -*-
"""Update docs/AIOS_System_Diagram.md to the post-M26 state (2026-08-25).

Adds TASK-220..224, coding_edition/, Coordinator Agent, Real Executor,
Planner Loop; refreshes dates and CLOSED notes. Idempotent guard at top.
"""
import pathlib, sys

# Compute repo root from this file's location (no hardcoded absolute paths).
REPO = pathlib.Path(__file__).resolve().parents[2]
P = REPO / "docs" / "AIOS_System_Diagram.md"
s = P.read_text(encoding="utf-8")

def grepl(old, new):
    global s
    if old not in s:
        print("MISSING (global):", repr(old)); sys.exit(1)
    s = s.replace(old, new)

def onerepl(old, new):
    global s
    n = s.count(old)
    if n != 1:
        print(f"EXPECTED 1 got {n}:", repr(old)); sys.exit(1)
    s = s.replace(old, new)

# Idempotency guard
if "TASK-220→224" in s and "coding_edition/" in s:
    print("ALREADY APPLIED - no changes made")
    sys.exit(0)

# ---- Global phrase replacements ----
grepl("2026-08-24", "2026-08-25")
grepl("M0–M26 đã DONE", "M0–M26 + TASK-220→224 đã DONE")
grepl("M0–M26 CLOSED", "M0–M26 + T220–224 CLOSED")
grepl("M0–M26 đã hoàn tất", "M0–M26 + TASK-220→224 đã hoàn tất")
grepl("TASK-001 → TASK-218 + TASK-219", "TASK-001 → TASK-219 + TASK-220 → TASK-224")
grepl("M0 → M26 đã DONE", "M0 → M26 + T220–224 đã DONE")

# ---- Structural edits ----
# Section 1 mermaid: Layer 5 add Coordinator Agent
onerepl(
'''    subgraph L5["Layer 5 — AGENT (pure, I/O-free)"]
        A1["Spec-Writer · Critic · Reviewer"]
        A2["Orchestrator Agent v2"]
        A3["Autonomous Goal Engine"]
    end''',
'''    subgraph L5["Layer 5 — AGENT (pure, I/O-free)"]
        A1["Spec-Writer · Critic · Reviewer"]
        A2["Orchestrator Agent v2"]
        A3["Autonomous Goal Engine"]
        A4["Coordinator Agent (T220/221)<br/>spec→critique×2→review→close"]
    end''')

# Section 1 mermaid: Runtime R5 add RealToolHandler
onerepl(
'''        R5["Executor"]
        R6["Model Router · Providers"]''',
'''        R5["Executor + RealToolHandler<br/>(T222 real OS exec, opt-in)"]
        R6["Model Router · Providers"]''')

# Section 1 mermaid: wiring add A4 --> A2
onerepl(
'''    A2 --> O1 --> R1 --> C1 --> T1
    A3 -.->|objectives| O3''',
'''    A2 --> O1 --> R1 --> C1 --> T1
    A4 --> A2
    A3 -.->|objectives| O3''')

# Cross-cutting planes table: update Coding Plane + add Practical Loop
onerepl(
'''| Coding Plane | `coder/` |''',
'''| Coding Plane | `coder/`, `coding_edition/` (AIOS 2.0 — T197–218) |
| Practical Loop | `agents/coordinator.py` (T220/221) · `runtime/process.py` (T222) · `.github/skills/aios-plan/` (T223/224) |''')

# Monorepo: agents line
onerepl(
"  agents/              orchestrator, spec_writer, critic, reviewer",
"  agents/              orchestrator, spec_writer, critic, reviewer, coordinator (T220/221)")

# Monorepo: runtime line
onerepl(
"  runtime/             kernel, context, audit, artifact, permission,",
"  runtime/             kernel, context, audit, artifact, permission, process (T222 real exec),")

# Monorepo: add coding_edition after coder
onerepl(
"  coder/               (T125-T127) coder agent + coding planner + generation runtime",
"  coder/               (T125-T127) coder agent + coding planner + generation runtime\n  coding_edition/      (T197-T218) AIOS 2.0 Unified Coding Plane (contract/state/policy/risk/regression)")

# Monorepo: add Practical Loop comment after progress line
onerepl(
"  progress/            PLAN.md LOG.md STATS.md tasks/<TASK-xxx>/ _TEMPLATE/",
"  progress/            PLAN.md LOG.md STATS.md tasks/<TASK-xxx>/ _TEMPLATE/\n  # Practical AIOS Loop (T220-T224): agents/coordinator.py, runtime/process.py,\n  #   .github/skills/aios-plan/ (Planner Agent), work/YYYYMMDD-slug/ plan convention")

# Section 8 table: add T220-224 rows after M26
onerepl(
"| M26 | Unified Coding Plane (Final Milestone) | TASK-197 → 218 | DONE |",
"| M26 | Unified Coding Plane (Final Milestone) | TASK-197 → 218 | DONE |\n| — | Coordinator Agent (control-plane + chat endpoint) | TASK-220, TASK-221 | DONE |\n| — | AIOS Real Executor + `aiagent execute` CLI | TASK-222 | DONE |\n| — | AIOS Planner Agent + Skill (request→plan.yaml) | TASK-223 | DONE |\n| — | Planner confirm flow + `work/` directory convention | TASK-224 | DONE |")

# Section 8 note2: update task count
onerepl(
"toàn bộ 218 tasks + TASK-219 `DONE`. Không còn milestone PLANNED.",
"toàn bộ 218 tasks + TASK-219 + TASK-220 → TASK-224 `DONE`. Không còn milestone PLANNED.")

# Section 9 CLI: add execute/task commands note (anchor on section 10 header)
onerepl(
"```\n\n---\n\n## 10. Lộ trình tương lai — Roadmap M10 → M26",
"```\n\n> **Thực thi thật (T220–T224):** `aiagent execute <plan.yaml> --work-dir <dir> --yes` (Real Executor, opt-in `AIOS_REAL_EXECUTION_ENABLED`); `aiagent task <TASK-id>` chạy full pipeline + 7 governance gates.\n\n---\n\n## 10. Lộ trình tương lai — Roadmap M10 → M26")

# Section 10 mermaid: add PX node + style
onerepl(
'''    M25 --> M26[M26 Unified Coding Contract<br/>+ Coding SM + Policy]

    style M9 fill:#10b981,color:#fff''',
'''    M25 --> M26[M26 Unified Coding Contract<br/>+ Coding SM + Policy]
    M26 --> PX[Practical AIOS Loop<br/>Planner→plan.yaml→confirm→Real Exec<br/>T220-T224 DONE]

    style M9 fill:#10b981,color:#fff
    style PX fill:#0ea5e9,color:#fff''')

# Section 10 milestone map: add T220-224 row
onerepl(
"| M26 | Unified Coding Plane | T197 → 218 | DONE |",
"| M26 | Unified Coding Plane | T197 → 218 | DONE |\n| T220–224 | Practical AIOS Loop (Coordinator / Real Executor / Planner) | T220 → 224 | DONE |")

# Section 11 mermaid: add PRAC subgraph + wiring
onerepl(
'''    UX --> API --> ORC
    ORC --> RT --> CAP''',
'''    subgraph PRAC["Practical AIOS Loop (T220–T224)"]
        CO[Coordinator Agent<br/>spec→critique×2→review→close]
        PLN[Planner Agent<br/>request→plan.yaml]
        REX[Real Executor<br/>aiagent execute (opt-in)]
    end

    UX --> API --> ORC
    ORC --> RT --> CAP
    PLN -.->|plan.yaml| REX
    CO -.->|coordinate| ORC
    REX -.->|real OS exec| RT''')

# Section 11 mermaid: add styles
onerepl(
'''    style UG fill:#8b5cf6,color:#fff
    style ORACLE fill:#8b5cf6,color:#fff
    style HAR fill:#0ea5e9,color:#fff
    style GOV2 fill:#ef4444,color:#fff
    style RT fill:#10b981,color:#fff''',
'''    style UG fill:#8b5cf6,color:#fff
    style ORACLE fill:#8b5cf6,color:#fff
    style HAR fill:#0ea5e9,color:#fff
    style GOV2 fill:#ef4444,color:#fff
    style RT fill:#10b981,color:#fff
    style CO fill:#f59e0b,color:#fff
    style PLN fill:#0ea5e9,color:#fff
    style REX fill:#10b981,color:#fff''')

# Footer
onerepl(
"*Tài liệu được sinh tự động từ source tree AIOS — cập nhật khi có milestone mới.*",
"*Tài liệu được sinh tự động từ source tree AIOS — cập nhật 2026-08-25 (thêm TASK-220→224, coding_edition/, Coordinator Agent, Real Executor, Planner Loop).*")

P.write_text(s, encoding="utf-8")
print("OK: AIOS_System_Diagram.md updated to 2026-08-25 (TASK-220→224, coding_edition, Coordinator, Real Executor, Planner Loop)")
