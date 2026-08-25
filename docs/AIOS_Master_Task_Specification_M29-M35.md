# AIOS — Master Task Specification (Phase 2.x: M29–M35)

## Operational Integration & Autonomous Coding OS

> **Trạng thái tài liệu (2026-08-25):** ROADMAP MỚI (chưa implement). M0–M26 + M27 (control-plane) + M28 (self-evolution) đã CLOSED (226 task DONE). Phase này thêm **11 task PLANNED** (TASK-227 → TASK-237) chia thành 7 milestone M29–M35. Mục tiêu KHÔNG phải thêm subsystem mới, mà **nối các plane đã có thành một control/execution/evidence loop thống nhất**, giữ nguyên mọi invariant + layering (`Agent → Orchestrator → Runtime → Capability → Tool`) và nguyên tắc fail-closed / Harness-Verified / Evidence-First.
>
> **Nguồn:** đề xuất tái cấu trúc từ audit `docs/AIOS_System_Diagram.md` §14 — xác nhận 2 lỗ hổng: (1) Flow B (`aiagent execute` thuần) **không chạy governance pipeline**, (2) Flow H (Coding Plane) **chỉ smoke-test**, chưa nối `Capability` + `RealToolHandler` (T222) với `CodingEdition`.

## 0. Rationale — tại sao phase này, tại sao không mở subsystem mới

Diagram hiện tại đã có gần như toàn bộ thành phần của một AI coding OS: Planner, Coordinator, Governance, Orchestrator, Coding Plane, Capability, Runtime, Real Execution, Observation, Verification, Evidence, Evaluation, Autonomous Recovery. Vấn đề không phải thiếu module — mà là **các flow còn tách rời**:

- `aiagent execute` (Flow B) chạy shell `command:` nhưng **bypass 7 governance gates**.
- `CodingEdition` (Flow H) load được offline nhưng **chưa sinh code thật** vì thiếu nối với `RealToolHandler` + `Capability`.
- Autonomous Loop / Recovery / Experimentation / Stuck Detection / Governor / Coding Loop **tồn tại rời rạc**, chưa hợp nhất thành 1 lifecycle.

Do đó phase này ưu tiên **integration > addition**. Mỗi milestone map vào module đã có; chỉ M29/M30 thêm "glue contract" để nối chúng.

## 1. Target Architecture (AIOS 2.x)

```
                    ┌──────────────────────┐
                    │      HUMAN / UI      │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │       GOAL           │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ PLANNER / ORCHESTRATOR│
                    └──────────┬───────────┘
                               ↓
              ┌────────────────────────────────┐
              │       GOVERNANCE PLANE         │
              │ Policy · Permission · Risk     │
              │ Approval · KillSwitch           │
              └───────────────┬────────────────┘
                              ↓
                    ┌──────────────────────┐
                    │    EXECUTION PLAN    │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │    CODING / AGENT    │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │     CAPABILITY       │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │       RUNTIME        │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │   REAL EXECUTION     │
                    └──────────┬───────────┘
                               ↓
             ┌─────────────────┴─────────────────┐
             ↓                                   ↓
       Observation                          Artifacts
             ↓                                   ↓
       Verification ───────────────→ Evidence
             ↓                                   ↓
         Evaluation ───────────────→ Knowledge
             ↓
       ┌─────┴─────┐
       ↓           ↓
     DONE        RECOVER
                   ↓
               REPLAN
                   ↓
                 LOOP
```

## 2. Priority Table

| Priority | Milestone | Trọng tâm |
|----------|-----------|-----------|
| 🔴 P0 | M29 | Unified Execution Plane |
| 🔴 P0 | M30 | Unified Coding Agent (Real Coding Plane) |
| 🔴 P0 | M31 | Autonomous Coding Loop |
| 🟠 P1 | M32 | Evidence-Native AIOS |
| 🟠 P1 | M33 | Autonomous Recovery & Self-Healing |
| 🟡 P2 | M34 | AIOS Control Center |
| 🟢 P3 | M35 | Self-Evolving AIOS |

> **Không làm M34 trước M29–M33.** UI hiện tại không phải bottleneck; Dashboard chỉ phản ánh state thật qua API (nguyên tắc hiện tại).

---

# M29 — Unified Execution Plane

