"""Automated tests for the execution state checkpoint service (TASK-005)."""

import pytest

from aios.runtime.state import (
    ExecutionState,
    RunStatus,
    StateError,
    StateStore,
)


def test_save_load_roundtrip():
    store = StateStore()
    st = ExecutionState(execution_id="e1", status=RunStatus.RUNNING)
    st.set_step("s0", "COMPLETED")
    st.cursor = 1
    store.save(st)
    loaded = store.load("e1")
    assert loaded is not None
    assert loaded.step_status == {"s0": "COMPLETED"}
    assert loaded.cursor == 1


def test_load_missing_returns_none():
    store = StateStore()
    assert store.load("nope") is None


def test_serialization_roundtrip():
    st = ExecutionState(execution_id="e2", status=RunStatus.FAILED)
    st.set_step("s0", "FAILED")
    data = st.to_dict()
    restored = ExecutionState.from_dict(data)
    assert restored.execution_id == "e2"
    assert restored.status == RunStatus.FAILED
    assert restored.step_status == {"s0": "FAILED"}


def test_snapshot_is_independent():
    st = ExecutionState(execution_id="e3")
    snap = st.snapshot()
    snap.set_step("s0", "COMPLETED")
    assert "s0" not in st.step_status


def test_store_rejects_non_state():
    store = StateStore()
    with pytest.raises(StateError):
        store.save("nope")


def test_delete_and_list():
    store = StateStore()
    store.save(ExecutionState(execution_id="e1"))
    store.save(ExecutionState(execution_id="e2"))
    assert set(store.list_ids()) == {"e1", "e2"}
    store.delete("e1")
    assert store.list_ids() == ["e2"]


def test_resume_cursor_semantics():
    store = StateStore()
    st = ExecutionState(execution_id="e1", status=RunStatus.RUNNING)
    st.set_step("s0", "COMPLETED")
    st.cursor = 1
    store.save(st)
    loaded = store.load("e1")
    assert loaded.cursor == 1
    assert loaded.step_status["s0"] == "COMPLETED"
