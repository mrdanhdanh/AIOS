import os
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.governance.task_registry import TaskRegistry, RegistryError, parse_master_spec


def test_create_and_uniqueness():
    reg = TaskRegistry()
    reg.create_task("TASK-001", "Governance")
    # Rule 1: cannot reuse an existing ID
    try:
        reg.create_task("TASK-001", "Duplicate")
        assert False, "should reject duplicate ID"
    except RegistryError:
        pass


def test_invalid_id_rejected():
    reg = TaskRegistry()
    for bad in ["TASK", "001", "task-1", "TASK-ABC"]:
        try:
            reg.create_task(bad, "x")
            assert False, f"should reject {bad}"
        except RegistryError:
            pass


def test_never_deleted_only_deprecated():
    reg = TaskRegistry()
    reg.create_task("TASK-002", "Wrong")
    reg.deprecate("TASK-002")
    assert reg.get("TASK-002").status == "DEPRECATED"
    assert reg.has("TASK-002") is True  # still present, never deleted


def test_parse_master_spec_validates_uniqueness():
    reg = parse_master_spec()
    assert len(reg) == 218  # TASK-001 .. TASK-218
    assert reg.has("TASK-001") and reg.has("TASK-218")
    # milestone derived (Rule 2)
    assert reg.get("TASK-001").milestone == "M0"
    assert reg.get("TASK-218").milestone == "M26"
