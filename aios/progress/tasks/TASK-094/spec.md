# TASK-094 — Detect + Diagnose

## Objective
Phát hiện (detect) sự cố/hành vi sai và chẩn đoán (diagnose) nguyên nhân gốc
(root cause) có evidence, làm nền tảng cho remediation (T095-T098). TASK-094 là
**detection + diagnosis, không phải remediation** (dựa trên Stuck T061 +
Observability T065/T069 + Evidence T001).

## Scope
**In scope:** `aios/remediation_detect/` — Incident, Symptom, Diagnosis,
DetectDiagnoseEngine. Tích hợp Stuck (T061) + Observability (T065/T069) + Evidence (T001).
**Out of scope:** remediation/apply; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/remediation_detect/detect.py` — detect + diagnose engine.
- `aios/remediation_detect/tests/test_detect.py` — 9 tests (Test Matrix).
- Tích hợp với Stuck (T061) + Observability (T065/T069) + Evidence (T001).

## Acceptance Criteria
- Detect phát hiện anomaly/failure/deviation.
- Symptom được capture có evidence.
- Root cause trace được (causal chain).
- Thiếu evidence → escalate, không kết luận (fail-closed).
- Mọi diagnosis có provenance (T001 Rule 5).
- Cùng incident + evidence → cùng diagnosis (deterministic).
- Tích hợp được với Stuck + Observability + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T093 (Behavioral Spec + ADR-0008) → T094 → T095.
- T061 (Stuck), T065/T069 (Observability), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `remediation_detect` là `unknown`
  layer; chỉ import stdlib + `aios.stuck_detection` + `aios.observability` + `aios.governance.evidence`.
