"""Generate AIOS-compatible Superpowers skills + router + mapping doc.

Source of truth for the Superpowers -> AIOS integration (TASK-SUPERPOWERS).
Writes into work/20260825-superpowers-integration/generated/ so the plan's
install step can copy into the AIOS repo. Pure stdlib, deterministic, offline.

Philosophy captured (from obra/superpowers, MIT):
  - Test-Driven Development      (write tests first, always)
  - Systematic over ad-hoc       (process over guessing)
  - Complexity reduction         (simplicity as primary goal)
  - Evidence over claims         (verify before declaring success)
Plus the "using-superpowers" meta-rule: invoke the relevant skill BEFORE any
action, process skills first, then implementation skills.
"""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
GEN = os.path.join(ROOT, "work", "20260825-superpowers-integration", "generated")
PKG = os.path.join(GEN, "skills", "superpowers")
SKILLS_DIR = os.path.join(PKG, "skills")
AIOS_SKILL = os.path.join(GEN, "aios", "skill")
AIOS_TESTS = os.path.join(AIOS_SKILL, "tests")
DOCS = os.path.join(GEN, "docs")

VERSION = "1.0.0"
AUTHOR = "aios-integration"

# ---------------------------------------------------------------------------
# Skill content. Each entry: description, argument_hint, skill_md, instructions_md
# ---------------------------------------------------------------------------
SKILLS = {}

SKILLS["using-superpowers"] = dict(
    description="Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions.",
    argument_hint="",
    skill_md=r'''---
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
''',
    instructions_md=r'''You are invoking the using-superpowers meta-skill. Before any other action:
1. Run the skill-applicability check (superpowers_router.route(request)).
2. Announce the selected skill(s) and follow them in priority order.
3. Process skills (brainstorming, systematic-debugging) precede implementation skills.
''',
)

SKILLS["brainstorming"] = dict(
    description="You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation.",
    argument_hint="[request]",
    skill_md=r'''---
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
''',
    instructions_md=r'''Invoke before any creative/implementation work. Classify Spike/Bounded/Architectural, announce the path, get approval before any code. Produce spec.md for Architectural tasks.
''',
)

SKILLS["systematic-debugging"] = dict(
    description="Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes.",
    argument_hint="[symptom]",
    skill_md=r'''---
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
''',
    instructions_md=r'''On any bug/failure: complete Phase 1 (root cause) before proposing fixes. Use failing test + smallest change. After 3 failed fixes, stop and question architecture. Record evidence via AIOS EvidenceStore.
''',
)

SKILLS["test-driven-development"] = dict(
    description="Use when implementing any feature or bugfix, before writing implementation code.",
    argument_hint="",
    skill_md=r'''---
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
''',
    instructions_md=r'''Write the failing test first, watch it fail for the right reason, then write minimal code. Never write production code before a failing test.
''',
)

SKILLS["verification-before-completion"] = dict(
    description="Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims.",
    argument_hint="",
    skill_md=r'''---
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
''',
    instructions_md=r'''Before any success/completion claim or commit: identify the proving command, run it fresh, read full output + exit code, then claim only with evidence. Never trust agent reports without independent verification.
''',
)

SKILLS["writing-plans"] = dict(
    description="Use when you have a spec or requirements for a multi-step task, before touching code.",
    argument_hint="[spec]",
    skill_md=r'''---
name: writing-plans
description: "Use when you have a spec or requirements for a multi-step task, before touching code."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Writing Plans (AIOS-adapted)

Write comprehensive implementation plans assuming the engineer has zero context
for our codebase and questionable taste. Document everything: files to touch,
code, testing, docs, how to test. Bite-sized tasks. DRY. YAGNI. TDD. Frequent
commits.

## Plan Document Header (every plan MUST start with this)
```markdown
# [Feature] Implementation Plan
**Goal:** [one sentence]
**Architecture:** [2-3 sentences]
**Tech Stack:** [key tech]
**Spec:** [path to spec this plan implements]
## Global Constraints
[verbatim project-wide requirements]
```

## Task Right-Sizing
A task is the smallest unit carrying its own test cycle + reviewer gate. Each
task ends with an independently testable deliverable.

## Bite-Sized Granularity (each step one action, 2-5 min)
- "Write the failing test" / "Run it to make sure it fails" /
  "Implement minimal code" / "Run tests, make sure they pass" / "Commit".

## AIOS Mapping
- AIOS equivalent: `aios-plan` skill + `plan.yaml` (WorkflowDefinition) under
  `work/YYYYMMDD-slug/`. One node = one real command.
- Bite-sized steps map to AIOS task breakdown (`tasks.md`).
- Save plans to `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`.
''',
    instructions_md=r'''From a spec, produce a plan with header + bite-sized TDD tasks, one action per step, frequent commits. In AIOS, emit plan.yaml under work/YYYYMMDD-slug/ with permissions:[process.execute].
''',
)

