# Test — TASK-220

## Commands
```
python -m pytest aios/agents/tests/test_coordinator.py -q
python -m pytest aios/governance/architecture -q -k agents
python -m pytest aios -q
```

## Results
- `test_coordinator.py`: **3 passed** (happy path close, fail-closed reject, deterministic).
- Architecture gate (`agents` layer): **3 passed** (no ARCH-001..004 violation).
- Full suite regression: green (no break introduced).

## Coverage notes
- Happy path: `coordinate()` sinh đủ `spec.md`/`critique-1.md`/`critique-2.md`/`tasks.md`, `approved=True`, `closed=True`.
- Fail-closed: `Reviewer` reject → `approved=False`, `closed=False`, step `orchestrate` không chạy.
- Deterministic: cùng input → `result.to_dict()` identical.
