---
name: requesting-code-review
description: "Use when your implementation is complete and you want independent review before merging."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Requesting Code Review (AIOS-adapted)

## Process
1. Ensure tests pass and `verification-before-completion` is satisfied.
2. Generate a review package: diff scope, spec compliance checklist, test
   evidence, known trade-offs.
3. Dispatch a reviewer (fresh context) with the package.
4. Receive findings; hand off to `receiving-code-review`.

## AIOS Mapping
- AIOS equivalent: `critic` agent produces `critique-1.md`/`critique-2.md`;
  `reviewer` agent produces `review.md`.
- Review package == AIOS evidence artifacts in the task folder.
