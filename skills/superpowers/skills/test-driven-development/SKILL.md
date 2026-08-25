---
name: test-driven-development
description: "Use when implementing any feature or bugfix, before writing implementation code."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Test-Driven Development (AIOS-adapted)

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over. No exceptions.

## Red-Green-Refactor

1. **RED** - Write one minimal failing test showing the desired behavior.
2. **Verify RED** - Run it; confirm it fails for the RIGHT reason.
3. **GREEN** - Write minimal code to make it pass.
4. **Verify GREEN** - Run; all green.
5. **REFACTOR** - Clean up; stay green.

## When to Use
Always: new features, bug fixes, refactoring, behavior changes.
Exceptions (ask partner): throwaway prototypes, generated code, config files.

## AIOS Mapping
- AIOS `python -m pytest aios -q` with `fail_under: 80` enforces coverage.
- Pairs with `systematic-debugging` (failing test = reproduction) and
  `verification-before-completion` (red-green proof).
