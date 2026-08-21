#!/usr/bin/env python3
"""Normalize AIOS detailtask specs (T017-050) to a consistent governance format.

For every `# TASK-0XX` region in each detailtask file it will:
  1. Insert a `## 1. Metadata` block right after the task heading (if missing).
  2. Renumber any `AC-XXX-YY` acceptance headings to `AC-0XX-YY`.
  3. Convert bullet lines inside the Acceptance Criteria section into
     `#### AC-0XX-NN — <short name>` numbered, testable criteria.
  4. Ensure a `## Dependency` section exists (append canonical DAG if missing).

Run:  python .review/norm.py            # all 017-050 files
      python .review/norm.py T020-022    # only one file (basename without .md)
"""
from __future__ import annotations
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DETAIL = os.path.join(ROOT, "docs", "detailtask")

# tasknum (3-digit) -> (title_viet, milestone, canonical_obj, dep_tasknum, priority)
TITLE = {
    "017": "FastAPI REST + WebSocket", "018": "Dashboard SPA", "019": "VS Code Extension",
    "020": "Upgrade Pipeline", "021": "Observability + Architecture Health", "022": "Orchestrator v2",
    "023": "Memory Coordinator", "024": "Context Optimizer", "025": "Model Router",
    "026": "Planning Engine", "027": "Execution Graph", "028": "Parallel Scheduler",
    "029": "Harness Kernel + Contract + Registry + Run", "030": "Execution Verification + Evidence + Replay",
    "031": "Test Harness + Scenario + Simulation", "032": "Evaluation Harness + Metrics",
    "033": "Benchmark + Regression Gate", "034": "Doctor + Readiness",
    "035": "Identity + Principal + RBAC/ABAC", "036": "Multi-Tenancy + Tenant Boundary",
    "037": "Distributed Runtime + Runtime Node", "038": "Distributed Scheduler + Lease + Failover",
    "039": "Quota + Cost + Resource Governance", "040": "Credential + Network + Sandbox Isolation",
    "041": "HA + Audit + Recovery", "042": "Enterprise Operations + Dashboard",
    "043": "Public AIOS SDK", "044": "Plugin Runtime", "045": "Extension Contracts",
    "046": "Ecosystem Registry", "047": "Developer Kit", "048": "Ecosystem Hub",
    "049": "Certification", "050": "Autonomous Goal Engine",
}
MS = {**{k: "M3 — Desktop Edition" for k in ["017", "018", "019"]},
      **{k: "M4 — Platform Edition" for k in ["020", "021", "022"]},
      **{k: "M5 — Core Intelligence" for k in ["023", "024", "025", "026", "027", "028"]},
      **{k: "M6 — AIOS Harness" for k in ["029", "030", "031", "032", "033", "034"]},
      **{k: "M7 — Enterprise" for k in ["035", "036", "037", "038", "039", "040", "041"]},
      **{k: "M8 — Ecosystem + Autonomy" for k in ["042", "043", "044", "045", "046", "047", "048", "049", "050"]}}
