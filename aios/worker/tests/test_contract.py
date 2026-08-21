"""Tests for Worker contracts — AC-013-01/06/07 (TASK-013)."""

import pytest

from aios.worker.contract import (
    WorkerContract,
    WorkerContext,
    WorkerError,
    WorkerEvidence,
    WorkerRequest,
    WorkerResult,
    WorkerResultStatus,
    WorkerType,
    compute_hash,
)


# -- WorkerContract AC-013-01: 10 mandatory fields --

def test_worker_contract_create_minimal():
    c = WorkerContract.create(
        worker_id="general-worker",
        worker_type=WorkerType.GENERAL,
        version="1.0.0",
        capabilities=["research", "summarize"],
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        lifecycle={"states": ["REGISTERED", "READY"]},
        execution_context={"run_id": "string"},
        policy_context={"permissions": "list"},
        evidence_contract={"required": False},
    )
    c.validate()
    assert c.worker_id == "general-worker"
    assert c.worker_type == WorkerType.GENERAL
    assert c.version == "1.0.0"


def test_worker_contract_all_ten_fields_present():
    c = WorkerContract.create(
        worker_id="coder-worker",
        worker_type="coder",
        capabilities=["code.read", "code.write"],
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        lifecycle={"states": ["REGISTERED"]},
        execution_context={"run_id": "string"},
        policy_context={"permissions": "list"},
        evidence_contract={"required": True},
        description="coder",
    )
    d = c.to_dict()
    for field in ["worker_id", "worker_type", "version", "capabilities", "input_schema", "output_schema", "lifecycle", "execution_context", "policy_context", "evidence_contract"]:
        assert field in d, f"missing field {field}"


def test_worker_contract_invalid_id():
    with pytest.raises(WorkerError):
        WorkerContract.create(worker_id="", worker_type=WorkerType.GENERAL, capabilities=[], input_schema={}, output_schema={}, lifecycle={}, execution_context={}, policy_context={}, evidence_contract={})
    with pytest.raises(WorkerError):
        WorkerContract.create(worker_id="123bad", worker_type=WorkerType.GENERAL, capabilities=[], input_schema={}, output_schema={}, lifecycle={}, execution_context={}, policy_context={}, evidence_contract={})


def test_worker_contract_invalid_version():
    with pytest.raises(WorkerError):
        WorkerContract.create(worker_id="w1", worker_type=WorkerType.GENERAL, version="not-semver", capabilities=[], input_schema={}, output_schema={}, lifecycle={}, execution_context={}, policy_context={}, evidence_contract={})


def test_worker_contract_invalid_capability():
    with pytest.raises(WorkerError):
        WorkerContract.create(worker_id="w1", worker_type=WorkerType.GENERAL, capabilities=[""], input_schema={}, output_schema={}, lifecycle={}, execution_context={}, policy_context={}, evidence_contract={})


def test_worker_contract_invalid_worker_type():
    with pytest.raises(WorkerError):
        WorkerContract.create(worker_id="w1", worker_type="invalid_type", capabilities=[], input_schema={}, output_schema={}, lifecycle={}, execution_context={}, policy_context={}, evidence_contract={})


def test_worker_contract_to_dict_from_dict_roundtrip():
    c = WorkerContract.create(
        worker_id="doctor-worker",
        worker_type=WorkerType.DOCTOR,
        version="1.2.3",
        capabilities=["diagnose.task"],
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        lifecycle={"states": ["READY"]},
        execution_context={"run_id": "string"},
        policy_context={"permissions": "list"},
        evidence_contract={"required": True},
        description="doctor",
        metadata={"owner": "team-a"},
    )
    d = c.to_dict()
    c2 = WorkerContract.from_dict(d)
    assert c2.worker_id == c.worker_id
    assert c2.worker_type == c.worker_type
    assert c2.version == c.version
    assert c2.capabilities == c.capabilities
    assert c2.metadata["owner"] == "team-a"


def test_worker_contract_four_types():
    for wtype in [WorkerType.GENERAL, WorkerType.CODER, WorkerType.DOCTOR, WorkerType.SYSTEM_DOCTOR]:
        c = WorkerContract.create(
            worker_id=f"{wtype.value}-worker",
            worker_type=wtype,
            capabilities=["cap.a"],
            input_schema={},
            output_schema={},
            lifecycle={},
            execution_context={},
            policy_context={},
            evidence_contract={},
        )
        assert c.worker_type == wtype


# -- WorkerRequest AC-013-01/04 --

def test_worker_request_create():
    req = WorkerRequest.create(
        task_id="task-001",
        objective={"description": "Fix failing test"},
        allowed_capabilities=["code.read", "code.write"],
        context={"workspace": "project-a"},
        policy_context={"network": "denied"},
    )
    req.validate()
    assert req.task_id == "task-001"
    assert req.allowed_capabilities == ["code.read", "code.write"]
    assert req.context["workspace"] == "project-a"


def test_worker_request_invalid_task_id():
    with pytest.raises(WorkerError):
        WorkerRequest.create(task_id="", objective={}).validate()
    with pytest.raises(WorkerError):
        WorkerRequest(task_id="", objective={}).validate()


def test_worker_request_to_dict_from_dict():
    req = WorkerRequest.create(task_id="t1", objective={"description": "do work"}, allowed_capabilities=["research"])
    d = req.to_dict()
    req2 = WorkerRequest.from_dict(d)
    assert req2.task_id == req.task_id
    assert req2.allowed_capabilities == req.allowed_capabilities


