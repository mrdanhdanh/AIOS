# TASK-141 — Output + Artifact Collector

## Objective
Triển khai **Output + Artifact Collector** (M20) như một năng lực có contract, evidence và harness riêng — thu thập output (stdout/stderr/log) và artifact từ test/build/lint run (T139/T140) thành artifact có provenance. TASK-141 là **collector, không phải runner mới** (dựa trên Test Runner T139 + Build/Lint T140 + Coding Artifact T130 + Evidence T001).

## Scope
**In scope:** `aios/execution/collector.py` — `OutputArtifactCollector`, `CollectedArtifact`, `OutputCapture`, `redact`.
**Out of scope:** runner mới (T139/T140), verification (T142).

## Deliverables
- `aios/execution/collector.py` implementation + secret isolation.
- Unit + Contract + Integration + Architecture + Regression tests (`test_collector.py`).
- Tích hợp: T139/T140 -> T141 -> T142.

## Acceptance Criteria
- Collector thu output (stdout/stderr/log) từ run.
- Collector thu artifact từ test/build/lint (T139/T140).
- Mọi output/artifact có `content_hash` (T078) + provenance (T001 Rule 5).
- Collector không lộ secret (T040/T113).
- Output/artifact không hash được -> reject (fail-closed, T078).
- Cùng run -> cùng collected set (deterministic).
- Tích hợp được với Test Runner + Build/Lint + Coding Artifact + Evidence + Integrity.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T139 (Test Runner) + T140 (Build/Lint) -> T141 -> T142.
- T001 (Rule 5), T078 (Integrity), T130 (Artifact), T040/T113 (Secret).

## Governance references
- Rule 1..7 via `aios/governance/*`. `execution` là `unknown` (infra) layer.
