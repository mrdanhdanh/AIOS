---
name: receiving-code-review
description: "Use when you receive code review feedback that you need to address."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Receiving Code Review (AIOS-adapted)

## Process
1. Read every finding; do not batch-dismiss.
2. For each: reproduce/understand, fix at root cause (see `systematic-debugging`
   if it is a bug), re-verify with `verification-before-completion`.
3. For disagreements: record a `Ruling` with rationale; do not silently ignore.
4. Re-run the full verification gate; only then claim addressed.

## AIOS Mapping
- AIOS equivalent: `critic`/`reviewer` loops in the task lifecycle; findings
  become lifecycle artifacts (`critique-*.md`, `review.md`).