SKILLS["executing-plans"] = dict(
    description="Use when you have a written implementation plan to execute in a separate session with review checkpoints.",
    argument_hint="[plan]",
    skill_md=r'''---
name: executing-plans
description: "Use when you have a written implementation plan to execute in a separate session with review checkpoints."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Executing Plans (AIOS-adapted)

Load plan, review critically, execute all tasks, report when complete.

## The Process
### Step 1: Load and Review Plan
1. Ensure an isolated workspace (`using-git-worktrees`).
2. Read plan; review critically; raise concerns before starting.
3. Create todos for plan items; proceed.

### Step 2: Execute Tasks
For each task: mark in_progress -> follow each step exactly -> run verifications
as specified -> mark completed.

### Step 3: Complete Development
Announce `finishing-a-development-branch`; follow it to verify tests, present
options, execute choice.

## When to Stop and Ask
Hit a blocker (missing dep, test fails, unclear instruction), plan has critical
gaps, or you do not understand an instruction. Ask rather than guess.

## AIOS Mapping
- AIOS equivalent: `aiagent execute <plan.yaml> --work-dir <dir> --yes` after
  `AIOS_REAL_EXECUTION_ENABLED=1`.
- Review checkpoints == AIOS `REVIEWED` + `UnifiedTaskGate`.
- Never implement on main without explicit consent (AIOS working-tree hygiene).
''',
    instructions_md=r'''Load the plan, review critically, execute task-by-task with verifications, stop and ask on blockers. Finish via finishing-a-development-branch. In AIOS use aiagent execute with a real-execution flag.
''',
)

SKILLS["subagent-driven-development"] = dict(
    description="Use when executing implementation plans with independent tasks in the current session.",
    argument_hint="[plan]",
    skill_md=r'''---
name: subagent-driven-development
description: "Use when executing implementation plans with independent tasks in the current session."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Subagent-Driven Development (AIOS-adapted)

Execute plan by dispatching a fresh implementer subagent per task, a task review
(spec compliance + code quality) after each, and a broad whole-branch review at
the end.

## Core Principle
Fresh subagent per task + task review + broad final review = high quality, fast
iteration. Subagents never inherit your session context; you construct exactly
what they need.

## Continuous Execution
Do not pause to check in between tasks. Execute all tasks from the plan without
stopping. The only reasons to stop are: an irreversible/destructive operation; a
security-sensitive action; a side effect outside the worktree (merge, push,
publish); or a plan so broken every path is a guess.

## Rulings, not stalls
A running plan does not wait on a human. Conflicts, ambiguities, plan defects -
decide them. Record every decision in the ledger as
`Ruling: <what> - <why> - <cost if wrong>` and keep going.

## AIOS Mapping
- AIOS equivalent: `Orchestrator` dispatches `spec_writer`/`critic`/`reviewer`
  agents; each task gets its own `aios/progress/tasks/TASK-xxx/` lifecycle.
- The ledger == AIOS `AuditTrail` (runtime kernel) + `LOG.md`.
- Final broad review == AIOS `reviewer` agent producing `review.md`.
''',
    instructions_md=r'''For independent plan tasks: dispatch a fresh subagent per task, review spec+quality after each, broad review at end. Decide conflicts with logged rulings; stop only for destructive/security/external-side-effect/broken-plan.
''',
)

SKILLS["requesting-code-review"] = dict(
    description="Use when your implementation is complete and you want independent review before merging.",
    argument_hint="[branch]",
    skill_md=r'''---
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
''',
    instructions_md=r'''Before merge: verify, build a review package (diff + spec checklist + test evidence), dispatch a fresh reviewer. Hand findings to receiving-code-review.
''',
)

