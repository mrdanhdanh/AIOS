---
name: brainstorming
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Brainstorming Ideas Into Designs (AIOS-adapted)

Turn ideas into fully formed designs and specs through collaborative dialogue.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, or take any
implementation action until you have told your human partner what you intend
and they have approved it. The ceremony scales with the task; the approval
gate never does.
</HARD-GATE>

## Three Paths

Classify the request and say the classification out loud so your partner can
override it:

- **Spike** - a feasibility question whose output is an answer, not code you
  keep. Present the question + probe plan in 2-3 sentences, get a nod, then
  investigate as cheaply as correctness allows. No spec file.
- **Bounded** - a well-scoped change to code that already exists in this repo.
  Ask the clarifying questions that matter, present a short design IN CHAT,
  and STOP. Implementation starts only after approval. No spec file.
- **Architectural** - new projects/subsystems or interface changes. Follow the
  full process: questions, approaches, sectioned design, written spec, then
  the `writing-plans` skill.

When in doubt, take the heavier path. Hidden complexity upgrades the path
mid-task (stop, say so, step up). Nothing downgrades.

## Anti-Pattern: "Too Simple To Need Approval"

Every path ends with your partner approving your intent before implementation.
A todo list, a single-function utility, a config change - the design may be
two sentences in chat, but you MUST present it and get approval.

## Checklist

**Spike:** explore context -> present question + probe plan -> approval -> investigate -> report findings (label anything built as throwaway).
**Bounded:** explore context -> ask clarifying questions -> present short design -> approval -> implement.
**Architectural:** explore -> ask questions -> present approaches -> present sectioned design -> write spec -> `writing-plans`.

## AIOS Mapping

- Maps to AIOS governance gates 1-6: SPEC -> CRITIQUE x2 -> BREAKDOWN -> REVIEW.
- The written spec is `spec.md` in `aios/progress/tasks/TASK-xxx/`.
- Approval gate == AIOS `REVIEWED` lifecycle artifact requirement.
