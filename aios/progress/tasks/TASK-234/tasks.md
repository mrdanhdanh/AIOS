# TASK-234 — Breakdown

## Sub-tasks
1. **T234.1** — `Evidence` thêm `requirement_id`/`freshness`/`coverage`; `is_stale()`.
2. **T234.2** — `EvidenceStore` thêm `_coverage` + `coverage_map`/`is_requirement_covered`.
3. **T234.3** — `record_execution_evidence` truyền `requirement_id` + `freshness` (1h TTL).
4. **T234.4** — Test + architecture gate.

## Verification
`pytest aios/governance/evidence/tests/test_evidence.py -k "freshness or coverage"` + `pytest aios/governance/architecture`.
