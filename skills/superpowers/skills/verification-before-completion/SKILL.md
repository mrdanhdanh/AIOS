---
name: verification-before-completion
description: "Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Verification Before Completion (AIOS-adapted)

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you have not run the verification command in THIS message, you cannot claim
it passes.

## The Gate Function
1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete).
3. READ: Full output, exit code, failure count.
4. VERIFY: Does output confirm the claim? If NO, state actual status with evidence.
5. ONLY THEN: Make the claim (with evidence).

## Common Failures
| Claim | Requires | Not sufficient |
|-------|----------|----------------|
| Tests pass | Test output: 0 failures | Previous run, "should pass" |
| Build succeeds | Build exit 0 | Linter passing |
| Bug fixed | Original symptom passes | Code changed, assumed fixed |
| Agent completed | VCS diff shows changes | Agent reports "success" |

## Red Flags - STOP
Using "should", "probably", "seems to"; expressing satisfaction before
verification; committing without verification; trusting agent success reports;
relying on partial verification.

## AIOS Mapping
- Core of AIOS Evidence/Provenance (Rule 5): UNKNOWN never promoted to PASS.
- Enforced by `UnifiedTaskGate` (all 7 gates AND) and `gate_check.py`.
- "Fresh verification" == re-running `pytest`/`gate_check` before any DONE claim.
