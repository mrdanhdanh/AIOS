# Self-Improvement Proposal — Self-improve: harden retry-loop

**Target module:** `retry-loop`

**Confidence:** 1.00

**Source signals:**
- retry-0:FAIL
- retry-1:FAIL
- retry-2:FAIL
- retry-3:FAIL
- retry-4:FAIL

# Self-Improvement Spec — retry-loop

## Problem
Recurring governance/evidence signals from `retry-loop`:
- retry-0:FAIL
- retry-1:FAIL
- retry-2:FAIL
- retry-3:FAIL
- retry-4:FAIL

## Objective
Reduce recurrence via deterministic hardening (fail-closed, provenance-bearing).

## Acceptance Criteria
1. Root-cause analysis recorded with evidence links.
2. Fix passes UnifiedTaskGate.
3. Regression covers the failing path.