**Mục tiêu:** biến `plan.yaml → execute` thành execution path chuẩn duy nhất. `aiagent execute` không còn là đường bypass Governance; mọi execution sinh `Run + Artifact + Evidence`; simulation và real execution dùng cùng một contract.

## TASK-227 — Unified ExecutionPlan Contract

> **Trạng thái thực tế (2026-08-25):** PLANNED — thuộc phase AIOS 2.x (M29). Chưa implement.

**Mục tiêu**  
Chuẩn hóa một schema `ExecutionPlan` duy nhất được dùng bởi CẢ `aiagent task` (Flow A) và `aiagent execute` (Flow B). Hiện Flow B parse `plan.yaml` → `WorkflowDefinition.to_execution_plan()` (T222) nhưng không qua governance; Flow A chạy qua `Orchestrator` + `UnifiedTaskGate`. Task này định nghĩa contract chung: `Planner → ExecutionPlan → Policy → Capability → Runtime`, sao cho cả hai entry-point sinh cùng cấu trúc execution có thể bị Policy/Permission pre-check.

**Phạm vi**
- Định nghĩa `ExecutionPlan` schema (nodes, scope, resource, permission, policy_ref, evidence_ref) trong `aios/runtime/workflow/` (kế thừa `to_execution_plan`).
- `aiagent execute` sinh `ExecutionPlan` chuẩn thay vì chạy shell trực tiếp; mọi node phải qua `PolicyEngine.check()` + `PermissionBroker`.
- Converter 2 chiều `WorkflowDefinition ↔ ExecutionPlan` giữ tương thích ngược (DX stability).
- Không thêm package mới — mở rộng `aios/runtime/workflow/definition.py` + `aios/runtime/kernel.py`.

**Deliverables**
- `aios/runtime/workflow/definition.py` (ExecutionPlan contract + converter) + test.
- `aios/runtime/kernel.py` (`execute_plan` dùng ExecutionPlan chuẩn, policy-checked).
- Task artifacts + evidence + ADR.

**Acceptance Criteria**
- `aiagent execute plan.yaml` sinh `ExecutionPlan` có `policy_ref` + `permission` cho mỗi node.
- Node thiếu permission → DENY fail-closed (giống Flow A).
- Converter `WorkflowDefinition ↔ ExecutionPlan` round-trip không mất trường.
- `python -m pytest aios/governance/architecture -q` → 0 violations (không import agent-layer).
- Full suite không regress.

**Dependency / Gate**
- TASK-222 (Real Executor + CLI execute), TASK-008 (workflow CLI), TASK-010 (Decision Pipeline / ExecutionPlan), TASK-001 (gates).
- Milestone M29.

---

## TASK-228 — Unified Execution Entry-Point (Governance-aware execute)

> **Trạng thái thực tế (2026-08-25):** PLANNED — thuộc phase AIOS 2.x (M29). Chưa implement.

**Mục tiêu**  
Biến `aiagent execute` thành entry-point hợp nhất: simulation và real execution dùng CÙNG contract; approval / permission / resource / sandbox nằm trong MỘT flow; mọi execution (dù simulate hay real) sinh `Run + Artifact + Evidence` với provenance chain đầy đủ. Đóng khoảng cách Flow A ∧ Flow B.

**Phạm vi**
- `aiagent execute` có chế độ mặc định chạy pre-check governance (Policy/Permission/Risk/Approval/KillSwitch) trước khi exec; flag `--no-govern` bị loại bỏ hoặc chỉ dành dev offline an toàn.
- Simulation (`--simulate`) dùng cùng `ExecutionPlan` contract, chỉ khác ở bước thực thi (dry-run), vẫn sinh Evidence (loại SIMULATED).
- Mọi execution ghi `Run` + `Artifact` + `Evidence` (provenance `Evidence→Run→Artifact→Task→Requirement`).
- Tích hợp `RetryGuard` (T226) vào loop thực thi để auto-stop khi lỗi lặp.

**Deliverables**
- `aios/cli/workflow_cli.py` (`execute` governance-aware) + test.
- `aios/runtime/kernel.py` (unified exec loop + evidence emission).
- Task artifacts + evidence + ADR.