def test_worker_request_goal_id():
    req = WorkerRequest.create(task_id="t1", goal_id="goal-001", objective={})
    assert req.goal_id == "goal-001"
    d = req.to_dict()
    assert d["goal_id"] == "goal-001"


# -- WorkerContext AC-013-04/08 --

def test_worker_context_create():
    ctx = WorkerContext.create(task_id="task-001", worker_id="coder-worker", capability_scope=["code.read"], permissions=["filesystem.workspace"])
    ctx.validate()
    assert ctx.task_id == "task-001"
    assert ctx.worker_id == "coder-worker"
    assert ctx.can_use_capability("code.read") is True
    assert ctx.can_use_capability("network.outbound") is False


def test_worker_context_invalid():
    with pytest.raises(WorkerError):
        WorkerContext.create(task_id="", worker_id="w1", capability_scope=[]).validate()
    with pytest.raises(WorkerError):
        WorkerContext.create(task_id="t1", worker_id="", capability_scope=[]).validate()


def test_worker_context_to_dict_from_dict():
    ctx = WorkerContext.create(task_id="t1", worker_id="w1", capability_scope=["cap.a"], permissions=["p1"])
    d = ctx.to_dict()
    ctx2 = WorkerContext.from_dict(d)
    assert ctx2.task_id == ctx.task_id
    assert ctx2.capability_scope == ctx.capability_scope


def test_worker_context_isolation():
    ctx = WorkerContext.create(task_id="t1", worker_id="w1", capability_scope=["code.read"])
    assert ctx.can_use_capability("code.read") is True
    assert ctx.can_use_capability("code.write") is False
    # Worker cannot self-expand scope — must be in context
    assert "network.outbound" not in ctx.capability_scope


# -- WorkerResult AC-013-06 --

def test_worker_result_create_succeeded():
    r = WorkerResult.create(status=WorkerResultStatus.SUCCEEDED, output={"summary": "done"}, artifacts=[{"artifact_id": "a1"}], evidence=[{"evidence_id": "e1"}], metrics={"duration_ms": 100}, execution={"run_id": "run-001"})
    r.validate()
    assert r.is_success is True
    assert r.is_failure is False
    assert r.status == WorkerResultStatus.SUCCEEDED


def test_worker_result_all_statuses():
    for status in [WorkerResultStatus.SUCCEEDED, WorkerResultStatus.FAILED, WorkerResultStatus.BLOCKED, WorkerResultStatus.CANCELLED, WorkerResultStatus.PARTIAL]:
        r = WorkerResult.create(status=status, output={"summary": "test"})
        assert r.status == status


def test_worker_result_partial_not_promoted():
    r = WorkerResult.create(status=WorkerResultStatus.PARTIAL, output={"summary": "partial"})
    assert r.status == WorkerResultStatus.PARTIAL
    assert r.is_success is False
    # PARTIAL must not be auto-promoted to SUCCEEDED
    assert r.status != WorkerResultStatus.SUCCEEDED


def test_worker_result_to_dict_from_dict():
    r = WorkerResult.create(status="SUCCEEDED", output={"summary": "ok"}, metrics={"duration_ms": 42}, execution={"run_id": "r1"})
    d = r.to_dict()
    r2 = WorkerResult.from_dict(d)
    assert r2.status == r.status
    assert r2.output["summary"] == "ok"
    assert r2.metrics["duration_ms"] == 42


def test_worker_result_invalid_status():
    with pytest.raises(WorkerError):
        WorkerResult.create(status="INVALID", output={})


# -- WorkerEvidence AC-013-07 --

def test_worker_evidence_create():
    ev = WorkerEvidence.create(task_id="task-001", run_id="run-001", producer="coder-worker", type="result", source="worker:coder-worker", content="test content")
    ev.validate()
    assert ev.task_id == "task-001"
    assert ev.is_admissible is True
    assert ev.content_hash == compute_hash("test content")


def test_worker_evidence_provenance_chain():
    ev = WorkerEvidence.create(task_id="t1", run_id="r1", producer="w1", type="result", source="worker:w1", content="content", artifact_id="art-001", requirement_id="req-001")
    chain = ev.provenance_chain()
    assert chain["evidence_id"] == ev.evidence_id
    assert chain["run_id"] == "r1"
    assert chain["task_id"] == "t1"
    assert chain["complete"] is True


def test_worker_evidence_unknown_not_promoted():
    ev = WorkerEvidence.create(task_id="t1", run_id="r1", producer="w1", type="result", source="worker:w1", content="content", status="UNKNOWN")
    assert ev.status == "UNKNOWN"
    assert ev.is_admissible is False
    # UNKNOWN must not be treated as PASS
    assert ev.status != "ADMISSIBLE"


def test_worker_evidence_to_dict_from_dict():
    ev = WorkerEvidence.create(task_id="t1", run_id="r1", producer="w1", type="result", source="worker:w1", content="hello")
    d = ev.to_dict()
    ev2 = WorkerEvidence.from_dict(d)
    assert ev2.evidence_id == ev.evidence_id
    assert ev2.content_hash == ev.content_hash


def test_worker_evidence_missing_field_reject():
    with pytest.raises(WorkerError):
        WorkerEvidence(task_id="", run_id="r1", producer="w1", type="result", source="s", content_hash="h", evidence_id="e1").validate()
    with pytest.raises(WorkerError):
        WorkerEvidence(task_id="t1", run_id="", producer="w1", type="result", source="s", content_hash="h", evidence_id="e1").validate()


def test_compute_hash_deterministic():
    assert compute_hash("hello") == compute_hash("hello")
    assert compute_hash("hello") != compute_hash("world")
