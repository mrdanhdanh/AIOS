"""Unit + Contract + Integration + Architecture + Regression tests (TASK-125)."""

from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest

from aios.coder.contract import (
    CoderAgentContract,
    CoderAgentError,
    CoderAgentStateMachine,
    CoderCapabilityResolver,
    CodingTaskState,
)
from aios.capability.capability import CapabilityContract, CapabilityRegistry, CapabilityError


# --------------------------------------------------------------------------- #
# Contract
# --------------------------------------------------------------------------- #
def test_agent_io_free_capability_injected_ok():
    contract = CoderAgentContract(
        agent_id="coder-1", capabilities=("code.read", "code.write")
    )
    assert contract.io_free is True
    assert contract.can_inject("code.read") is True
    assert contract.can_inject("code.exec") is False


def test_agent_must_be_io_free():
    with pytest.raises(CoderAgentError):
        CoderAgentContract(agent_id="coder-1", io_free=False)


def test_agent_id_required():
    with pytest.raises(CoderAgentError):
        CoderAgentContract(agent_id="")


# --------------------------------------------------------------------------- #
# State machine — valid transitions
# --------------------------------------------------------------------------- #
def _sm():
    c = CoderAgentContract(agent_id="coder-1", capabilities=("code.read",))
    sm = CoderAgentStateMachine(c)
    sm.init("t1")
    return sm


def test_valid_transition_chain():
    sm = _sm()
    assert sm.current("t1") == CodingTaskState.PLANNED
    sm.transition("t1", CodingTaskState.CODING, {"plan"})
    sm.transition("t1", CodingTaskState.REVIEWING, {"generated_code"})
    sm.transition("t1", CodingTaskState.PATCHING, {"review_result"})
    sm.transition("t1", CodingTaskState.DONE, {"final_artifact", "evidence"})
    assert sm.current("t1") == CodingTaskState.DONE


# --------------------------------------------------------------------------- #
# TASK-230 — Coder Agent <-> Capability Registry
# --------------------------------------------------------------------------- #
def _registry_with(capability_id: str) -> CapabilityRegistry:
    reg = CapabilityRegistry()
    reg.register(
        CapabilityContract(
            capability_id=capability_id,
            version="1.0.0",
            description="test capability",
            tags=["test"],
        )
    )
    reg.register_tool(capability_id, "tool-x", priority=0, health="healthy")
    return reg


def test_resolver_resolves_declared_and_registered():
    contract = CoderAgentContract(agent_id="coder-1", capabilities=("code_read",))
    reg = _registry_with("code_read")
    resolver = CoderCapabilityResolver(contract, reg)
    assert resolver.resolve("code_read") == ["tool-x"]
    assert resolver.is_resolvable("code_read") is True


def test_resolver_fails_when_not_declared():
    contract = CoderAgentContract(agent_id="coder-1", capabilities=("code_read",))
    reg = _registry_with("code_write")
    resolver = CoderCapabilityResolver(contract, reg)
    with pytest.raises(CoderAgentError):
        resolver.resolve("code_write")
    assert resolver.is_resolvable("code_write") is False


def test_resolver_fails_when_not_registered():
    contract = CoderAgentContract(agent_id="coder-1", capabilities=("code_exec",))
    reg = _registry_with("code_read")
    resolver = CoderCapabilityResolver(contract, reg)
    with pytest.raises(CoderAgentError):
        resolver.resolve("code_exec")


def test_reviewing_to_done_direct():
    sm = _sm()
    sm.transition("t1", CodingTaskState.CODING, {"plan"})
    sm.transition("t1", CodingTaskState.REVIEWING, {"generated_code"})
    sm.transition("t1", CodingTaskState.DONE, {"final_artifact", "evidence"})
    assert sm.current("t1") == CodingTaskState.DONE


# --------------------------------------------------------------------------- #
# Fail-closed — missing artifact rejects
# --------------------------------------------------------------------------- #
def test_transition_missing_artifact_rejects():
    sm = _sm()
    with pytest.raises(CoderAgentError):
        sm.transition("t1", CodingTaskState.CODING, set())  # missing 'plan'


def test_transition_policy_rejected():
    sm = _sm()
    with pytest.raises(CoderAgentError):
        sm.transition("t1", CodingTaskState.CODING, {"plan"}, policy_ok=False)


def test_illegal_transition_rejects():
    sm = _sm()
    with pytest.raises(CoderAgentError):
        sm.transition("t1", CodingTaskState.DONE, {"final_artifact", "evidence"})


# --------------------------------------------------------------------------- #
# Deterministic
# --------------------------------------------------------------------------- #
def test_deterministic_same_state_artifact():
    sm_a = _sm()
    sm_b = _sm()
    sm_a.transition("t1", CodingTaskState.CODING, {"plan"})
    sm_b.transition("t1", CodingTaskState.CODING, {"plan"})
    assert sm_a.current("t1") == sm_b.current("t1") == CodingTaskState.CODING
    # same inputs -> identical provenance content hash
    assert sm_a.history("t1")[0].content_hash == sm_b.history("t1")[0].content_hash


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #
def test_transition_evidence_provenance():
    sm = _sm()
    sm.transition("t1", CodingTaskState.CODING, {"plan"})
    chain = sm.provenance_chain("t1")
    assert len(chain) == 1
    rec = chain[0]
    assert rec["from_state"] == "PLANNED"
    assert rec["to_state"] == "CODING"
    assert rec["evidence_id"].startswith("ev-")
    assert len(rec["content_hash"]) == 64  # sha256 hex


# --------------------------------------------------------------------------- #
# Architecture — module must not import forbidden primitives
# --------------------------------------------------------------------------- #
def test_module_has_no_forbidden_imports():
    src = Path(__file__).resolve().parents[1] / "contract.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    forbidden = {"subprocess", "os", "aios.runtime.providers", "aios.runtime.filesystem"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imported.add(mod)
    assert not (imported & forbidden), f"forbidden imports: {imported & forbidden}"


def test_contract_module_path_is_unknown_layer():
    # 'coder' is not in LAYER_KEYWORDS -> classified 'unknown' (infra).
    from aios.governance.architecture.guard import classify_module

    assert classify_module("aios/coder/contract.py") == "unknown"
