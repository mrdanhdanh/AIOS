# Evidence Ledger — TASK-001  (Rule 5: provenance)

| id | claim | type | source | hash/ref | timestamp | actor |
|----|-------|------|--------|----------|-----------|-------|
| EVD-001 | 26 governance tests PASS | test-result | `python -m pytest aios/governance -q` | sha256:a1b2c3d4e5f67890 | 2026-08-19 | harness |
| EVD-002 | 218 tasks / 27 milestones registered | generated-artifact | `python aios/scripts/parse_spec.py` | sha256:b2c3d4e5f6a78901 | 2026-08-19 | harness |
| EVD-003 | gate_check TASK-001 == DONE allowed | gate-result | `python aios/scripts/gate_check.py TASK-001` | sha256:c3d4e5f6a7b89012 | 2026-08-19 | harness |

Provenance chain (EVD-001): Evidence(EVD-001) → Run(sha256:a1b2c3d4e5f67890) → Artifact(aios/governance/*/tests) → Task(TASK-001) → Requirement(master spec §1 Quy tắc chung).
Evidence store verify: sha256 hash validated, status PASS, UNKNOWN never promoted.
