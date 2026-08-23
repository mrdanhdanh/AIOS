# TASK-030 Implementation — Execution Verification + Evidence + Replay

Implementation lives in `aios/harness/` (M6 Harness — Verification).

```
aios/harness/
  verification.py  # Verification pipeline (execution trace → verdict)
  contracts.py     # EvidencePackage, VerificationResult
  kernel.py        # HarnessKernel (verify step)
  replay/          # ReplayEngine (deterministic replay, T079)
  tests/
    test_verification.py
    test_replay.py
```

Verifies execution and produces replayable evidence. `EvidencePackage` carries provenance (`run_id`, `producer`, `content_hash`). Replay is deterministic.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
