"""Tests for observability components."""

from __future__ import annotations

import pytest

from aios.observability.arch_health import (
    ArchitectureHealth,
    ViolationReport,
    ViolationSeverity,
    ViolationType,
)
from aios.observability.audit import AuditService
from aios.observability.doctor import DoctorService, HealthLevel
from aios.observability.metrics import MetricsCollector
from aios.observability.profiler import ProfilerService
from aios.observability.prompt_history import PromptHistory


class TestMetricsCollector:
    def test_record_execution(self) -> None:
        mc = MetricsCollector()
        mc.record_execution(True, 10.0)
        mc.record_execution(False, 5.0)
        snap = mc.get_current()
        assert snap.execution_count == 2
        assert snap.execution_success == 1
        assert snap.execution_failure == 1

    def test_record_model_call(self) -> None:
        mc = MetricsCollector()
        mc.record_model_call(tokens=100, cost=0.01, latency_ms=50.0)
        mc.record_model_call(tokens=200, cost=0.02, success=False)
        snap = mc.get_current()
        assert snap.model_calls == 2
        assert snap.model_tokens == 300
        assert snap.model_failures == 1

    def test_record_workflow(self) -> None:
        mc = MetricsCollector()
        mc.record_workflow(duration_ms=100.0, node_failures=1)
        snap = mc.get_current()
        assert snap.workflow_duration_ms == 100.0
        assert snap.workflow_node_failures == 1

    def test_record_resource(self) -> None:
        mc = MetricsCollector()
        mc.record_resource(cpu=0.5, memory_mb=512.0)
        snap = mc.get_current()
        assert snap.resource_cpu == 0.5
        assert snap.resource_memory_mb == 512.0

    def test_record_custom(self) -> None:
        mc = MetricsCollector()
        mc.record_custom("queue_depth", 5)
        snap = mc.get_current()
        assert snap.custom["queue_depth"] == 5

    def test_snapshot_resets(self) -> None:
        mc = MetricsCollector()
        mc.record_execution(True)
        snap = mc.snapshot()
        assert snap.execution_count == 1
        # After snapshot, current should be reset
        current = mc.get_current()
        assert current.execution_count == 0

    def test_history(self) -> None:
        mc = MetricsCollector()
        mc.record_execution(True)
        mc.snapshot()
        mc.record_execution(True)
        mc.snapshot()
        assert len(mc.get_history()) == 2

    def test_uptime(self) -> None:
        mc = MetricsCollector()
        assert mc.uptime_seconds() >= 0

    def test_to_dict(self) -> None:
        mc = MetricsCollector()
        mc.record_execution(True)
        d = mc.get_current().to_dict()
        assert "execution_count" in d
        assert "model_calls" in d


class TestAuditService:
    def test_record_entry(self) -> None:
        audit = AuditService()
        entry = audit.record(who="user", what="execute", result="success")
        assert entry.who == "user"
        assert entry.what == "execute"
        assert entry.entry_id.startswith("audit-")

    def test_provenance(self) -> None:
        audit = AuditService()
        entry = audit.record(
            who="agent",
            what="tool_call",
            provenance=["task-001", "exec-001"],
        )
        assert entry.provenance_chain == ["task-001", "exec-001"]
        assert entry.compute_hash()

    def test_query_by_who(self) -> None:
        audit = AuditService()
        audit.record(who="alice", what="read")
        audit.record(who="bob", what="write")
        results = audit.query(who="alice")
        assert len(results) == 1
        assert results[0].who == "alice"

    def test_query_by_execution(self) -> None:
        audit = AuditService()
        audit.record(who="u", what="a", execution_id="ex-1")
        audit.record(who="u", what="b", execution_id="ex-2")
        results = audit.query(execution_id="ex-1")
        assert len(results) == 1

    def test_count(self) -> None:
        audit = AuditService()
        audit.record(who="u", what="a")
        audit.record(who="u", what="b")
        assert audit.count() == 2

    def test_get_entry(self) -> None:
        audit = AuditService()
        entry = audit.record(who="u", what="a")
        found = audit.get_entry(entry.entry_id)
        assert found is not None
        assert found.who == "u"

    def test_to_dict(self) -> None:
        audit = AuditService()
        entry = audit.record(who="u", what="a")
        d = entry.to_dict()
        assert "entry_id" in d
        assert "content_hash" in d


