# Critique 1 — TASK-105

- **Authority boundary phải explicit:** `aios_policy_verdict` là authoritative, `independent_verdict` chỉ là input. → Đã có `PolicyAuthority.reject_override` trong `query`.
- **INCONCLUSIVE/UNKNOWN fail-closed:** dùng `VerdictClass.from_any` + `IntegrityChecker.promotes_to_pass` để không promote. → Đã áp dụng.
- **Provenance bridge:** evidence từ oracle phải qua `EvidenceIngestBoundary` (T104). → Đã gọi `self._ingest.ingest`.
- **Determinism:** cùng invariant + cùng oracle input → cùng `independent_verdict`. → Oracle callable được gọi deterministic; evidence_id ổn định theo invariant+verdict.
