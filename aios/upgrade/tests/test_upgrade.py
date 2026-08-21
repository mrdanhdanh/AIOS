"""Tests for upgrade pipeline components."""

from __future__ import annotations

import pytest

from aios.upgrade.backup import BackupEngine
from aios.upgrade.compatibility import CompatibilityChecker, CompatibilityResult
from aios.upgrade.dryrun import DryRunEngine
from aios.upgrade.manifest import UpgradeManifest, UpgradeStep, UpgradeStepType
from aios.upgrade.migration import MigrationEngine, MigrationStatus
from aios.upgrade.rollback import RollbackEngine, RollbackStatus
from aios.upgrade.validation import ValidationPipeline, ValidationStatus


class TestUpgradeManifest:
    def test_create_manifest(self) -> None:
        m = UpgradeManifest(
            upgrade_id="up-001",
            source_version="0.4.0",
            target_version="0.5.0",
        )
        assert m.upgrade_id == "up-001"
        assert m.step_count == 0

    def test_with_steps(self) -> None:
        steps = [
            UpgradeStep(step_id="s1", step_type=UpgradeStepType.SCHEMA),
            UpgradeStep(step_id="s2", step_type=UpgradeStepType.CONTRACT),
        ]
        m = UpgradeManifest(
            upgrade_id="up-002",
            source_version="0.4.0",
            target_version="0.5.0",
            steps=steps,
        )
        assert m.step_count == 2
        assert m.all_reversible is True

    def test_to_dict(self) -> None:
        m = UpgradeManifest(
            upgrade_id="up-003",
            source_version="1.0.0",
            target_version="1.1.0",
            steps=[UpgradeStep(step_id="s1", step_type=UpgradeStepType.DATA)],
        )
        d = m.to_dict()
        assert d["upgrade_id"] == "up-003"
        assert "content_hash" in d
        assert len(d["steps"]) == 1

    def test_from_dict_roundtrip(self) -> None:
        m = UpgradeManifest(
            upgrade_id="up-004",
            source_version="1.0.0",
            target_version="2.0.0",
            steps=[UpgradeStep(step_id="s1", step_type=UpgradeStepType.CONFIG, reversible=False)],
        )
        d = m.to_dict()
        m2 = UpgradeManifest.from_dict(d)
        assert m2.upgrade_id == "up-004"
        assert m2.all_reversible is False

    def test_compute_hash_deterministic(self) -> None:
        m = UpgradeManifest(
            upgrade_id="up-005",
            source_version="1.0.0",
            target_version="2.0.0",
        )
        h1 = m.compute_hash()
        h2 = m.compute_hash()
        assert h1 == h2