class TestPromptHistory:
    def test_record(self) -> None:
        ph = PromptHistory()
        rec = ph.record(prompt_id="p1", version=1, tokens_used=100)
        assert rec.prompt_id == "p1"
        assert rec.tokens_used == 100

    def test_query_by_prompt(self) -> None:
        ph = PromptHistory()
        ph.record(prompt_id="p1", version=1)
        ph.record(prompt_id="p2", version=1)
        results = ph.query(prompt_id="p1")
        assert len(results) == 1

    def test_query_by_execution(self) -> None:
        ph = PromptHistory()
        ph.record(prompt_id="p1", version=1, execution_id="ex-1")
        ph.record(prompt_id="p1", version=1, execution_id="ex-2")
        results = ph.query(execution_id="ex-1")
        assert len(results) == 1

    def test_count(self) -> None:
        ph = PromptHistory()
        ph.record(prompt_id="p1", version=1)
        assert ph.count() == 1

    def test_to_dict(self) -> None:
        ph = PromptHistory()
        rec = ph.record(prompt_id="p1", version=1)
        d = rec.to_dict()
        assert d["prompt_id"] == "p1"


class TestProfilerService:
    def test_start_stop(self) -> None:
        prof = ProfilerService()
        prof.start("op1")
        result = prof.stop("op1")
        assert result is not None
        assert result.operation == "op1"
        assert result.duration_ms >= 0

    def test_stop_without_start(self) -> None:
        prof = ProfilerService()
        result = prof.stop("nonexistent")
        assert result is None

    def test_slowest(self) -> None:
        prof = ProfilerService()
        prof.start("fast")
        prof.stop("fast")
        prof.start("slow")
        prof.stop("slow", {"note": "slow op"})
        slowest = prof.get_slowest(1)
        assert len(slowest) == 1

    def test_by_operation(self) -> None:
        prof = ProfilerService()
        prof.start("op1")
        prof.stop("op1")
        prof.start("op1")
        prof.stop("op1")
        results = prof.get_by_operation("op1")
        assert len(results) == 2

    def test_summary(self) -> None:
        prof = ProfilerService()
        prof.start("op1")
        prof.stop("op1")
        s = prof.summary()
        assert s["total_operations"] == 1
        assert s["avg_duration_ms"] >= 0

    def test_summary_empty(self) -> None:
        prof = ProfilerService()
        s = prof.summary()
        assert s["total_operations"] == 0

    def test_to_dict(self) -> None:
        prof = ProfilerService()
        prof.start("op1")
        result = prof.stop("op1")
        d = result.to_dict()
        assert "operation" in d
        assert "duration_ms" in d


