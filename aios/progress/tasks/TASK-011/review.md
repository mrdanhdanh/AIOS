# TASK-011 — Review

## Pre-implementation checklist
- [x] spec.md present (AC-011-01..10, E2E verification, Definition of Done, out-of-scope M2)
- [x] critique-1.md present (APPROVE with required revisions addressed)
- [x] critique-2.md present (APPROVE with required revisions addressed)
- [x] tasks.md present (8 steps, deterministic, bounded remediation)

## Notes
Both critiques APPROVE. Guard patch is minimal (LAYER_KEYWORDS + ALLOWED_IMPORT_LAYERS only), `unknown` superset preserved for stdlib/third-party, `kernel→runtime` is segment-bound so prose false positives avoided. `agent: ["orchestrator","unknown"]` and `capability: ["unknown"]` are the intended hardening — they make AC-011-04 fail-closed as required by T008-009-011.md §2.5/§5. Kernel health already exhaustive (16 keys); hardening tests assert completeness rather than adding runtime behavior.

## Decision
- APPROVED — proceed to implementation.