**Acceptance Criteria**
- `aiagent execute plan.yaml` chạy pre-check governance trước exec (Policy/Permission PASS mới exec).
- `--simulate` sinh Evidence (SIMULATED) + Run nhưng 0 OS exec.
- Mọi execution sinh đủ `Run + Artifact + Evidence` (provenance complete).
- `RetryGuard` kích hoạt auto-stop khi lỗi lặp ≥ threshold.
- Architecture gate 0 violations; full suite không regress.

**Dependency / Gate**
- TASK-227 (Unified ExecutionPlan Contract), TASK-222, TASK-226 (RetryGuard), TASK-001.
- Milestone M29.

---

# M30 — Unified Coding Agent (Real Coding Plane)

**Mục tiêu:** biến Coding Plane từ "loaded/smoke-test" (Flow H) thành coding system thực sự: nối `CoderAgent` ↔ `Capability Registry`, `CodingEdition` ↔ `RealToolHandler`, tự động chạy test/static-analysis, artifact code có provenance, mọi mutation qua Policy.

## TASK-229 — Coder Agent ↔ Capability Registry

> **Trạng thái thực tế (2026-08-25):** PLANNED — thuộc phase AIOS 2.x (M30). Chưa implement.

**Mục tiêu**  
Nối `CoderAgent` (M19–M26 Coding Plane) với `Capability Registry` (`aios/capability/`) qua interface injected thay vì gọi trực tiếp. Đảm bảo Coder chỉ nhận capability qua contract, tuân ARCH-001..004 (không import provider/filesystem/tool internals).

**Phạm vi**
- `aios/coder/` nhận `CapabilityRegistry` (injected), resolve tool/capability theo tên.
- `CoderAgent` pure / I/O-free, capability-injected (pattern của `SelfImproverAgent` T225).
- Test: resolve capability, fail-closed khi capability không tồn tại.

**Deliverables**
- `aios/coder/` (wiring) + test + task artifacts + evidence.

**Acceptance Criteria**
- Coder resolve capability qua registry (không direct import).
- Thiếu capability → fail-closed (không guess).
- 0 vi phạm ARCH-001..004; full suite không regress.

**Dependency / Gate**
- TASK-218 (Unified Coding Plane M26), TASK-009 (Capability Foundation), TASK-001.
- Milestone M30.

---

## TASK-230 — CodingEdition ↔ RealToolHandler

> **Trạng thái thực tế (2026-08-25):** PLANNED — thuộc phase AIOS 2.x (M30). Chưa implement.

**Mục tiêu**  
Nối `CodingEdition.run(authorization=..., generated_code=..., verification_report=...)` (M26) với `RealToolHandler` (T222) để AIOS **thực sự viết + thực thi code** dưới Policy/Permission. Định nghĩa execution contract cho code generation (mutation phải qua Policy).

**Phạm vi**
- `CodingEdition` gọi `RealToolHandler` (shell/file/git) được Policy pre-check.
- Contract: generated_code → write → (optional) run tests → collect output → verification_report.
- Mọi file mutation qua `PermissionBroker` + `PolicyEngine` (fail-closed).
- `real_execution.enabled` vẫn opt-in (safe default).

**Deliverables**
- `aios/coding_edition/` (RealToolHandler wiring) + test + task artifacts + evidence.

**Acceptance Criteria**
- `CodingEdition.run(...)` thực thi code thật qua `RealToolHandler` khi `real_execution.enabled=true`.
- Mutation thiếu permission → DENY (không ghi file).
- Contract sinh `verification_report` hợp lệ.
- Architecture gate 0 violations; full suite không regress.

**Dependency / Gate**
- TASK-229 (Coder ↔ Capability), TASK-222 (RealToolHandler), TASK-218, TASK-001.
- Milestone M30.

---

## TASK-231 — Automated Test / Static Analysis + Code Provenance

> **Trạng thái thực tế (2026-08-25):** PLANNED — thuộc phase AIOS 2.x (M30). Chưa implement.

**Mục tiêu**  
Sau khi sinh code, AIOS tự động chạy test + static analysis; artifact code mang provenance đầy đủ (`Evidence→Run→Artifact→Task→Requirement`); mọi mutation qua Policy. Đóng vòng "viết code có chứng cứ".