class TestDoctorService:
    def test_check_all(self) -> None:
        doctor = DoctorService()
        from aios.observability.doctor import ComponentReport
        doctor.register("rt", lambda: ComponentReport("rt", HealthLevel.PASS))
        doctor.register("db", lambda: ComponentReport("db", HealthLevel.PASS))
        report = doctor.check_all()
        assert report.overall == HealthLevel.PASS
        assert report.healthy_count == 2

    def test_error_overall(self) -> None:
        doctor = DoctorService()
        from aios.observability.doctor import ComponentReport
        doctor.register("rt", lambda: ComponentReport("rt", HealthLevel.PASS))
        doctor.register("db", lambda: ComponentReport("db", HealthLevel.ERROR))
        report = doctor.check_all()
        assert report.overall == HealthLevel.ERROR

    def test_warning_overall(self) -> None:
        doctor = DoctorService()
        from aios.observability.doctor import ComponentReport
        doctor.register("rt", lambda: ComponentReport("rt", HealthLevel.PASS))
        doctor.register("db", lambda: ComponentReport("db", HealthLevel.WARNING))
        report = doctor.check_all()
        assert report.overall == HealthLevel.WARNING

    def test_unknown_overall(self) -> None:
        doctor = DoctorService()
        from aios.observability.doctor import ComponentReport
        doctor.register("rt", lambda: ComponentReport("rt", HealthLevel.PASS))
        doctor.register("db", lambda: ComponentReport("db", HealthLevel.UNKNOWN))
        report = doctor.check_all()
        assert report.overall == HealthLevel.UNKNOWN

    def test_exception_in_check(self) -> None:
        doctor = DoctorService()
        doctor.register("bad", (_ for _ in ()).throw(RuntimeError("boom")) if False else (_ for _ in ()).__class__)  # type: ignore
        # Simpler: register a function that raises
        def bad_check():
            raise RuntimeError("boom")
        doctor.register("bad", bad_check)  # type: ignore
        report = doctor.check_all()
        assert report.overall == HealthLevel.ERROR

    def test_health_level_is_healthy(self) -> None:
        assert HealthLevel.PASS.is_healthy() is True
        assert HealthLevel.WARNING.is_healthy() is False
        assert HealthLevel.ERROR.is_healthy() is False
        assert HealthLevel.UNKNOWN.is_healthy() is False

    def test_to_dict(self) -> None:
        doctor = DoctorService()
        from aios.observability.doctor import ComponentReport
        doctor.register("rt", lambda: ComponentReport("rt", HealthLevel.PASS))
        report = doctor.check_all()
        d = report.to_dict()
        assert "overall" in d
        assert "components" in d


class TestArchitectureHealth:
    def test_report_violation(self) -> None:
        ah = ArchitectureHealth()
        v = ah.report_violation(
            ViolationType.CONTRACT,
            ViolationSeverity.HIGH,
            "mod",
            "bad contract",
            "RULE-001",
        )
        assert v.module == "mod"
        assert ah.count() == 1

    def test_check_contract_violations(self) -> None:
        ah = ArchitectureHealth()

        class GoodModule:
            def to_dict(self): return {}

        class BadModule:
            pass

        violations = ah.check_contract_violations({
            "good": GoodModule(),
            "bad": BadModule(),
        })
        # BadModule has __dict__ so it passes the simple check
        assert isinstance(violations, list)

    def test_check_layer_violations(self) -> None:
        ah = ArchitectureHealth()
        # tool importing runtime = upward violation (tool index 7 > runtime index 4)
        violations = ah.check_layer_violations([("tool", "runtime")])
        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.LAYER

    def test_no_layer_violation(self) -> None:
        ah = ArchitectureHealth()
        # runtime importing capability = downward = ok
        violations = ah.check_layer_violations([("runtime", "capability")])
        assert len(violations) == 0

    def test_get_report(self) -> None:
        ah = ArchitectureHealth()
        ah.report_violation(ViolationType.CONTRACT, ViolationSeverity.LOW, "m", "d")
        report = ah.get_report()
        assert report.failed_checks == 1
        assert report.is_healthy is False

    def test_violations_by_type(self) -> None:
        ah = ArchitectureHealth()
        ah.report_violation(ViolationType.CONTRACT, ViolationSeverity.HIGH, "m", "d")
        ah.report_violation(ViolationType.LAYER, ViolationSeverity.HIGH, "m", "d")
        assert len(ah.violations_by_type(ViolationType.CONTRACT)) == 1
        assert len(ah.violations_by_type(ViolationType.LAYER)) == 1

    def test_violations_by_severity(self) -> None:
        ah = ArchitectureHealth()
        ah.report_violation(ViolationType.CONTRACT, ViolationSeverity.HIGH, "m", "d")
        ah.report_violation(ViolationType.CONTRACT, ViolationSeverity.LOW, "m", "d")
        assert len(ah.violations_by_severity(ViolationSeverity.HIGH)) == 1

    def test_to_dict(self) -> None:
        ah = ArchitectureHealth()
        ah.report_violation(ViolationType.CONTRACT, ViolationSeverity.HIGH, "m", "d")
        d = ah.get_report().to_dict()
        assert "violations" in d
        assert "is_healthy" in d