CANON = {
    "017": "Mở Runtime/Orchestrator qua API ổn định (REST + WebSocket, auth boundary, error model).",
    "018": "Xây operational UI thống nhất (10 view) phản ánh state thật; mọi action đi qua API/Runtime.",
    "019": "Đưa AIOS vào coding workspace; extension là client thuần, không chứa business logic riêng.",
    "020": "Xây upgrade/migration an toàn (resolve→backup→migrate→validate→rollback; dry-run).",
    "021": "Quan sát runtime và kiến trúc (metrics, audit, doctor, architecture health).",
    "022": "Nâng Orchestrator thành control plane có evaluation và improvement có kiểm soát.",
    "023": "Điều phối 4 loại memory và isolation; tích hợp Runtime/Harness hiện có.",
    "024": "Tối ưu context theo relevance, budget và lifecycle.",
    "025": "Chọn model theo policy, capability, cost và health.",
    "026": "Tạo/validate execution plan đa bước.",
    "027": "Biên dịch plan thành DAG acyclic, deterministic, policy-aware.",
    "028": "Chạy DAG song song trong resource/policy boundaries.",
    "029": "Kernel Harness độc lập với Runtime (contract/registry/run/lifecycle).",
    "030": "Xác minh execution và tạo evidence có thể replay.",
    "031": "Chạy scenario deterministic và simulation.",
    "032": "Đánh giá output và trajectory bằng evaluator suite.",
    "033": "Benchmark + Regression Gate cho toàn bộ hệ thống.",
    "034": "Nâng aiagent doctor + arch-health thành Doctor Harness; Readiness fail-closed.",
    "035": "Identity & Authorization Foundation (Principal, RBAC/ABAC, fail-closed).",
    "036": "Multi-Tenancy + Tenant Boundary cô lập xuyên runtime/data.",
    "037": "Distributed Runtime + Runtime Node (single→multi instance).",
    "038": "Distributed Scheduler + Lease + Failover.",
    "039": "Quota + Cost + Resource Governance.",
    "040": "Credential + Network + Sandbox Isolation.",
    "041": "HA + Audit + Recovery.",
    "042": "Enterprise Operations + Dashboard.",
    "043": "Public AIOS SDK (Python/TS, contract compatibility).",
    "044": "Plugin Runtime (lifecycle, sandbox, isolation).",
    "045": "Extension Contracts (public interface chuẩn hóa).",
    "046": "Ecosystem Registry.",
    "047": "Developer Kit.",
    "048": "Ecosystem Hub.",
    "049": "Certification.",
    "050": "Autonomous Goal Engine (goal lifecycle/control substrate).",
}
DEP = {f"{n:03d}": (f"{n - 1:03d}" if n - 1 >= 17 else None) for n in range(17, 51)}
PRI = {**{k: "Critical" for k in ["017", "035", "041", "050"]},
       **{k: "High" for k in TITLE if k not in ["017", "035", "041", "050"]}}


CHECKBOX = re.compile(r"^\s*[\*\-]?\s*\[[ xX]\]\s*(.*)$")

def clean_bullet(line: str) -> str:
    """Return (is_bullet, clean_text) for a top-level bullet/checkbox line."""
    m = re.match(r"^\s*[\*\-]\s+(.*)$", line)
    if m:
        txt = m.group(1)
        cb = CHECKBOX.match(line)
        if cb:
            txt = cb.group(1)
        return True, txt
    cb = CHECKBOX.match(line)
    if cb:
        return True, cb.group(1)
    return False, line


