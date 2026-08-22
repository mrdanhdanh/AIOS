# TASK-052 — Critique 1

## Missing spec sections
- Entity/relation lifecycle and example graph clarified in `contracts.py` + `engine.add_relation`.
- Provenance requirement on observations and relations enforced (AC-052-02/05).

## Risks
- Snapshot holding live references would mutate history. Mitigation: `snapshot()` deep-copies entities/relations.
- World Model could drift into a memory store. Mitigation: engine stores only current state, no recall/historical query API.

## Verdict
Implementable. Proceed.
