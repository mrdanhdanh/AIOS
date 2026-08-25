# TASK-238 — Test

- `test_lifecycle_promotes_when_all_gates_pass`: mọi gate pass -> PROMOTED, artifact only.
- `test_lifecycle_rejects_without_proposal`: không proposal -> PROPOSAL, không promote.
- `test_lifecycle_rejects_on_failed_independent`: independent fail -> INDEPENDENT.
- `test_lifecycle_rejects_on_failed_regression`: regression fail -> REGRESSION.
- `test_lifecycle_deterministic_same_inputs`: cùng input -> cùng report.

Kết quả: 5 passed.
