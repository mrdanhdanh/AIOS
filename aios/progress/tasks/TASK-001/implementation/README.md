# TASK-001 Implementation

The implementation lives in `d:\AIOS\aios\governance\` and `d:\AIOS\aios\agents\`.

```
aios/governance/
  task_registry/   # Rule 1
  dependency/      # Rule 2
  architecture/    # Rule 3
  deterministic/   # Rule 4
  evidence/        # Rule 5
  lifecycle/       # Rule 6
  regression/      # Rule 7
  gates/           # Unified Task Gate (convergence)
  cli/             # parse_spec.py, gate_check.py
aios/agents/        # orchestrator / spec-writer / critic / reviewer
```

`verify_task001.py` below runs a self-contained smoke check of all seven gates.
