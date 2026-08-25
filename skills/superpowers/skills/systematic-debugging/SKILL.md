---
name: systematic-debugging
description: "Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Systematic Debugging (AIOS-adapted)

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you have not completed Phase 1, you cannot propose fixes.

## The Four Phases (complete each before the next)

### Phase 1: Root Cause Investigation
1. Read error messages carefully (stack traces, line numbers, codes).
2. Reproduce consistently (exact steps, every time?).
3. Check recent changes (git diff, commits, deps, config, env).
4. In multi-component systems, add diagnostic instrumentation at each
   boundary and run once to gather evidence showing WHERE it breaks.
5. Trace data flow backward to the source of the bad value.

### Phase 2: Pattern Analysis
- Find working examples similar to the broken one.
- Read reference implementations COMPLETELY (no skimming).
- List every difference, however small.
- Understand dependencies, config, environment assumptions.

### Phase 3: Hypothesis and Testing
- State a single hypothesis: "I think X is the root cause because Y."
- Test with the SMALLEST possible change (one variable at a time).
- Verify before continuing; if it fails, form a NEW hypothesis.

### Phase 4: Implementation
- Create a failing test case FIRST (use `test-driven-development`).
- Implement a SINGLE fix addressing the root cause.
- Verify with `verification-before-completion` before claiming success.
- If >= 3 fixes failed: STOP and question the architecture with your partner.

## Red Flags - STOP
"Quick fix for now", "just try changing X", "skip the test", "it's probably X",
"one more fix attempt" (when already tried 2+), each fix reveals a new problem
elsewhere. ALL mean: return to Phase 1.

## AIOS Mapping
- Mirrors AIOS deterministic pipeline (Rule 4): evidence before action.
- Evidence gathered maps to AIOS EvidenceStore (Rule 5) provenance chain.
- Architecture-questioning aligns with AIOS ArchitectureGuard (Rule 3).
