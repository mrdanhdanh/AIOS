# TASK-016 — Architecture Hardening

## Objective
Xây dựng Architecture Hardening Gate để biến các architecture invariant của AIOS từ quy ước thiết kế thành các quy tắc có thể kiểm tra tự động. TASK-016 bảo đảm khi codebase phát triển, các vi phạm như Agent truy cập Tool trực tiếp, bypass Capability/Policy, Workflow phụ thuộc Engine, Orchestrator God Object, import ngược/cycle, Plugin xâm nhập Core, LLM bypass deterministic path đều bị phát hiện và làm gate FAIL. Architecture violation = gate FAIL = task/release không được PASS. TASK-016 tạo enforcement mechanism để architecture được bảo vệ liên tục trong CI và regression.

## Scope
- **Architecture Rule Engine** (`aios/governance/architecture/rules.py`): tập rule kiểm tra architecture bằng AST/import analysis, mỗi rule có rule_id, description, severity, source_layer, target_layer, allowed/denied, invariant_id, category, evidence. Map INV-001..010 vào ARCH-A..H.
- **Layer Dependency Validation** (`aios/governance/architecture/rules.py` + `graph.py`): xác định layers UI→API→Orchestrator→Runtime→Skill→Capability→Tool (canonical: Agent→Orchestrator→Worker→Runtime→Skill→Capability→Tool), dependency hợp lệ phải đi theo boundary contract, cấm Tool→Orchestrator, Tool→Agent, Capability→Agent, Agent→Tool implementation, import xuyên tầng không contract.
- **Agent Boundary** (`scanner.py` + `rules.py`): Worker/Agent chỉ được Agent→Capability→Runtime/Tool boundary, cấm import subprocess/requests/docker/filesystem_adapter, cấm truy cập Runtime Service impl, Tool Registry impl, Provider impl, Filesystem adapter, Docker client, Shell executor trực tiếp.
- **Capability Boundary** (`rules.py`): Agent chỉ yêu cầu execute_code/run_tests/filesystem.read/git.diff thay vì PythonTool/ShellTool/GitTool hard-code, phát hiện hard-code Tool implementation.
- **Workflow/Engine Independence** (`rules.py`): Workflow Definition độc lập engine, cấm Workflow Definition→LangGraph implementation hard dependency, phải qua Compiler Interface (LangGraph/Mock), phát hiện import trực tiếp engine impl từ domain contract.
- **Policy/Permission Boundary** (`rules.py` + `gate.py`): Execution không bypass Policy→Permission→Execution, mọi execution path phải qua policy boundary trước side effect, kiểm tra import dependency, service wiring, execution call path, adapter bypass.
- **Orchestrator Boundary** (`rules.py`): Orchestrator là Control Plane nhưng không God Object, responsibility nằm ở Decision Pipeline/Task Planner/Agent Selector/Capability Router/Permission Broker/Failure Recovery/Goal Manager/Task Queue/System Knowledge, cảnh báo/FAIL khi Orchestrator sở hữu trực tiếp Tool execution/Memory storage/Model provider/Sandbox/Scheduler internals/Persistence internals, chỉ điều phối qua contract/service interface.
- **AST Scanner** (`aios/governance/architecture/scanner.py`): enumerate source files, parse AST, extract imports/from-import/function calls/class inheritance/decorators/package ownership, xác định layer, áp dụng rules, sinh violations, sinh machine-readable report.
- **Architecture Graph** (`aios/governance/architecture/graph.py`): dependency graph Module A→B→C, hỗ trợ traversal/reverse/cycle detection/forbidden edge/layer violation, dùng graph nội bộ đơn giản, không kéo dependency nặng.
- **Violation Model** (`aios/governance/architecture/violations.py`): ArchitectureViolation với violation_id, rule_id, invariant_id, file, line, source_component, target_component, violation_type, severity, message, evidence, detected_at, status (ERROR/WARNING/INFO, FAIL/UNKNOWN/PASS, fail-closed UNKNOWN≠PASS).
- **Architecture Gate** (`aios/governance/architecture/gate.py`): Scan→Rule Evaluation→Violation Collection→Invariant Evaluation→PASS/FAIL/UNKNOWN, fail-closed, UNKNOWN không promote thành PASS.
- **Report** (`aios/governance/architecture/report.py`): machine-readable JSON report với violations, summary, gate result, provenance.
- **CI Integration**: architecture test chạy trong CI, pytest→Architecture Tests→Contract Tests→Integration Tests→Architecture Gate, violation làm CI FAIL, TASK BLOCKED, không cho merge/release khi architecture FAIL dù functional PASS.
- **Out of scope**: UI/API implementation (M3), multi-tenant (M7), full container isolation (M6 harness), LLM-dependent architecture decisions.