SKILLS["receiving-code-review"] = dict(
    description="Use when you receive code review feedback that you need to process and address.",
    argument_hint="[feedback]",
    skill_md=r'''---
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
''',
    instructions_md=r'''Process every review finding: understand, fix at root, re-verify. Record disagreements as rulings. Re-run the full gate before claiming addressed.
''',
)

SKILLS["using-git-worktrees"] = dict(
    description="Use when starting implementation work that should be isolated from the main working tree.",
    argument_hint="[branch]",
    skill_md=r'''---
name: using-git-worktrees
description: "Use when starting implementation work that should be isolated from the main working tree."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Using Git Worktrees (AIOS-adapted)

## Process
1. Create an isolated workspace for the task (never implement on main without
   explicit consent).
2. Keep the worktree scoped to one plan/task.
3. Run verifications inside the worktree before any merge/push.

## AIOS Mapping
- AIOS convention: every job lives under `work/YYYYMMDD-slug/` (plans/, scripts/,
  logs/, generated source). This is AIOS's worktree-equivalent isolation.
- `aiagent execute --work-dir <dir>` runs plans in isolation.
''',
    instructions_md=r'''Isolate implementation work in a dedicated worktree (AIOS: work/YYYYMMDD-slug/). Never implement on main without consent. Verify inside the worktree before merge.
''',
)

SKILLS["finishing-a-development-branch"] = dict(
    description="Use when implementation is complete and you are ready to verify, present options, and close the branch.",
    argument_hint="[branch]",
    skill_md=r'''---
name: finishing-a-development-branch
description: "Use when implementation is complete and you are ready to verify, present options, and close the branch."
license: MIT
metadata:
  author: aios-integration
  version: "1.0.0"
---

# Finishing a Development Branch (AIOS-adapted)

## Process
1. Run the FULL verification gate (`verification-before-completion`): tests,
   linter, build, evidence.
2. Present options to your partner (merge / squash / keep / discard).
3. On choice, execute it. For merge/push, this is a side effect outside the
   worktree -> STOP and ask first.
4. Auto-commit source when the task reaches DONE (AIOS Rule 8 / Quy tắc 8).

## AIOS Mapping
- AIOS Rule 8 (Auto-COMMIT): a scheduled TASK reaching DONE (Unified Gate PASS)
  MUST commit source in the same session with message `TASK-xxx: <title> - DONE`
  plus PLAN.md/LOG.md/STATS.md updates. Never leave a dirty working tree.
- DONE only via `UnifiedTaskGate` (all 7 gates AND).
''',
    instructions_md=r'''When done: run full verification, present merge/squash/keep/discard options, ask before external side-effects (push/merge). On DONE, auto-commit per AIOS Rule 8 with updated progress docs.
''',
)


