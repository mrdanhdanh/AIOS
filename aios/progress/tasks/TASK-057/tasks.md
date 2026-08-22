# TASK-057 — Breakdown

## Steps
1. `aios/autonomous_memory/contracts.py` — FailureMemoryEntry, GoalMemoryEntry, MemoryScope, TrustStatus, VerificationStatus.
2. `aios/autonomous_memory/retention.py` — RetentionPolicy (TTL + deterministic eviction).
3. `aios/autonomous_memory/controller.py` — MemoryController (provenance/redaction/trust/retention/dedupe/autonomy-gated write).
4. `aios/autonomous_memory/tests/test_autonomous_memory.py` — 8 tests.
5. Run architecture guard — no subprocess/provider/filesystem import.
6. Run full suite — no regressions.

## Exit Criteria
- All AC-057-01..11 PASS, gate PASS, no regressions.
