# TASK-057 — Autonomous Memory

## Objective
Build **controlled Autonomous Memory** — a capability on the existing Memory (T007) that stores failure memory (classified by T055 + recovery outcome) and goal memory (history/plan/outcome/observation) with trust/verification guard, controlled retention, and scoped access. It is NOT a second memory system (no AutonomousMemoryStore/VectorDB/KnowledgeDB/Retriever). Enforces INV-034 (no unverified promote) and INV-024 (credential isolation).

## Scope
### In scope
- `FailureMemoryEntry` (goal_id/execution_id/failure_class/classification/recovery_strategy/outcome/evidence_ref/retrieval_metadata) — no `embedding_key`.
- `GoalMemoryEntry` (goal_id/execution_id/plan_ref/outcome/observation/lesson_candidate/evidence_ref/verification_status/trust_status) — `lesson_candidate` NOT trusted on write.
- Provenance Validator: `evidence_ref` must be *valid* (full chain Evidence→Run→Artifact→Task→Requirement), not just a string.
- Safety/Redaction: consume T040 contract; redaction failure → no raw persist.
- Trust/Verification Guard (INV-034): only VERIFIED+TRUSTED entries are consumed by Planner/Loop.
- Retention Policy: TTL + deterministic eviction by RetentionPriority (TRUSTED>VERIFIED>UNVERIFIED, newer>older). No semantic/LLM ranking.
- Scope isolation: execution/goal/session/tenant; cross-scope read → DENY.
- Deduplicate: same (goal_id+signature) → update, not duplicate.
- Autonomy-gated write: consume T054 decision; governor deny → no persist.

### Out of scope
- Embedding/retrieval architecture (T007 knowledge pipeline), security subsystem, second control plane.

## Deliverables
- `aios/autonomous_memory/contracts.py` — FailureMemoryEntry, GoalMemoryEntry, MemoryScope, TrustStatus, VerificationStatus.
- `aios/autonomous_memory/retention.py` — RetentionPolicy (TTL + deterministic eviction).
- `aios/autonomous_memory/controller.py` — MemoryController (provenance/redaction/trust/retention/dedupe/autonomy-gated write).
- `aios/autonomous_memory/tests/` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-057-01: Failure memory persists with valid evidence_ref (complete provenance).
- AC-057-02: Goal memory persists observation + lesson_candidate (not trusted directly).
- AC-057-03: lesson_candidate unverified → UNTRUSTED, Planner does not use.
- AC-057-04: Retention (TTL/size/scope) enforced; eviction deterministic.
- AC-057-05: Sensitive data redacted via T040; redaction fail → no raw persist.
- AC-057-06: Cross-scope read → DENY.
- AC-057-07: Unverified/poisoned entry not trusted/promoted (INV-034).
- AC-057-08: Governor deny → no persist.
- AC-057-09: Missing/invalid evidence → REJECT.
- AC-057-10: No AutonomousMemoryStore/VectorDB/KnowledgeDB/Retriever created.
- AC-057-11: Regression M0–M8 PASS.

## Dependencies
- TASK-007 Memory + Knowledge
- TASK-055 Autonomous Recovery
- TASK-040 Security/Redaction
- TASK-054 Autonomy Governor

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
