# TASK-058 — Critique 1

## Missing spec sections
- Experiment contract + MetricSpec enumerated in `contracts.py`.
- Promotion gate logic in `controller.evaluate` (3-way AND).

## Risks
- LLM could define vague success criteria. Mitigation: `propose` rejects empty/zero-threshold metric_spec.
- Mutable baseline version breaks A/B. Mitigation: `propose` rejects latest/current/empty versions.
- Self-promotion. Mitigation: controller only returns `PromotionDecision`; no deploy path.

## Verdict
Implementable. Proceed.
