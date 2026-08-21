"""Tests for harness doctor and readiness."""

from __future__ import annotations

from aios.harness.doctor import DoctorCheck, DoctorVerdict, HarnessDoctor, ReadinessChecker


class TestHarnessDoctor:
    def test_diagnose_all_pass(self) -> None:
        doctor = HarnessDoctor()
        doctor.register("check1", lambda: DoctorCheck("check1", DoctorVerdict.PASS))
        report = doctor.diagnose()
        assert report.overall == DoctorVerdict.PASS

    def test_diagnose_with_error(self) -> None:
        doctor = HarnessDoctor()
        doctor.register("ok", lambda: DoctorCheck("ok", DoctorVerdict.PASS))
        doctor.register("bad", lambda: DoctorCheck("bad", DoctorVerdict.ERROR))
        report = doctor.diagnose()
        assert report.overall == DoctorVerdict.ERROR

    def test_diagnose_exception(self) -> None:
        doctor = HarnessDoctor()
        def bad_check() -> DoctorCheck:
            raise RuntimeError("boom")
        doctor.register("bad", bad_check)
        report = doctor.diagnose()
        assert report.overall == DoctorVerdict.ERROR

    def test_verdict_is_healthy(self) -> None:
        assert DoctorVerdict.PASS.is_healthy is True
        assert DoctorVerdict.WARNING.is_healthy is False
        assert DoctorVerdict.UNKNOWN.is_healthy is False


class TestReadinessChecker:
    def test_all_pass(self) -> None:
        rc = ReadinessChecker()
        rc.add_check(lambda: True)
        assert rc.is_ready() is True

    def test_one_fail(self) -> None:
        """AC-034-02: Fail-closed."""
        rc = ReadinessChecker()
        rc.add_check(lambda: True)
        rc.add_check(lambda: False)
        assert rc.is_ready() is False

    def test_no_checks_fail_closed(self) -> None:
        rc = ReadinessChecker()
        assert rc.is_ready() is False
