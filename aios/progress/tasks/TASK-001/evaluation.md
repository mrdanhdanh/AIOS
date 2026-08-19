# Evaluation — TASK-001

## AC verification
| AC | result | evidence ref |
|----|--------|--------------|
| Registry duplicate → REJECT | PASS | EVD-001 (test_registry, sha256:a1b2c3d4e5f67890) |
| Dependency missing/cyclic/milestone → BLOCK (fail-closed) | PASS | EVD-001 (test_graph) + DependencyGraph milestone check |
| Architecture violation → FAIL (incl. `import os`, dynamic import, workflow↔engine) | PASS | EVD-001 (test_rules, ARCH-001..004) |
| Deterministic: LLM call 0 / fallback validated (validator REQUIRED) | PASS | EVD-001 (test_path) + ControlPathError on missing validator |
| Evidence provenance chain (sha256, task-scoped, UNKNOWN≠PASS) | PASS | EVD-001 (test_store) + TaskGate task-scoped verify |
| State Machine missing artifact → REJECT | PASS | EVD-001 (test_statemachine) + gate reads STATUS.md |
| Regression closure failure/exception → BLOCK | PASS | EVD-001 (test_runner) + RegressionRunner fail-closed |

## Self-critique (điều chỉnh bổ sung)
- Vá fail-open: DependencyGraph, EvidenceStore, DeterministicPath, RegressionRunner, Architecture, TaskGate, gate_check.py đều chuyển sang fail-closed.
- `docs/PLAN.md` §6 bổ sung cột Fail-closed và mô tả chi tiết mechanism.
- EVIDENCE.md chuyển sang `sha256:` hash thực thụ; gate kiểm tra task-scoped.

## Verdict
- [x] PASS (with provenance — see EVIDENCE.md, sha256 validated, gate reads STATUS.md)