**Phạm vi**
- Hook post-generation: chạy test/static-analysis qua `RealToolHandler` (policy-checked).
- Mỗi artifact code sinh `Evidence` (content_hash, producer, source, parent_artifact).
- Báo cáo tổng hợp (pass/fail/coverage) đẩy vào `Evaluation`.

**Deliverables**
- `aios/coding_edition/` (post-gen hook) + test + task artifacts + evidence.

**Acceptance Criteria**
- Sinh code → auto chạy test/static-analysis → kết quả vào Evidence.
- Code artifact có provenance chain complete.
- Thiếu permission → không chạy (fail-closed).
- Architecture gate 0 violations; full suite không regress.

**Dependency / Gate**
- TASK-230 (CodingEdition ↔ RealToolHandler), TASK-005 (Evidence), TASK-001.
- Milestone M30.

---

# M31 — Autonomous Coding Loop

**Mục tiêu:** hợp nhất `autonomous_loop`, `autonomous_recovery`, `evaluation`, `autonomous_experimentation`, `stuck_detection`, `autonomy_governor`, `coding_loop` thành MỘT lifecycle duy nhất. **Không tạo subsystem mới.**

## TASK-232 — Unified Autonomous Lifecycle

> **Trạng thái thực tế (2026-08-25):** PLANNED — thuộc phase AIOS 2.x (M31). Chưa implement.

**Mục tiêu**  
Định nghĩa một state machine / orchestration loop duy nhất:

```
Goal → Plan → Execute → Observe → Evaluate
  → Success? ── yes → DONE
       no → Diagnose → Generate Repair Candidate
            → Simulation → Policy → Apply → Verify → loop
```

Map các module đã có vào các node trên; không thêm package.

**Phạm vi**
- `aios/autonomous_loop/` + `aios/coding_loop/` + `aios/autonomous_recovery/` + `aios/stuck_detection/` + `aios/autonomy_governor/` + `aios/evaluation/` + `aios/autonomous_experimentation/` được điều phối bởi một `AutonomousLifecycle` (trong `orchestrator` hoặc `autonomous_loop`).
- Node `Diagnose` dùng `stuck_detection` + `autonomous_recovery`; `Repair Candidate` dùng `autonomous_experimentation`; `Simulation` dùng `harness`; `Policy` dùng `autonomy_governor` + `PolicyEngine`; `Verify` dùng `verification` + `evaluation`.
- `RetryGuard` (T226) + `KillSwitch` (M10) là guard của loop.

**Deliverables**
- `aios/autonomous_loop/lifecycle.py` (Unified Autonomous Lifecycle) + test + task artifacts + evidence.

**Acceptance Criteria**
- Loop chạy end-to-end trên scenario giả lập: Plan→Execute→Observe→Evaluate→(fail)→Diagnose→Repair→Simulate→Apply→Verify→loop→DONE.
- Mọi transition qua Policy/Permission (fail-closed).
- KillSwitch / RetryGuard kích hoạt đúng điều kiện.
- 0 vi phạm ARCH-001..004; full suite không regress.

**Dependency / Gate**
- TASK-228 (Unified Execution), TASK-231 (Coding provenance), TASK-226 (RetryGuard), TASK-041 (HA/Audit/Recovery), TASK-001.
- Milestone M31.

---

# M32 — Evidence-Native AIOS

**Mục tiêu:** "Không có evidence → không có success." Nâng cấp từ chain có sẵn (`Requirement→Task→Artifact→Run→Evidence`, `UNKNOWN ≠ PASS`) thành evidence-native toàn diện.

## TASK-233 — Automatic Evidence Generation

> **Trạng thái thực tế (2026-08-25):** PLANNED — thuộc phase AIOS 2.x (M32). Chưa implement.

**Mục tiêu**  
Mọi execution tự động sinh Evidence với provenance; tracking coverage theo requirement và freshness.

**Phạm vi**
- Hook trong `RuntimeKernel.execute_plan` (T228) tự emit Evidence mỗi Run.
- `EvidenceStore` thêm `requirement_id`, `freshness` (timestamp TTL), `coverage` map.
- Test: coverage theo requirement, freshness expiry.

**Deliverables**
- `aios/runtime/` (evidence hook) + `aios/governance/evidence/` (coverage/freshness) + test + artifacts.

