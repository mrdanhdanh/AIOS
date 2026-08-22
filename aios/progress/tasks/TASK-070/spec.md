# TASK-070 — AIOS Security Baseline (Security Foundation 1.0)

## Objective
Thiết lập **security baseline 1.0** cho AIOS: authentication (external entry),
authorization (Runtime PermissionBroker + PolicyEngine), secret handling (scoped
refs, no plaintext), least-privilege scoping và audit trail cho mọi privileged
action. Đây là **security foundation**, không redesign — tái sử dụng Runtime
Permission/Policy (T054/Policy) và Autonomy Governor (T054).

## Scope
**In scope**
- `SecurityContext` dataclass (principal, scopes, permissions, secret_refs, evidence_ref).
- Auth validator cho external entry (API/SDK) — reject không auth (fail-closed).
- Permission broker integration (mọi capability/tool action qua permission check).
- Secret handling: scoped refs, redaction helper.
- Least-privilege: vượt scope → BLOCK.
- Audit trail: mọi privileged action ghi audit evidence (provenance).
- Integration với `aios.runtime`, `aios.autonomy_governor`, `aios.api`.

**Out of scope**
- Hệ thống security song song (bắt buộc dùng Runtime Permission/Policy).
- Key rotation service thực tế (chỉ định nghĩa ref + store cục bộ).
- Import `aios.agents.*` (vi phạm architecture guard).

## Deliverables
- `aios/security/context.py` — `SecurityContext`.
- `aios/security/auth.py` — `AuthValidator`, `TokenRecord`, `AuthError`.
- `aios/security/secrets.py` — `SecretStore`, `SecretRef`, `redact_message`.
- `aios/security/audit.py` — `SecurityAudit`, `AuditRecord`.
- `aios/security/broker.py` — `SecurityPermissionBroker` (wrap Runtime Permission+Policy).
- `aios/security/engine.py` — `SecurityBaseline`, `SecurityDecision`.
- `aios/security/api_bridge.py` — `from_api_context` (lazy import `aios.api.auth`).
- `aios/security/tests/test_security_baseline.py` — phủ mọi AC + Test Matrix.
- 9 lifecycle artifacts dưới `aios/progress/tasks/TASK-070/`.

## Acceptance Criteria
- AC1: Mọi external entry yêu cầu auth hợp lệ.
- AC2: Action không permission → BLOCK (fail-closed).
- AC3: Secret không log plaintext / không leak.
- AC4: Least-privilege enforced (vượt scope → BLOCK).
- AC5: Mọi privileged action ghi audit evidence (provenance).
- AC6: Cùng security context + action → cùng quyết định (deterministic).
- AC7: Tích hợp được với Runtime (T065) + Governor (T054) + API.

## Dependencies
- TASK-069 (Reliability Engineering) — predecessor.
- TASK-054 (Autonomy Governor / Policy) — runtime permission + policy.
- TASK-017 (API auth boundary) — external entry.

## Governance references
- Rule 3 (Architecture): `security` classified `unknown`; chỉ import downward/peer
  (`runtime`, `autonomy_governor`, `governance.evidence`, `api` lazy). Không import `agents`.
- Rule 4 (Deterministic): engine `check` thuần túy, không LLM.
- Rule 5 (Evidence): audit dùng `aios.governance.evidence.store.EvidenceStore`.
