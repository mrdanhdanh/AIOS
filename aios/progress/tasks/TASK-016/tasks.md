# TASK-016 — Breakdown

- [x] **16.1** Implement `aios/governance/architecture/violations.py` — ArchitectureViolation model (violation_id, rule_id, invariant_id, file, line, source/target, type, severity, message, evidence, detected_at, status, fail-closed).
- [x] **16.2** Implement `aios/governance/architecture/scanner.py` — AST scanner (enumerate files, parse AST, extract imports/calls/inheritance/decorators/ownership, layer detection, violation generation, machine-readable report).
- [x] **16.3** Implement `aios/governance/architecture/graph.py` — DependencyGraph (add_node/edge, traversal, reverse, cycle detection DFS, topological sort, forbidden edge, layer violation).
- [x] **16.4** Implement `aios/governance/architecture/rules.py` — Rule engine (ARCH-A..H categories, INV-001..010 mapping, allowed/forbidden matrix, severity, evidence, rule evaluation).
- [x] **16.5** Implement `aios/governance/architecture/gate.py` — ArchitectureGate (Scan→Rule→Violation→Invariant→PASS/FAIL/UNKNOWN, fail-closed, aggregation, invariant evaluation).
- [x] **16.6** Implement `aios/governance/architecture/report.py` — Report generator (machine-readable JSON, summary, gate result, provenance, violations).
- [x] **16.7** Update `aios/governance/architecture/guard.py` + `__init__.py` — harden guard (delegate to scanner/rules, backward compat), update exports.
- [x] **16.8** Create `aios/governance/architecture/tests/test_import_boundaries.py` — ARCH-A import boundary tests (positive/negative, relative/dynamic imports).
- [x] **16.9** Create `aios/governance/architecture/tests/test_layer_rules.py` — layer dependency validation tests (allowed/denied matrix, reverse dependency).
- [x] **16.10** Create `aios/governance/architecture/tests/test_invariants.py` — INV-001..010 invariant enforcement tests.
- [x] **16.11** Create `aios/governance/architecture/tests/test_cycles.py` — circular dependency detection tests (A→B→C→A, package-level).
- [x] **16.12** Create `aios/governance/architecture/tests/test_policy_bypass.py` — policy bypass detection tests (Agent→Tool without Policy).
- [x] **16.13** Create `aios/governance/architecture/tests/test_capability_boundary.py` — capability boundary tests (Agent hard-code Tool vs CapabilityContract).
- [x] **16.14** Create `aios/governance/architecture/tests/test_workflow_engine_independence.py` — workflow engine coupling tests (Workflow→LangGraph).
- [x] **16.15** Create `aios/governance/architecture/tests/test_plugin_isolation.py` — plugin isolation tests (Skill→Core bypass, deterministic-first, orchestrator God Object, fail-closed, CI).
- [x] **16.16** Run `python -m pytest aios -q` — verify 1100+ tests PASS, no architecture violations, fail-closed.
- [x] **16.17** Write `test.md` + `evaluation.md` + `REGRESSION.md` with evidence.
- [x] **16.18** Update `aios/progress/PLAN.md`, `LOG.md`, `STATS.md` — mark TASK-016 DONE.