**Acceptance Criteria**
- Mọi execution sinh Evidence tự động (không cần gọi tay).
- Evidence có `requirement_id` + `freshness`; expired → status STALE.
- Coverage map requirement→evidence đầy đủ.
- Architecture gate 0 violations; full suite không regress.

**Dependency / Gate**
- TASK-228 (Unified Execution + evidence emission), TASK-005 (Evidence Store), TASK-001.
- Milestone M32.

---

## TASK-234 — Evidence Quality & Integrity

> **Trạng thái thực tế (2026-08-25):** PLANNED — thuộc phase AIOS 2.x (M32). Chưa implement.

**Mục tiêu**  
Conflict detection, replay, quality score; evaluation CHỈ được dựa trên evidence hợp lệ (non-UNKNOWN, non-STALE).

**Phạm vi**
- `EvidenceStore`: detect conflict (2 evidence cùng requirement, kết quả mâu thuẫn), replay (tái tạo từ Run), quality score (producer trust × freshness × verification).
- `Evaluation` từ chối evidence `UNKNOWN`/`STALE`/conflict → không tính PASS.

**Deliverables**
- `aios/governance/evidence/` (conflict/replay/quality) + `aios/evaluation/` (valid-evidence gate) + test + artifacts.

**Acceptance Criteria**
- Conflict detection báo cáo đúng cặp mâu thuẫn.
- Replay tái tạo Evidence từ Run gốc.
- Quality score tính đúng; evaluation bỏ qua UNKNOWN/STALE/conflict.
- Architecture gate 0 violations; full suite không regress.

**Dependency / Gate**
- TASK-233 (Auto Evidence), TASK-030 (Execution Verification), TASK-032 (Evaluation Harness), TASK-001.
- Milestone M32.

---

# M33 — Autonomous Recovery & Self-Healing

**Mục tiêu:** tận dụng `remediation_detect/candidate/simulation/apply/integrity` + `autonomous_recovery` + `kill_switch` thành flow tự hồi phục. Chuyển từ autonomous execution → autonomous recovery.

## TASK-235 — Unified Remediation Lifecycle

> **Trạng thái thực tế (2026-08-25):** PLANNED — thuộc phase AIOS 2.x (M33). Chưa implement.

**Mục tiêu**  
Flow hợp nhất:

```
Failure → Detect → Diagnose → Candidate → Risk Score
  → Simulation → Independent Verification → Approval / Auto-Apply
  → Rollback nếu FAIL
```

**Phạm vi**
- `remediation_detect` (phát hiện) → `autonomous_recovery`/`stuck_detection` (diagnose) → `remediation_candidate` (candidate) → risk score → `remediation_simulation` (sim) → `verification`/`oracle` (independent verify) → `remediation_apply` (apply, policy-gated) → `remediation_integrity` (integrity) → rollback nếu FAIL.
- `kill_switch` là guard cứng.
- Không tạo package mới — chỉ orchestration layer trong `autonomous_recovery/`.

**Deliverables**
- `aios/autonomous_recovery/lifecycle.py` (Unified Remediation Lifecycle) + test + artifacts + evidence.

**Acceptance Criteria**
- Flow chạy end-to-end trên scenario failure giả lập: detect→diagnose→candidate→risk→sim→verify→apply→(ok|rollback).
- Auto-Apply chỉ khi risk < threshold + independent verify PASS.
- Rollback kích hoạt khi apply FAIL (integrity check).
- KillSwitch override mọi bước.
- Architecture gate 0 violations; full suite không regress.

**Dependency / Gate**
- TASK-232 (Autonomous Lifecycle), TASK-011 (M1 Remediation), TASK-041 (Recovery), TASK-001.
- Milestone M33.

---

# M34 — AIOS Control Center

**Mục tiêu:** sau khi execution/coding/autonomy đã hợp nhất, nâng UI thành Control Center phản ánh state thật. **Không thêm business logic vào Dashboard** — UI chỉ mirror state qua API.

## TASK-236 — Unified Control Center Dashboard

> **Trạng thái thực tế (2026-08-25):** PLANNED — thuộc phase AIOS 2.x (M34). Chưa implement.

**Mục tiêu**  
Dashboard trở thành Control Center với views: Goals, Executions, Agents, Plans, Coding, Evidence, Verification, Autonomy, Resources, Policies, Artifacts, Failures, Recovery, System Health. Mọi data qua API (T017), không logic riêng ở frontend.

