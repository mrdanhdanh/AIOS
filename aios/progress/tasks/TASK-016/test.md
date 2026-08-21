# TASK-016 — Test Report

## Scope
Architecture Hardening Gate (final M2 gate). AST scanner + dependency graph +
rule engine (ARCH-A..H / INV-001..010) + fail-closed gate + report.

## Execution
```
python -m pytest aios/governance/architecture/tests/ -q
```

## Result
```
112 passed in 0.56s
```

## Per-module
| Module | Tests | Notes |
|--------|-------|-------|
| architecture (scanner/graph/rules/gate/report/violations) | 44 | core engine + gate + report |
| test_import_boundaries | 12 | ARCH-A positive/negative, relative/dynamic imports |
| test_layer_rules | 11 | allowed/denied matrix, reverse dependency |
| test_invariants | 13 | INV-001..010 enforcement |
| test_cycles | 8 | A->B->C->A, package-level cycle detection |
| test_policy_bypass | 7 | Agent->Tool without Policy detected |
| test_capability_boundary | 7 | Agent hard-code Tool vs CapabilityContract |
| test_workflow_engine_independence | 5 | Workflow->LangGraph coupling detected |
| test_plugin_isolation | 5 | Skill->Core bypass, God Object, fail-closed, CI |

## Full suite (M2 regression)
```
python -m pytest aios -q
1257 passed in 5.55s
```
