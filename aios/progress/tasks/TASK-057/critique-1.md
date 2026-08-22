# TASK-057 — Critique 1

## Missing spec sections
- Entry contracts enumerated in `contracts.py` (no `embedding_key`; `lesson_candidate` + trust/verification).
- Retention priority ordering in `retention.RetentionPolicy.priority`.

## Risks
- Unverified lesson could be consumed. Mitigation: `write_goal` forces UNVERIFIED/UNTRUSTED; only `verify_entry` promotes.
- Cross-scope leak. Mitigation: `read` is scope-keyed; controller never returns another scope.
- Redaction bypass. Mitigation: observation passed through injected `redact` before persist.

## Verdict
Implementable. Proceed.
