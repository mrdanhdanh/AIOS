# TASK-047 — Breakdown

## Steps
1. Create `aios/devkit/contracts.py` — ProjectTemplate (name, description, files), ScaffoldConfig (project_name, template, author)
2. Create `aios/devkit/scaffold.py` — DevKitScaffold: register_template, get_template, scaffold (with template lookup), list_templates
3. Implement manifest validation and contract compatibility checking
4. Implement test integration (orchestration via Harness) and simulation
5. Implement packaging with immutable artifact and evidence
6. Create `aios/devkit/tests/` — 5 tests (register_template, get_template, scaffold, list_templates, default template)
7. Run architecture guard — verify no DevKit → Runtime/Tool/Policy DB direct access
8. Run full suite — 1823/1823 PASS (5 new), no regressions

## Dependencies
- TASK-046 Ecosystem Registry

## Exit Criteria
- All AC-047-01..10 PASS, gate PASS, no regressions
