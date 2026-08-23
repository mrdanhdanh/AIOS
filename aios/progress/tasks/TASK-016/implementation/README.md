# TASK-016 Implementation — Architecture Hardening

Implementation lives in `aios/governance/architecture/` (M2 Architecture Hardening Gate).

```
aios/governance/architecture/
  guard.py       # ArchitectureGuard, LAYER_ORDER, LAYER_KEYWORDS, ARCH-001..004
  scanner.py     # AST/import scanner
  graph.py       # Dependency graph, cycle detection
  rules.py       # ARCH-A..H + INV-001..010 rule definitions
  gate.py        # Architecture gate (FAIL → BLOCKED)
  report.py      # Violation report, evidence
  baseline.py    # Baseline snapshot (T063 extension)
  violations.py  # Violation dataclass
  __init__.py    # re-exports
  tests/
    test_architecture_guard.py
    test_layering.py
    test_bypass_detection.py
    test_m1_hardening.py  # 30 tests (TASK-011)
    test_arch_hardening.py # 112 tests (TASK-016)
```

Enforces `Agent → Orchestrator → Runtime → Capability → Tool` (downward only). Violations → `ARCHITECTURE GATE = FAIL → TASK BLOCKED` (fail-closed, also on parse errors).

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2477 PASS current).
