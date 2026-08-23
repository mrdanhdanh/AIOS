"""Tests for the execution contract (T135)."""

import pytest

from aios.execution import (
    ExecutionContract,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionStatus,
)
from aios.execution._common import ExecutionError


def test_request_requires_ids():
    with pytest.raises(ExecutionError):
        ExecutionRequest(request_id="", command="x")
    with pytest.raises(ExecutionError):
        ExecutionRequest(request_id="r", command="")


def test_response_requires_status():
    with pytest.raises(ExecutionError):
        ExecutionResponse(request_id="r", status="not-a-status")


def test_contract_requires_execution_id():
    with pytest.raises(ExecutionError):
        ExecutionContract(execution_id="")


def test_validate_request_rejects_missing_refs():
    c = ExecutionContract(execution_id="e1")
    req = ExecutionRequest(request_id="r", command="pytest")
    assert c.validate_request(req) is False


def test_validate_request_accepts_with_refs():
    c = ExecutionContract(execution_id="e1", sandbox_ref="sb1", policy_ref="pol1")
    req = ExecutionRequest(request_id="r", command="pytest", sandbox_ref="sb1", policy_ref="pol1")
    assert c.validate_request(req) is True


def test_validate_response_rejects_unattributed_blocked():
    c = ExecutionContract(execution_id="e1")
    resp = ExecutionResponse(request_id="r", status=ExecutionStatus.BLOCKED)
    assert c.validate_response(resp) is False


def test_content_hash_deterministic():
    c1 = ExecutionContract(execution_id="e1", sandbox_ref="sb1", policy_ref="pol1")
    c2 = ExecutionContract(execution_id="e1", sandbox_ref="sb1", policy_ref="pol1")
    assert c1.content_hash() == c2.content_hash()


def test_provenance_has_hash():
    c = ExecutionContract(execution_id="e1", sandbox_ref="sb1", policy_ref="pol1")
    prov = c.provenance()
    assert prov["execution_id"] == "e1"
    assert "content_hash" in prov and prov["content_hash"]
