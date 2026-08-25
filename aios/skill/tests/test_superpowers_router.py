"""Tests for the Superpowers skill router (TASK-SUPERPOWERS)."""

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
