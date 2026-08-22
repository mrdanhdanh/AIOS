"""Tests for SkillDistiller + Static Deploy (TASK-083, M11)."""

from __future__ import annotations

import pytest

from aios.skill_distiller.distiller import (
    SkillDistiller,
    StaticPackage,
    StaticDeploy,
    DistillerError,
)


def _workflow():
    return {
        "name": "summarizer",
        "inputs": {"text": "string"},
        "outputs": {"summary": "string"},
    }


def test_distill_produces_contract_1_0():
    d = SkillDistiller()
    skill = d.distill(_workflow(), "skill.sum", evidence_ref="ev-1")
    assert skill.contract_version == "1.0.0"
    assert skill.conforms_to == "architecture(1.0)"
    assert d.conforms(skill) is True


def test_distill_deterministic():
    d = SkillDistiller()
    a = d.distill(_workflow(), "skill.sum")
    b = d.distill(_workflow(), "skill.sum")
    assert a.to_dict() == b.to_dict()


def test_deploy_rejects_nonconforming_contract():
    d = SkillDistiller()
    skill = d.distill(_workflow(), "skill.sum")
    skill.contract_version = "0.9.0"  # not 1.0
    pkg = StaticPackage("p", "def run():\n    return 1\n")
    with pytest.raises(DistillerError):
        StaticDeploy(d).deploy(skill, pkg)


def test_deploy_rejects_dynamic_dependency():
    d = SkillDistiller()
    skill = d.distill(_workflow(), "skill.sum", evidence_ref="ev-1")
    pkg = StaticPackage("p", "import subprocess\n")
    with pytest.raises(DistillerError):
        StaticDeploy(d).deploy(skill, pkg)


def test_deploy_rejects_guard_violation():
    d = SkillDistiller()
    skill = d.distill(_workflow(), "skill.sum", evidence_ref="ev-1")
    # A skill-layer module importing a forbidden provider adapter trips the guard.
    bad_src = "from aios.core.providers import Something\n"
    pkg = StaticPackage("p", bad_src)
    with pytest.raises(DistillerError):
        StaticDeploy(d).deploy(skill, pkg)


def test_deploy_success():
    d = SkillDistiller()
    skill = d.distill(_workflow(), "skill.sum", evidence_ref="ev-1")
    pkg = StaticPackage("p", "def run(text):\n    return text[:10]\n")
    result = StaticDeploy(d).deploy(skill, pkg)
    assert result["deployed"] is True
    assert result["skill_id"] == "skill.sum"
