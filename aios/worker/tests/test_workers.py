"""Tests for concrete workers — AC-013-01/06/07/09 (TASK-013)."""

import pytest

from aios.capability.capability import CapabilityContract, CapabilityRegistry
from aios.worker.contract import WorkerContext, WorkerRequest, WorkerResultStatus, WorkerType
from aios.worker.workers import (
    CoderWorker,
    DoctorWorker,
    GeneralWorker,
    SystemDoctorWorker,
    DEFAULT_CODER_CONTRACT,
    DEFAULT_DOCTOR_CONTRACT,
    DEFAULT_GENERAL_CONTRACT,
    DEFAULT_SYSTEM_DOCTOR_CONTRACT,
)


def _make_cap_registry(caps) -> CapabilityRegistry:
    reg = CapabilityRegistry()
    for cap in caps:
        try:
            reg.register(CapabilityContract.create(cap, description=f"cap {cap}"))
        except Exception:
            pass
    return reg


class TestGeneralWorker:
    def test_contract(self):
        w = GeneralWorker()
        assert w.worker_type == "general"
        assert w.contract.worker_type == WorkerType.GENERAL
        assert "research" in w.capabilities
        assert "summarize" in w.capabilities

    def test_default_contract_valid(self):
        DEFAULT_GENERAL_CONTRACT.validate()
        assert DEFAULT_GENERAL_CONTRACT.worker_id == "general-worker"

    def test_execute_research(self):
        caps = ["research", "summarize", "transform", "inspect", "coordinate"]
        w = GeneralWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(task_id="task-001", objective={"description": "research AI trends"}, allowed_capabilities=caps)
        result = w.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert "research" in result.output.get("capability", "") or "research" in str(result.output).lower()
        assert len(result.evidence) == 1
        assert len(result.artifacts) == 1

    def test_execute_summarize(self):
        caps = ["research", "summarize", "transform", "inspect", "coordinate"]
        w = GeneralWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(task_id="task-001", objective={"description": "summarize document"}, allowed_capabilities=caps)
        result = w.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert result.output["capability"] == "summarize"

    def test_execute_with_limited_scope(self):
        caps = ["research", "summarize", "transform", "inspect", "coordinate"]
        w = GeneralWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(task_id="task-001", objective={"description": "do work"}, allowed_capabilities=["inspect"])
        result = w.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert result.output["capability"] == "inspect"

    def test_result_has_evidence(self):
        caps = ["research", "summarize", "transform", "inspect", "coordinate"]
        w = GeneralWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(task_id="task-001", objective={"description": "inspect code"}, allowed_capabilities=["inspect"])
        result = w.execute(req)
        assert len(result.evidence) == 1
        ev = result.evidence[0]
        assert ev["task_id"] == "task-001"
        assert "content_hash" in ev


class TestCoderWorker:
    def test_contract(self):
        w = CoderWorker()
        assert w.worker_type == "coder"
        assert w.contract.worker_type == WorkerType.CODER
        assert "code.read" in w.capabilities
        assert "code.write" in w.capabilities
        assert "test.run" in w.capabilities

    def test_default_contract_valid(self):
        DEFAULT_CODER_CONTRACT.validate()
        assert DEFAULT_CODER_CONTRACT.worker_id == "coder-worker"

    def test_execute_fix_task(self):
        caps = ["code.read", "code.write", "test.run", "code.analyze", "code.refactor"]
        w = CoderWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(task_id="task-001", objective={"description": "Fix failing test_login()"}, allowed_capabilities=caps)
        result = w.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert "steps" in result.output
        assert len(result.output["steps"]) >= 1
        assert len(result.evidence) == 1

    def test_execute_no_subprocess(self):
        # Verify coder worker doesn't use subprocess/open/requests directly
        import ast
        import pathlib
        workers_path = pathlib.Path(__file__).resolve().parents[1] / "workers.py"
        text = workers_path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in ("subprocess", "requests", "docker"), f"workers.py imports {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "subprocess" not in node.module
                    assert "docker" not in node.module
            elif isinstance(node, ast.Call):
                # Check for open() / subprocess.run() calls
                if isinstance(node.func, ast.Name):
                    assert node.func.id not in ("open",), f"workers.py calls {node.func.id}() directly"
                elif isinstance(node.func, ast.Attribute):
                    assert node.func.attr not in ("run", "Popen", "call"), f"workers.py calls {node.func.attr}()"

    def test_execute_with_limited_scope(self):
        caps = ["code.read", "code.write", "test.run", "code.analyze", "code.refactor"]
        w = CoderWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(task_id="task-001", objective={"description": "analyze code"}, allowed_capabilities=["code.analyze"])
        result = w.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED

    def test_coder_result_has_evidence(self):
        caps = ["code.read", "code.write", "test.run", "code.analyze", "code.refactor"]
        w = CoderWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(task_id="task-001", objective={"description": "refactor module"}, allowed_capabilities=caps)
        result = w.execute(req)
        assert len(result.evidence) == 1
        assert result.evidence[0]["task_id"] == "task-001"


