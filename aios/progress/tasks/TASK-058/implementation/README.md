# TASK-058 Implementation

## Modules
- `contracts.py` — `Experiment`, `ExperimentStatus`, `MetricSpec`, `PromotionDecision`.
- `controller.py` — `ExperimentController`: `propose` (validates metric_spec + immutable versions), `authorize` (governor), `run` (Harness only), `evaluate` (multi-dimensional promotion gate, fail-closed).

## Design notes
- Capability on Runtime; reuses Harness T029–T034. No sandbox/control plane of its own.
- Promotion is multi-dimensional: verified quality improvement AND no prohibited cost/latency/failure regression AND policy PASS.
- INCONCLUSIVE/UNKNOWN never promote; controller only emits a `PromotionDecision` artifact (never deploys).
- Governor denial → BLOCK before any run.
