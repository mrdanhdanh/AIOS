---
name: using-superpowers
description: "Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Using Superpowers (AIOS-adapted)

## The Rule

**Invoke the relevant or requested skill BEFORE any response or action** -
including clarifying questions, exploring the codebase, or checking files.
If it turns out wrong for the situation, you do not have to use it.

Announce "Using [skill] to [purpose]" and follow the skill exactly. If it has
a checklist, create a todo per item.

## Skill Priority (process skills first)

When multiple skills apply, process skills come first - they set the approach,
then implementation skills carry it out.

- "Let's build X" -> `brainstorming` first, then implementation skills.
- "Fix this bug" -> `systematic-debugging` first, then domain skills.
- "Is it done?" / "Tests pass?" -> `verification-before-completion` before any claim.

## Iron Law

```
NO ACTION WITHOUT A SKILL-APPLICABILITY CHECK FIRST
```

If you have not checked whether a skill applies, you cannot respond.

## Red Flags (rationalizing)

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "I can check git/files quickly" | Files lack conversation context. Check first. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "The skill is overkill" | Simple things become complex. Use it. |

## AIOS Mapping

- Mirrors AIOS deterministic-first (Rule 4): never jump to the LLM/default path.
- Enforced by `aios/skill/superpowers_router.py` (deterministic request -> skill set).
- User instructions (AGENTS.md, direct requests) take precedence over skills.