**Phạm vi**
- Mở rộng `aios/dashboard/` + `aios/api/` routers để expose state thật (ExecutionPlan, Evidence, Verification, Autonomy, Recovery).
- Frontend chỉ render; mọi compute nằm backend (giữ nguyên tách layer).
- Tận dụng `observability` (T021) + `operations` (T042) đã có.

**Deliverables**
- `aios/dashboard/` (Control Center views) + `aios/api/` (state routers) + test + artifacts.

**Acceptance Criteria**
- Dashboard hiển thị đủ 14 views từ API state thật.
- 0 business logic ở frontend (chỉ render).
- Architecture gate 0 violations (dashboard/api không import runtime internals sai layer); full suite không regress.

**Dependency / Gate**
- TASK-228 (Unified Execution state), TASK-233 (Evidence state), TASK-235 (Recovery state), TASK-017 (API), TASK-018 (Dashboard), TASK-001.
- Milestone M34.

---

# M35 — Self-Evolving AIOS

**Mục tiêu:** đích dài hạn — AIOS tự đề xuất và thúc đẩy nâng cấp bản thân qua Experiment → Harness → Evidence → Verification → Policy → Promotion. **AIOS KHÔNG được tự sửa chính nó trực tiếp.**

## TASK-237 — Self-Evolution Lifecycle

> **Trạng thái thực tế (2026-08-25):** PLANNED — thuộc phase AIOS 2.x (M35). Chưa implement.

**Mục tiêu**  
Flow:

```
Observe → Evaluate → Find weakness → Propose improvement
  → Experiment → Harness verification → Independent verification
  → Risk evaluation → Human / Policy approval → Apply
  → Regression → Promote
```

Tận dụng `SelfImproverAgent` (T225) làm nguồn đề xuất; mọi change phải qua Harness + Independent Oracle + Policy + Regression trước khi Promote. Phù hợp nguyên tắc Evidence-First / Harness-Verified / fail-closed.

**Phạm vi**
- `SelfImproverAgent` (T225) sinh `ImprovementProposal` → đẩy vào pipeline thử nghiệm (không apply trực tiếp).
- Experiment chạy trong sandbox/harness; Evidence thu được qua `EvidenceStore`.
- Promotion chỉ khi Harness PASS + Independent Oracle PASS + Policy approve + Regression green.
- `KillSwitch` + `RetryGuard` guard toàn bộ.

**Deliverables**
- `aios/agents/self_improver.py` (promotion pipeline hook) + `aios/autonomous_experimentation/` (experiment) + test + artifacts + evidence.

**Acceptance Criteria**
- Proposal → Experiment → Harness → Independent → Policy → Regression → Promote chạy end-to-end trên scenario giả lập.
- AIOS KHÔNG sửa `aios/` trực tiếp không qua pipeline (fail-closed).
- Promotion bị chặn nếu bất kỳ gate FAIL.
- Architecture gate 0 violations; full suite không regress.

**Dependency / Gate**
- TASK-225 (Self-Improver), TASK-232 (Autonomous Lifecycle), TASK-234 (Evidence Quality), TASK-029 (Harness Kernel), TASK-001.
- Milestone M35.

---

# 3. Dependency Graph tóm tắt (M29–M35)

```
T227 ─┬─> T228 ─┬─> T232 ─┬─> T235 ─┬─> T236
T222 ─┘         │          │         │
T218 ─> T229 ─> T230 ─> T231 ─┘      │
T008/T010 ──────┘                    │
T005 ─> T233 ─> T234 ────────────────┤
T225 ───────────────────────────────> T237
T226 (RetryGuard) guard T228/T232/T235/T237
```

> Mọi task tuân thủ Definition of Done (PLAN → SPEC → CRITIQUE×2 → BREAKDOWN → REVIEW → IMPLEMENT → TEST → EVALUATE → REGRESSION → PROGRESS/LOG → COMMIT) và 7 governance gates. Khi thực thi từng TASK-xxx, tạo đủ artifacts trong `aios/progress/tasks/TASK-xxx/` và chạy `aiagent task TASK-xxx` để qua unified gate trước khi DONE + Auto-COMMIT (Quy tắc 8).