def write_skill(sid: str, data: dict) -> None:
    base = os.path.join(SKILLS_DIR, sid)
    os.makedirs(os.path.join(base, "catalog"), exist_ok=True)
    os.makedirs(os.path.join(base, "prompts"), exist_ok=True)

    with open(os.path.join(base, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(data["skill_md"])

    with open(os.path.join(base, "prompts", "instructions.md"), "w", encoding="utf-8") as f:
        f.write(data["instructions_md"])

    manifest = {
        "author": AUTHOR,
        "checksum": "",
        "configuration": {},
        "dependencies": [],
        "description": data["description"],
        "enabled": False,
        "entrypoint": "SKILL.md",
        "install_location": f"/skills/{sid}/1.0.0",
        "install_source": "git",
        "metadata": {
            "frontmatter": {
                "argument-hint": data["argument_hint"],
                "description": data["description"],
                "license": "MIT",
                "metadata": {"author": AUTHOR, "version": VERSION},
                "name": sid,
            },
            "source": "github-copilot-skill",
        },
        "name": sid,
        "permissions": [],
        "required_capabilities": [],
        "resources": {"instructions_chars": len(data["instructions_md"])},
        "runtime": "python3.11",
        "skill_id": sid,
        "status": "pending",
        "version": VERSION,
    }
    with open(os.path.join(base, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    catalog = {
        "kind": "skill",
        "layout": "claude",
        "manifest_path": "manifest.json",
        "name": sid,
        "plugin_manifest_path": "plugin_manifest.json",
        "skill_id": sid,
        "source": "git",
        "version": VERSION,
    }
    with open(os.path.join(base, "catalog", f"skill-{sid}.json"), "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)


def write_router() -> None:
    os.makedirs(AIOS_SKILL, exist_ok=True)
    os.makedirs(AIOS_TESTS, exist_ok=True)
    content = '''"""Superpowers skill router (AIOS integration, TASK-SUPERPOWERS).

Deterministic, offline-first, no LLM. Given a free-text request, returns the
ordered set of applicable Superpowers skills, implementing the
`using-superpowers` meta-rule: the meta-skill is always considered first, then
process skills (brainstorming, systematic-debugging) take priority over
implementation skills.

Layering: lives in the `skill` package; imports only stdlib. Architecture-guard
safe (no upward imports).
"""

from __future__ import annotations

from typing import List

META_SKILL = "using-superpowers"
PROCESS_SKILLS = ("brainstorming", "systematic-debugging")

# request keyword -> skill id
SKILL_KEYWORDS = {
    "brainstorming": ["build", "create", "feature", "implement", "design", "add ", "new ", "component", "subsystem", "architect"],
    "systematic-debugging": ["bug", "fix", "error", "fail", "unexpected", "broken", "debug", "traceback", "exception", "regress"],
    "test-driven-development": ["tdd", "test", "coverage"],
    "verification-before-completion": ["complete", "done", "verify", "pass", "claim", " pr", "commit", "push", "finished"],
    "writing-plans": ["plan", "breakdown", "spec", "tasks"],
    "executing-plans": ["execute plan", "run plan", "implement plan"],
    "subagent-driven-development": ["subagent", "parallel", "delegate", "dispatch"],
    "requesting-code-review": ["code review", "reviewer", "review request"],
    "receiving-code-review": ["review feedback", "address review", "review comments"],
    "using-git-worktrees": ["worktree", "branch isolation", "isolated workspace"],
    "finishing-a-development-branch": ["finish branch", "merge branch", "close branch", "finish development"],
}

ALL_SKILLS = [META_SKILL] + list(SKILL_KEYWORDS.keys())


def _matches(skill_id: str, request: str) -> bool:
    if skill_id == META_SKILL:
        return True
    low = request.lower()
    return any(kw in low for kw in SKILL_KEYWORDS[skill_id])


def route(request: str) -> List[str]:
    """Return ordered applicable skill ids for a request.

    Order: meta-skill first, then process skills, then the rest (stable by
    SKILL_KEYWORDS definition order). Deterministic.
    """
    if not request or not request.strip():
        return [META_SKILL]
    applicable = [sid for sid in SKILL_KEYWORDS if _matches(sid, request)]
    ordered = [META_SKILL]
    for sid in applicable:
        if sid in PROCESS_SKILLS:
            ordered.append(sid)
    for sid in applicable:
        if sid not in PROCESS_SKILLS and sid != META_SKILL:
            ordered.append(sid)
    # de-dup preserve order
    seen = set()
    result = []
    for sid in ordered:
        if sid not in seen:
            seen.add(sid)
            result.append(sid)
    return result


def applicable_skills(request: str) -> List[str]:
    """Public alias used by the skill manager bridge."""
    return route(request)
'''
    with open(os.path.join(AIOS_SKILL, "superpowers_router.py"), "w", encoding="utf-8") as f:
        f.write(content)

    test_content = '''"""Tests for the Superpowers skill router (TASK-SUPERPOWERS)."""

from aios.skill.superpowers_router import (
    META_SKILL,
    PROCESS_SKILLS,
    route,
    applicable_skills,
)


def test_meta_skill_always_present():
    assert route("hello world")[0] == META_SKILL


def test_empty_request_returns_meta_only():
    assert route("") == [META_SKILL]
    assert route("   ") == [META_SKILL]


def test_bug_request_prioritizes_systematic_debugging():
    r = route("fix this bug, it fails with a traceback")
    assert META_SKILL in r
    assert "systematic-debugging" in r
    # process skill precedes implementation skills (when both present)
    if "test-driven-development" in r:
        assert r.index("systematic-debugging") < r.index("test-driven-development")


def test_build_request_includes_brainstorming():
    r = route("let's build a new feature and write a plan")
    assert "brainstorming" in r
    assert "writing-plans" in r


def test_verify_request_includes_verification_skill():
    r = route("is it done? verify the tests pass before commit")
    assert "verification-before-completion" in r


def test_process_skills_before_implementation():
    r = route("build a feature then fix a bug and verify it is done")
    # both process skills appear before any non-process matched skill
    proc_positions = [r.index(p) for p in PROCESS_SKILLS if p in r]
    impl_positions = [r.index(s) for s in r if s not in PROCESS_SKILLS and s != META_SKILL]
    if proc_positions and impl_positions:
        assert max(proc_positions) < min(impl_positions)


def test_applicable_skills_alias():
    assert applicable_skills("review feedback") == route("review feedback")
'''
    with open(os.path.join(AIOS_TESTS, "test_superpowers_router.py"), "w", encoding="utf-8") as f:
        f.write(test_content)


def write_mapping_doc() -> None:
    os.makedirs(DOCS, exist_ok=True)
    doc = '''# Superpowers -> AIOS Integration

Source methodology: [obra/superpowers](https://github.com/obra/superpowers) (MIT).
Integrated as AIOS skills under `skills/superpowers/` plus a deterministic router
`aios/skill/superpowers_router.py`.

## Philosophy (Superpowers) -> AIOS component

| Superpowers principle | AIOS equivalent |
|-----------------------|-----------------|
| Test-Driven Development (write tests first) | `python -m pytest aios -q`, `fail_under: 80` (pyproject.toml) |
| Systematic over ad-hoc (process over guessing) | Deterministic pipeline (Rule 4), `governance/deterministic/pipeline.py` |
| Complexity reduction (simplicity first) | ArchitectureGuard (Rule 3), `LAYER_ORDER` enforcement |
| Evidence over claims (verify before success) | EvidenceStore + provenance (Rule 5), `UnifiedTaskGate` |
| Skill-before-action (using-superpowers) | `superpowers_router.route()` + deterministic-first (Rule 4) |

## Skills delivered

Twelve AIOS-adapted skills, each with `SKILL.md`, `manifest.json`,
`catalog/skill-<id>.json`, `prompts/instructions.md`:

1. `using-superpowers` - meta-rule: invoke skill before any action.
2. `brainstorming` - Spike/Bounded/Architectural paths + approval HARD-GATE.
3. `systematic-debugging` - 4 phases, iron law: root cause before fix.
4. `test-driven-development` - RED/GREEN/REFACTOR, no code before failing test.
5. `verification-before-completion` - no claim without fresh evidence.
6. `writing-plans` - bite-sized TDD tasks (maps to `aios-plan` / `plan.yaml`).
7. `executing-plans` - load, review, execute, verify, finish.
8. `subagent-driven-development` - fresh subagent per task + ledger of rulings.
9. `requesting-code-review` - review package + fresh reviewer.
10. `receiving-code-review` - process findings at root, re-verify.
11. `using-git-worktrees` - isolated workspace (maps to `work/YYYYMMDD-slug/`).
12. `finishing-a-development-branch` - verify, present options, auto-commit (Rule 8).

## Router behavior

`route(request)` returns ordered skill ids: meta-skill first, then process
skills (`brainstorming`, `systematic-debugging`), then implementation skills.
Deterministic, no LLM, architecture-guard safe.

## Gaps / future work

- Wire `superpowers_router` into the AIOS `SkillManager` so agent dispatch
  consults it before acting (currently advisory via AGENTS.md).
- Add drill-style eval harness for the skills (Superpowers uses
  superpowers-evals); AIOS could reuse `harness/` for this.
- Port the visual-companion telemetry opt-out (`SUPERPOWERS_DISABLE_TELEMETRY`)
  semantics into AIOS observability config.
'''
    with open(os.path.join(DOCS, "superpowers-integration.md"), "w", encoding="utf-8") as f:
        f.write(doc)


def main() -> None:
    os.makedirs(SKILLS_DIR, exist_ok=True)
    for sid, data in SKILLS.items():
        write_skill(sid, data)
    write_router()
    write_mapping_doc()
    print(f"Generated {len(SKILLS)} skills + router + tests + mapping doc under {GEN}")


if __name__ == "__main__":
    main()
