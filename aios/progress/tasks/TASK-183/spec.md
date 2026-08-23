# TASK-183 — Approval Workflow + Rollback Recommendation

## Objective
Triển khai Approval Workflow + Rollback Recommendation như một năng lực có contract, evidence và harness riêng (M24 — Governance & Quality).

## Scope
- Package: `aios/quality_gate/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/quality_gate/approval_workflow.py` — class `ApprovalWorkflow`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- ApprovalRequest/ApprovalReport immutable; submit APPROVED/REJECTED; HIGH/CRITICAL needs >=2 approvers (fail-closed); rollback recommendation; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T182,T097,T055 (all DONE in prior milestones).