## Deliverables
- `aios/governance/architecture/scanner.py` — AST scanner (imports, calls, inheritance, decorators, ownership, layer detection, violation generation).
- `aios/governance/architecture/graph.py` — DependencyGraph (traversal, reverse, cycle detection DFS, topological sort, forbidden edge, layer violation).
- `aios/governance/architecture/violations.py` — ArchitectureViolation model (violation_id, rule_id, invariant_id, file, line, source/target, type, severity, message, evidence, detected_at, status).
- `aios/governance/architecture/rules.py` — Rule engine (ARCH-A..H, INV-001..010 mapping, allowed/forbidden matrix, severity, evidence).
- `aios/governance/architecture/gate.py` — ArchitectureGate (PASS/FAIL/UNKNOWN, fail-closed, invariant evaluation, aggregation).
- `aios/governance/architecture/report.py` — Report generator (machine-readable JSON, summary, provenance).
- `aios/governance/architecture/__init__.py` — updated re-exports.
- `aios/governance/architecture/guard.py` — hardened (backward compat, delegates to new scanner/rules).
- Tests: `aios/governance/architecture/tests/test_import_boundaries.py`, `test_layer_rules.py`, `test_invariants.py`, `test_cycles.py`, `test_policy_bypass.py`, `test_capability_boundary.py`, `test_workflow_engine_independence.py`, `test_plugin_isolation.py` (≥80 tests, cover AC-001..013).
- Governance artifacts: `aios/progress/tasks/TASK-016/{spec,critique-1,critique-2,tasks,review,test,evaluation,REGRESSION}.md`.

## Acceptance Criteria
1. **AC-001 — Layer enforcement**: dependency sai layer phải bị phát hiện (FAIL).
2. **AC-002 — Agent/Tool boundary**: Agent truy cập Tool implementation trực tiếp phải bị block.
3. **AC-003 — Capability boundary**: Agent chỉ được truy cập Tool thông qua Capability contract.
4. **AC-004 — Workflow independence**: Workflow domain không phụ thuộc trực tiếp vào engine implementation.
5. **AC-005 — Policy boundary**: Execution bypass Policy/Permission phải FAIL.
6. **AC-006 — Circular dependency**: Dependency cycle phải FAIL.
7. **AC-007 — Orchestrator boundary**: Orchestrator không được sở hữu trực tiếp Tool/Provider/Storage implementation.
8. **AC-008 — Deterministic-first**: LLM không được trở thành routing path mặc định.
9. **AC-009 — Plugin isolation**: Skill/plugin không được bypass Core boundary.
10. **AC-010 — CI enforcement**: Architecture violation làm CI FAIL.
11. **AC-011 — Fail closed**: UNKNOWN không được tự động chuyển thành PASS.
12. **AC-012 — Regression**: Architecture suite phải chạy cùng regression suite của các dependency trước đó.
13. **AC-013 — Evidence**: Mỗi violation phải có file/line/rule/invariant/evidence đủ để developer truy nguyên.

## Dependencies
- TASK-010 Decision Pipeline (DONE) — Normalizer→Rule→Workflow→Planner, deterministic-first.
- TASK-012 Operational Orchestration (DONE) — Goal Manager, Task Queue, Permission Broker, Failure Recovery.
- TASK-013 Worker Plane (DONE) — General/Coder/Doctor/SystemDoctor, capability-only.
- TASK-014 Tool + Capability Layer (DONE) — ToolRegistry, CapabilityRouter, Policy pre-check.
- TASK-015 Plugin / Skill Execution (DONE) — Skill lifecycle, Sandbox Pool, isolation.
- M0/M1 Governance + Runtime (DONE) — Task Registry, Dependency Graph, Lifecycle, Evidence, Architecture Guard foundation.

## Governance references
- Rule 3 Architecture Guard (Agent→Orchestrator→Worker→Runtime→Skill→Capability→Tool, no bypass, layering enforced).
- Rule 4 Deterministic-first (LLM only when INSUFFICIENT, validator required).
- Rule 5 Evidence (provenance Evidence→Run→Artifact→Task→Requirement, UNKNOWN≠PASS).
- Rule 7 Regression (dependency closure must PASS).
- INV-001..010 mapped to ARCH-A..H, fail-closed, CI gate.
