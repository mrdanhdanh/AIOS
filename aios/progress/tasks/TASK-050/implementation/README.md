# TASK-050 Implementation — Autonomous Goal Engine

Implementation lives in `aios/autonomous_goal/` (M9 Autonomy — Goal Engine).

```
aios/autonomous_goal/
  contracts.py    # Goal, GoalStatus, GoalPriority
  engine.py       # GoalEngine (create/update/progress)
  state_machine.py# Goal state machine (policy boundary)
  policy.py       # Goal policy (evidence, provenance)
  __init__.py     # re-exports
  tests/
    test_engine.py
    test_state_machine.py
    test_policy.py
```

Long-horizon goal management with objectives/progress/policy boundary/evidence.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
