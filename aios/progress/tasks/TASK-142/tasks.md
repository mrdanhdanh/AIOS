# TASK-142 — Task Breakdown

1. Định nghĩa `VerifyStatus` (PASS/FAIL/INCONCLUSIVE) + `VerificationResult` (authority locked to `aios`).
2. `VerificationEngine.verify` fail-closed: empty hash -> raise (T078).
3. Chỉ PASS -> `integrity_verified=True`; FAIL/INCONCLUSIVE -> False.
4. `provenance()` với `content_hash` (T001/T078).
5. Tests (`test_verification.py`): 6 tests.
6. Chạy pytest + gate_check.