class TestDoctorWorker:
    def test_contract(self):
        w = DoctorWorker()
        assert w.worker_type == "doctor"
        assert w.contract.worker_type == WorkerType.DOCTOR
        assert "diagnose.task" in w.capabilities

    def test_default_contract_valid(self):
        DEFAULT_DOCTOR_CONTRACT.validate()
        assert DEFAULT_DOCTOR_CONTRACT.worker_id == "doctor-worker"

    def test_diagnose_test_failure(self):
        caps = ["diagnose.task", "inspect.logs", "inspect.artifacts", "analyze.failure"]
        w = DoctorWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(
            task_id="task-001",
            objective={"failure": {"error": "test_login failed: assertion error", "run_id": "run-001"}},
            allowed_capabilities=caps,
        )
        result = w.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert result.output["diagnosis"]["category"] == "TEST_FAILURE"
        assert "recommendation" in result.output["diagnosis"]
        assert "Doctor only diagnoses" in result.output["diagnosis"]["note"]

    def test_diagnose_dependency_error(self):
        caps = ["diagnose.task", "inspect.logs", "inspect.artifacts", "analyze.failure"]
        w = DoctorWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(
            task_id="task-001",
            objective={"failure": {"error": "ModuleNotFoundError: No module named 'yaml'"}},
            allowed_capabilities=caps,
        )
        result = w.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert result.output["diagnosis"]["category"] == "DEPENDENCY_ERROR"

    def test_diagnose_does_not_remediate(self):
        caps = ["diagnose.task", "inspect.logs", "inspect.artifacts", "analyze.failure"]
        w = DoctorWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(
            task_id="task-001",
            objective={"failure": {"error": "timeout waiting for response"}},
            allowed_capabilities=caps,
        )
        result = w.execute(req)
        # Doctor only diagnoses, doesn't remediate
        assert "recommendation" in result.output["diagnosis"]
        assert "note" in result.output["diagnosis"]
        # Result is SUCCEEDED (diagnosis succeeded), not remediation
        assert result.status == WorkerResultStatus.SUCCEEDED

    def test_doctor_result_has_evidence(self):
        caps = ["diagnose.task", "inspect.logs", "inspect.artifacts", "analyze.failure"]
        w = DoctorWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(task_id="task-001", objective={"failure": {"error": "unknown error"}}, allowed_capabilities=caps)
        result = w.execute(req)
        assert len(result.evidence) == 1
        assert result.evidence[0]["type"] == "diagnosis"


class TestSystemDoctorWorker:
    def test_contract(self):
        w = SystemDoctorWorker()
        assert w.worker_type == "system_doctor"
        assert w.contract.worker_type == WorkerType.SYSTEM_DOCTOR
        assert "diagnose.runtime" in w.capabilities

    def test_default_contract_valid(self):
        DEFAULT_SYSTEM_DOCTOR_CONTRACT.validate()
        assert DEFAULT_SYSTEM_DOCTOR_CONTRACT.worker_id == "system-doctor-worker"

    def test_diagnose_runtime_unhealthy(self):
        caps = ["diagnose.runtime", "health.check", "inspect.config", "analyze.architecture"]
        w = SystemDoctorWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(
            task_id="task-001",
            objective={"description": "runtime unhealthy: capability_router down"},
            allowed_capabilities=caps,
        )
        result = w.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert result.output["diagnosis"]["status"] == "DEGRADED"
        assert result.output["diagnosis"]["severity"] == "HIGH"
        assert len(result.output["diagnosis"]["findings"]) > 0

    def test_diagnose_architecture_violation(self):
        caps = ["diagnose.runtime", "health.check", "inspect.config", "analyze.architecture"]
        w = SystemDoctorWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(
            task_id="task-001",
            objective={"description": "architecture violation detected"},
            allowed_capabilities=caps,
        )
        result = w.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert result.output["diagnosis"]["status"] == "DEGRADED"

    def test_diagnose_healthy(self):
        caps = ["diagnose.runtime", "health.check", "inspect.config", "analyze.architecture"]
        w = SystemDoctorWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(
            task_id="task-001",
            objective={"description": "check system health"},
            allowed_capabilities=caps,
        )
        result = w.execute(req)
        assert result.status == WorkerResultStatus.SUCCEEDED
        assert result.output["diagnosis"]["status"] == "HEALTHY"

    def test_system_doctor_only_proposes(self):
        caps = ["diagnose.runtime", "health.check", "inspect.config", "analyze.architecture"]
        w = SystemDoctorWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(
            task_id="task-001",
            objective={"description": "runtime unhealthy"},
            allowed_capabilities=caps,
        )
        result = w.execute(req)
        assert "note" in result.output["diagnosis"]
        assert "proposes" in result.output["diagnosis"]["note"] or "propose" in result.output["diagnosis"]["note"].lower() or "Runtime" in result.output["diagnosis"]["note"]

    def test_system_doctor_result_has_evidence(self):
        caps = ["diagnose.runtime", "health.check", "inspect.config", "analyze.architecture"]
        w = SystemDoctorWorker(capability_registry=_make_cap_registry(caps))
        req = WorkerRequest.create(task_id="task-001", objective={"description": "health check"}, allowed_capabilities=caps)
        result = w.execute(req)
        assert len(result.evidence) == 1
        assert result.evidence[0]["type"] == "diagnosis"


class TestAllWorkersShareContract:
    def test_all_workers_have_ten_fields(self):
        for WorkerClass in [GeneralWorker, CoderWorker, DoctorWorker, SystemDoctorWorker]:
            w = WorkerClass()
            d = w.contract.to_dict()
            for field in ["worker_id", "worker_type", "version", "capabilities", "input_schema", "output_schema", "lifecycle", "execution_context", "policy_context", "evidence_contract"]:
                assert field in d, f"{WorkerClass.__name__} missing field {field}"

    def test_all_workers_validate(self):
        for WorkerClass in [GeneralWorker, CoderWorker, DoctorWorker, SystemDoctorWorker]:
            w = WorkerClass()
            w.contract.validate()

    def test_all_workers_distinct_types(self):
        types = set()
        for WorkerClass in [GeneralWorker, CoderWorker, DoctorWorker, SystemDoctorWorker]:
            w = WorkerClass()
            types.add(w.worker_type)
        assert len(types) == 4
        assert types == {"general", "coder", "doctor", "system_doctor"}
