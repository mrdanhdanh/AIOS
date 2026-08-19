"""Automated tests for the Deterministic Control Path gate (Rule 4)."""

import pytest

from aios.governance.deterministic import (
    DeterministicControlPath,
    Request,
    ValidationError,
)


def test_deterministic_rule_avoids_llm():
    """Rule 4: when the rule decides, LLM call count must be 0."""
    calls = {"n": 0}

    def fake_llm(nr):
        calls["n"] += 1
        return "llm-plan"

    path = DeterministicControlPath(llm_fallback=fake_llm, validator=lambda s: True)
    plan = path.execute(Request(text="status", metadata={}))
    assert plan.source == "deterministic"
    assert path.llm_call_count == 0
    assert calls["n"] == 0


def test_llm_only_called_when_insufficient():
    """Rule 4: LLM is only a fallback and its output passes the validator."""
    calls = {"n": 0}

    def fake_llm(nr):
        calls["n"] += 1
        return "generated-plan"

    path = DeterministicControlPath(
        llm_fallback=fake_llm,
        validator=lambda s: s == "generated-plan",
    )
    plan = path.execute(Request(text="write a novel about governance", metadata={}))
    assert path.llm_call_count == 1
    assert calls["n"] == 1
    assert plan.source == "llm"
    assert plan.raw == "generated-plan"


def test_llm_output_failing_validation_is_rejected():
    """Rule 4: invalid LLM output must not be accepted."""
    path = DeterministicControlPath(
        llm_fallback=lambda nr: "bad-plan",
        validator=lambda s: False,
    )
    with pytest.raises(ValidationError):
        path.execute(Request(text="do something weird", metadata={}))
    # Even though called, the invalid output is rejected (never returned).
    assert path.llm_call_count == 1


def test_insufficient_without_llm_raises():
    path = DeterministicControlPath()
    with pytest.raises(RuntimeError):
        path.execute(Request(text="unknown intent", metadata={}))
