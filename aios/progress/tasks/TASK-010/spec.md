# TASK-010 — Decision Pipeline

## Objective
Xây AIOS Orchestrator v1 Decision Pipeline — lớp quyết định trung tâm biến request chưa cấu trúc thành ExecutionPlan có thể đưa xuống Runtime. Pipeline ưu tiên deterministic path `Request → Normalizer → Rule Engine → Workflow Matcher → Planner LLM → ExecutionPlan`; LLM chỉ fallback khi deterministic `INSUFFICIENT` và output phải qua validator. Đây là control plane cho M2, nối Runtime M1 với Goal/Worker/Tool của các task sau.

## Scope
- **Normalizer** (`aios/orchestrator/normalizer.py`): alias/command/parameter normalization, default values, target resolution, mode/priority/metadata/source_channel, không gọi LLM, deterministic.
- **Rule Engine** (`aios/orchestrator/rule_engine.py`): xử lý `run tests`, `system health`, `list skills`, `review code`, `diagnose runtime`… trả `MATCHED`/`INSUFFICIENT`, không dùng LLM khi đã MATCHED.
- **Workflow Matcher** (`aios/orchestrator/workflow_matcher.py`): tìm workflow/template/macro trong Workflow Library (in-memory registry, deterministic substring/capability match), `MATCHED` → ExecutionPlan không cần Planner.
- **Planner LLM** (`aios/orchestrator/planner.py`): chỉ chạy khi `Rule=INSUFFICIENT AND Workflow=NO_MATCH`, nhận normalized request + capabilities + workflow candidates + metadata + policy/resource constraints → ExecutionPlan, không trực tiếp execute tool, output qua validator.
- **ExecutionPlan** (`aios/orchestrator/execution_plan.py`): artifact trung gian `id/request_id/nodes/edges/permissions/resources/policy`, validate trước khi Execution Service nhận (schema→contract→capability→permission→policy→resource).
- **Decision Pipeline** (`aios/orchestrator/decision_pipeline.py`): orchestrate `Normalizer → RuleEngine → WorkflowMatcher → Planner → Policy → ExecutionPlan`, evidence chain `Request → NormalizedRequest → Decision → Workflow/Planner → ExecutionPlan`, offline-first, fail-closed.
- **Governance compat**: `aios/governance/deterministic/pipeline.py` giữ `DeterministicControlPath` backward compat, delegate hoặc re-export sang orchestrator pipeline.
- **Out of scope**: Goal Manager/Task Queue (TASK-012), Worker Plane (TASK-013), Tool Router (TASK-014), UI/API.

## Deliverables
- `aios/orchestrator/__init__.py` — package doc + re-exports.
- `aios/orchestrator/normalizer.py` — `NormalizedRequest`, `Normalizer`.
- `aios/orchestrator/rule_engine.py` — `RuleDecision`, `RuleEngine`.
- `aios/orchestrator/workflow_matcher.py` — `WorkflowMatch`, `WorkflowMatcher`, `WorkflowLibrary`.
- `aios/orchestrator/planner.py` — `PlannerRequest`, `PlannerResponse`, `Planner`, `PlannerError`.
- `aios/orchestrator/execution_plan.py` — `ExecutionPlan`, `PlanNode`, `PlanEdge`, `ExecutionPlanError`.
- `aios/orchestrator/decision_pipeline.py` — `DecisionPipeline`, `DecisionResult`, `DecisionEvidence`.
- `aios/governance/deterministic/pipeline.py` — enhanced Normalizer/RuleEngine/WorkflowMatcher + backward compat.
- Tests: `aios/orchestrator/tests/test_normalizer.py`, `test_rule_engine.py`, `test_workflow_matcher.py`, `test_planner.py`, `test_execution_plan.py`, `test_decision_pipeline.py`, `test_architecture.py`.

## Acceptance Criteria
1. **AC-010-01 — Normalization**: cùng semantic request → normalized representation ổn định (intent/target/mode/priority).
2. **AC-010-02 — Deterministic routing**: request RuleEngine nhận diện → `llm_call_count==0`.
3. **AC-010-03 — Workflow reuse**: WorkflowMatcher tìm thấy workflow → Planner không gọi.
4. **AC-010-04 — Planner fallback**: Planner chỉ gọi khi `Rule=INSUFFICIENT AND Workflow=NO_MATCH`.
5. **AC-010-05 — Planner validation**: Planner output invalid → REJECT, không đưa vào Runtime.
6. **AC-010-06 — Policy boundary**: ExecutionPlan chịu Policy/Permission validation trước execution.
7. **AC-010-07 — Offline**: deterministic requests chạy không cần model provider.
8. **AC-010-08 — Evidence**: truy nguyên `Request → Decision → Plan` với evidence chain.
9. **AC-010-09 — Architecture**: Planner/Orchestrator không trực tiếp gọi Tool (guard PASS).
10. **AC-010-10 — Regression**: `python -m pytest aios -q` xanh, M1 544 tests vẫn PASS.

## Dependencies
- TASK-003 Kernel Foundations (DONE), TASK-004/005 Runtime Services (DONE), TASK-006 Model Provider (DONE), TASK-007 Memory/Knowledge (DONE), TASK-008 Workflow Definition/Compiler (DONE), TASK-009 Capability Foundation (DONE), TASK-011 M1 Remediation (DONE).

## Governance references
- Rule 4 Deterministic-first via `aios/governance/deterministic/pipeline.py` + `aios/orchestrator/decision_pipeline.py`; Rule 3 Architecture Guard `Agent→Orchestrator→Runtime→Capability→Tool`; Rule 5 Evidence via `DecisionEvidence`; Rule 7 Regression via full suite.
