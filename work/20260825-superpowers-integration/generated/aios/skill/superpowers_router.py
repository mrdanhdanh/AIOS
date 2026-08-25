"""Superpowers skill router (AIOS integration, TASK-SUPERPOWERS).

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