def make_name(s: str) -> str:
    s = re.sub(r"[`*_#\[\]]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    words = s.split()
    name = " ".join(words[:8])
    if len(name) > 64:
        name = name[:61].rstrip() + "..."
    return name or "criterion"


TASK_HEADING = re.compile(r"^#{1,4}\s+TASK-(\d+)\s*[—-]\s*(.+?)\s*$", re.MULTILINE)
AC_HEADING_RE = re.compile(r"^(#{1,4})\s+AC\s+(\d{1,3})(?:-(\d{1,3}))?\s*(.*)$", re.MULTILINE)


def normalize_region(region: str, tasknum: str) -> str:
    lines = region.split("\n")
    out: list[str] = []
    i = 0
    # 1) metadata insertion after first line
    if i < len(lines):
        out.append(lines[i])
        i += 1
        if "## 1. Metadata" not in region:
            meta = [
                "", "## 1. Metadata", "",
                f"* **Milestone:** {MS[tasknum]}",
                f"* **Task ID:** TASK-{tasknum}",
                f"* **Tên:** {TITLE[tasknum]}",
                f"* **Mục tiêu canonical:** {CANON[tasknum]}",
            ]
            if DEP[tasknum]:
                meta.append(f"* **Dependency trực tiếp:** TASK-{DEP[tasknum]} — {TITLE.get(DEP[tasknum],'')}")
            else:
                meta.append("* **Dependency trực tiếp:** M2 foundation (TASK-016)")
            meta.append(f"* **Priority:** {PRI[tasknum]}")
            meta.append("* **Status:** PLANNED")
            meta.append("* **Execution model:** Runtime-first · Policy-first · Evidence-first · Fail-closed")
            meta.append("")
            out.extend(meta)

    ac_active = False
    ac_level = 0
    seen_ac = False
    nn = 0
    in_fence = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line); i += 1; continue
        if not in_fence and re.match(r"^#{1,4}\s", line):
            m = re.match(r"^#{1,4}\s+(.*)$", line)
            head = m.group(1) if m else ""
            if re.search(r"acceptance criteria", head, re.I) or re.search(r"ACCEPTANCE CRITERIA", head, re.I):
                ac_active = True
                ac_level = len(line) - len(line.lstrip("#"))
                out.append(line); i += 1; continue
            elif re.match(r"^#{1,4}\s+AC-\d", line):
                # already an AC heading: stop promoting further bullets
                seen_ac = True
                new = re.sub(r"AC-\d{3}-", f"AC-{tasknum}-", line)
                out.append(new); i += 1; continue
            else:
                # any other heading ends the AC region
                ac_active = False
                out.append(line); i += 1; continue
        if ac_active and not in_fence and not seen_ac:
            is_b, txt = clean_bullet(line)
            if is_b and not re.match(r"^\s*[\*\-]\s+[\*\-]\s", line):
                nn += 1
                out.append(f"#### AC-{tasknum}-{nn:02d} — {make_name(txt)}")
                if txt.strip():
                    out.append(txt.strip())
                i += 1; continue
        out.append(line); i += 1

    text = "\n".join(out)
    # 2) renumber any stray AC-XXX-YY / AC-NNN headings inside region (preserve level + spacing)
    def _ren(mt):
        nn = mt.group(3) if mt.group(3) is not None else mt.group(2)
        return f"{mt.group(1)} AC-{tasknum}-{int(nn):02d} {mt.group(4)}"
    text = AC_HEADING_RE.sub(_ren, text)
    # 4) ensure Dependency section exists
    if not re.search(r"^#{1,4}\s+.*dependency.*$", text, re.I | re.MULTILINE):
        if DEP[tasknum]:
            dep_line = f"TASK-{DEP[tasknum]} — {TITLE.get(DEP[tasknum],'')}\n        ↓\n     TASK-{tasknum}"
        else:
            dep_line = f"M2 foundation (TASK-016)\n        ↓\n     TASK-{tasknum}"
        text = text.rstrip() + "\n\n---\n\n## Dependency\n\n```text\n" + dep_line + "\n```\n"
    return text


def process_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    heads = list(TASK_HEADING.finditer(text))
    if not heads:
        return False
    parts = []
    for idx, h in enumerate(heads):
        start = h.start()
        end = heads[idx + 1].start() if idx + 1 < len(heads) else len(text)
        region = text[start:end]
        tasknum = h.group(1)
        if tasknum not in TITLE:
            parts.append(region)
            continue
        parts.append(normalize_region(region, tasknum))
    new_text = "".join(parts)
    if new_text.strip() != text.strip():
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)
        return True
    return False


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    files = sorted(os.listdir(DETAIL))
    changed = []
    for fn in files:
        if not fn.endswith(".md"):
            continue
        m = re.match(r"^T0(1[7-9]|[2-4]\d|50)", fn)  # T017..T050
        if not m:
            continue
        base = fn[:-3]
        if only and base != only:
            continue
        p = os.path.join(DETAIL, fn)
        if process_file(p):
            changed.append(fn)
    print("Changed:", changed)


if __name__ == "__main__":
    main()