class TestCompatibilityChecker:
    def test_same_version(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_version("1.0.0", "1.0.0")
        assert result.result == CompatibilityResult.COMPATIBLE

    def test_patch_bump(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_version("1.0.0", "1.0.1")
        assert result.result == CompatibilityResult.COMPATIBLE

    def test_minor_bump(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_version("1.0.0", "1.1.0")
        assert result.result == CompatibilityResult.MIGRATION_REQUIRED

    def test_major_bump(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_version("1.0.0", "2.0.0")
        assert result.result == CompatibilityResult.MIGRATION_REQUIRED

    def test_invalid_version(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_version("abc", "def")
        assert result.result == CompatibilityResult.UNKNOWN

    def test_short_version(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_version("1", "2")
        assert result.result == CompatibilityResult.UNKNOWN

    def test_contracts_compatible(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_contracts(
            {"api": "v1", "core": "v1"},
            {"api": "v1", "core": "v1"},
        )
        assert result.result == CompatibilityResult.COMPATIBLE

    def test_contracts_breaking(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_contracts(
            {"api": "v1"},
            {"api": "v2"},
        )
        assert result.result == CompatibilityResult.MIGRATION_REQUIRED

    def test_contracts_new(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_contracts(
            {"api": "v1"},
            {"api": "v1", "new": "v1"},
        )
        assert result.result == CompatibilityResult.COMPATIBLE

    def test_contracts_removed(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_contracts(
            {"api": "v1", "old": "v1"},
            {"api": "v1"},
        )
        assert result.result == CompatibilityResult.MIGRATION_REQUIRED

    def test_deps_satisfied(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_dependencies(
            {"pyyaml": "6.0"},
            {"pyyaml": "6.0"},
        )
        assert result.result == CompatibilityResult.COMPATIBLE

    def test_deps_missing(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_dependencies(
            {"pyyaml": "6.0", "fastapi": "0.100"},
            {"pyyaml": "6.0"},
        )
        assert result.result == CompatibilityResult.INCOMPATIBLE

    def test_check_all_compatible(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_all("1.0.0", "1.0.1")
        assert result == CompatibilityResult.COMPATIBLE

    def test_check_all_incompatible(self) -> None:
        checker = CompatibilityChecker()
        result = checker.check_all(
            "1.0.0", "2.0.0",
            source_contracts={"api": "v1"},
            target_contracts={"api": "v1"},
            required_deps={"dep": "1.0"},
            available_deps={},
        )
        assert result == CompatibilityResult.INCOMPATIBLE


class TestBackupEngine:
    def test_create_backup(self) -> None:
        engine = BackupEngine()
        manifest = engine.create_backup("1.0.0", {"key": "value"})
        assert manifest.backup_id.startswith("backup-")
        assert manifest.version == "1.0.0"
        assert engine.backup_count == 1

    def test_restore_backup(self) -> None:
        engine = BackupEngine()
        state = {"a": 1, "b": 2}
        manifest = engine.create_backup("1.0.0", state)
        restored = engine.restore_backup(manifest.backup_id)
        assert restored == state

    def test_verify_backup(self) -> None:
        engine = BackupEngine()
        manifest = engine.create_backup("1.0.0", {"x": 1}, items=["x"])
        assert engine.verify_backup(manifest.backup_id) is True

    def test_verify_nonexistent(self) -> None:
        engine = BackupEngine()
        assert engine.verify_backup("nonexistent") is False

    def test_list_backups(self) -> None:
        engine = BackupEngine()
        engine.create_backup("1.0.0", {"a": 1})
        engine.create_backup("1.0.1", {"b": 2})
        assert len(engine.list_backups()) == 2

    def test_delete_backup(self) -> None:
        engine = BackupEngine()
        manifest = engine.create_backup("1.0.0", {"a": 1})
        assert engine.delete_backup(manifest.backup_id) is True
        assert engine.backup_count == 0

    def test_to_dict(self) -> None:
        engine = BackupEngine()
        manifest = engine.create_backup("1.0.0", {"a": 1})
        d = manifest.to_dict()
        assert "backup_id" in d
        assert "checksum" in d


class TestMigrationEngine:
    def test_migrate_success(self) -> None:
        engine = MigrationEngine()
        manifest = UpgradeManifest(
            upgrade_id="up-001",
            source_version="1.0.0",
            target_version="2.0.0",
            steps=[
                UpgradeStep(step_id="s1", step_type=UpgradeStepType.SCHEMA),
                UpgradeStep(step_id="s2", step_type=UpgradeStepType.CONTRACT),
            ],
        )
        result = engine.migrate(manifest)
        assert result.succeeded
        assert result.steps_completed == 2
        assert len(result.evidence) == 2

    def test_migrate_precondition_fail(self) -> None:
        engine = MigrationEngine()
        manifest = UpgradeManifest(
            upgrade_id="up-002",
            source_version="1.0.0",
            target_version="2.0.0",
            steps=[
                UpgradeStep(
                    step_id="s1",
                    step_type=UpgradeStepType.DATA,
                    preconditions=["existing_key"],
                ),
            ],
        )
        result = engine.migrate(manifest, current_state={})
        assert not result.succeeded
        assert result.status == MigrationStatus.FAILED

    def test_migrate_with_state(self) -> None:
        engine = MigrationEngine()
        manifest = UpgradeManifest(
            upgrade_id="up-003",
            source_version="1.0.0",
            target_version="2.0.0",
            steps=[
                UpgradeStep(
                    step_id="s1",
                    step_type=UpgradeStepType.DATA,
                    preconditions=["existing_key"],
                ),
            ],
        )
        result = engine.migrate(manifest, current_state={"existing_key": True})
        assert result.succeeded

    def test_history(self) -> None:
        engine = MigrationEngine()
        manifest = UpgradeManifest(
            upgrade_id="up-004",
            source_version="1.0.0",
            target_version="2.0.0",
            steps=[UpgradeStep(step_id="s1", step_type=UpgradeStepType.CONFIG)],
        )
        engine.migrate(manifest)
        assert len(engine.get_history()) == 1


class TestDryRunEngine:
    def test_simulate_ready(self) -> None:
        engine = DryRunEngine()
        manifest = UpgradeManifest(
            upgrade_id="up-001",
            source_version="1.0.0",
            target_version="2.0.0",
            steps=[UpgradeStep(step_id="s1", step_type=UpgradeStepType.SCHEMA)],
        )
        result = engine.simulate(manifest)
        assert result.ready
        assert len(result.steps) == 1
        assert result.steps[0].would_execute is True

    def test_simulate_not_ready(self) -> None:
        engine = DryRunEngine()
        manifest = UpgradeManifest(
            upgrade_id="up-002",
            source_version="1.0.0",
            target_version="2.0.0",
            steps=[
                UpgradeStep(
                    step_id="s1",
                    step_type=UpgradeStepType.DATA,
                    preconditions=["existing_key"],
                ),
            ],
        )
        result = engine.simulate(manifest, current_state={})
        assert not result.ready
        assert len(result.issues) > 0

    def test_no_side_effects(self) -> None:
        """AC-020-05: Dry-run creates no side effects."""
        engine = DryRunEngine()
        state = {"a": 1}
        original = dict(state)
        manifest = UpgradeManifest(
            upgrade_id="up-003",
            source_version="1.0.0",
            target_version="2.0.0",
            steps=[UpgradeStep(step_id="s1", step_type=UpgradeStepType.DATA)],
        )
        engine.simulate(manifest, current_state=state)
        assert state == original  # State unchanged

    def test_deterministic(self) -> None:
        """AC-020-06: Dry-run deterministic."""
        engine = DryRunEngine()
        manifest = UpgradeManifest(
            upgrade_id="up-004",
            source_version="1.0.0",
            target_version="2.0.0",
            steps=[
                UpgradeStep(step_id="s1", step_type=UpgradeStepType.SCHEMA),
                UpgradeStep(step_id="s2", step_type=UpgradeStepType.CONTRACT),
            ],
        )
        r1 = engine.simulate(manifest)
        r2 = engine.simulate(manifest)
        assert r1.to_dict()["steps"] == r2.to_dict()["steps"]
        assert r1.ready == r2.ready


class TestValidationPipeline:
    def test_all_pass(self) -> None:
        pipeline = ValidationPipeline()
        pipeline.register("check_a", lambda s: __import__("aios.upgrade.validation", fromlist=["ValidationCheck"]).ValidationCheck(name="a", status=ValidationStatus.PASS))
        result = pipeline.validate({"x": 1})
        assert result.passed

    def test_one_fail(self) -> None:
        from aios.upgrade.validation import ValidationCheck
        pipeline = ValidationPipeline()
        pipeline.register("check_a", lambda s: ValidationCheck(name="a", status=ValidationStatus.PASS))
        pipeline.register("check_b", lambda s: ValidationCheck(name="b", status=ValidationStatus.FAIL, detail="broken"))
        result = pipeline.validate({"x": 1})
        assert not result.passed
        assert result.failed_count == 1

    def test_validate_with_manifest_checks(self) -> None:
        from aios.upgrade.validation import ValidationCheck
        pipeline = ValidationPipeline()
        pipeline.register("schema_check", lambda s: ValidationCheck(name="schema_check", status=ValidationStatus.PASS))
        result = pipeline.validate_with_manifest_checks({}, ["schema_check", "unknown_check"])
        assert result.passed
        assert len(result.checks) == 2
        assert result.checks[1].status == ValidationStatus.SKIP

    def test_exception_in_check(self) -> None:
        def bad_check(s): raise RuntimeError("boom")
        pipeline = ValidationPipeline()
        pipeline.register("bad", bad_check)
        result = pipeline.validate({})
        assert not result.passed


class TestRollbackEngine:
    def test_rollback_success(self) -> None:
        backup_engine = BackupEngine()
        state = {"a": 1, "b": 2}
        manifest = backup_engine.create_backup("1.0.0", state)
        rollback_engine = RollbackEngine(backup_engine)
        target: dict = {"a": 99}
        result = rollback_engine.rollback(manifest.backup_id, target)
        assert result.status == RollbackStatus.SUCCESS
        assert target == state
        assert len(result.evidence) == 1

    def test_rollback_nonexistent(self) -> None:
        backup_engine = BackupEngine()
        rollback_engine = RollbackEngine(backup_engine)
        result = rollback_engine.rollback("nonexistent")
        assert result.status == RollbackStatus.FAILED

    def test_auto_rollback_on_failure(self) -> None:
        backup_engine = BackupEngine()
        state = {"a": 1}
        manifest = backup_engine.create_backup("1.0.0", state)
        rollback_engine = RollbackEngine(backup_engine)
        target: dict = {}
        result = rollback_engine.auto_rollback(manifest.backup_id, migration_failed=True, target_state=target)
        assert result.status == RollbackStatus.SUCCESS
        assert target == state

    def test_auto_rollback_not_needed(self) -> None:
        backup_engine = BackupEngine()
        manifest = backup_engine.create_backup("1.0.0", {"a": 1})
        rollback_engine = RollbackEngine(backup_engine)
        result = rollback_engine.auto_rollback(manifest.backup_id, migration_failed=False)
        assert result.status == RollbackStatus.NOT_NEEDED

    def test_to_dict(self) -> None:
        backup_engine = BackupEngine()
        manifest = backup_engine.create_backup("1.0.0", {"a": 1})
        rollback_engine = RollbackEngine(backup_engine)
        result = rollback_engine.rollback(manifest.backup_id)
        d = result.to_dict()
        assert "status" in d
        assert "evidence" in d
