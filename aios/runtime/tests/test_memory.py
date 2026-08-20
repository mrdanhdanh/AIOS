"""Automated tests for the memory substrate (TASK-007)."""

import hashlib
import threading

import pytest

from aios.runtime.memory import MemoryEntry, MemoryError, MemoryStore, MemoryType


# -- MemoryType --

def test_memory_type_all_four():
    assert set(MemoryType.all()) == {
        MemoryType.CONVERSATION, MemoryType.SESSION, MemoryType.KNOWLEDGE, MemoryType.ARTIFACT
    }


def test_memory_type_values():
    assert MemoryType.CONVERSATION.value == "conversation"
    assert MemoryType.SESSION.value == "session"


# -- MemoryEntry --

def test_entry_create_computes_hash():
    e = MemoryEntry.create(MemoryType.CONVERSATION, "scope-1", "hello world")
    assert e.content_hash == hashlib.sha256(b"hello world").hexdigest()
    assert e.verify()


def test_entry_create_from_bytes():
    e = MemoryEntry.create(MemoryType.SESSION, "s1", b"bytes content")
    assert e.content == "bytes content"
    assert e.verify()


def test_entry_create_with_provenance():
    e = MemoryEntry.create(
        MemoryType.KNOWLEDGE, "scope-x", "data",
        producer="agent-1", source="doc.pdf", task_id="TASK-007", run_id="run-1",
        metadata={"k": "v"},
    )
    assert e.producer == "agent-1"
    assert e.source == "doc.pdf"
    assert e.task_id == "TASK-007"
    assert e.metadata["k"] == "v"


def test_entry_verify_fails_when_tampered():
    e = MemoryEntry.create(MemoryType.ARTIFACT, "sc", "original")
    e.content = "tampered"
    assert not e.verify()


def test_entry_scope_required():
    with pytest.raises(MemoryError):
        MemoryEntry.create(MemoryType.CONVERSATION, "", "data")
    with pytest.raises(MemoryError):
        MemoryEntry.create(MemoryType.CONVERSATION, "  ", "data")


def test_entry_unknown_type_rejected():
    with pytest.raises(MemoryError):
        MemoryEntry.create("unknown_type", "sc", "data")


def test_entry_non_str_bytes_rejected():
    with pytest.raises(MemoryError):
        MemoryEntry.create(MemoryType.CONVERSATION, "sc", 12345)


def test_entry_str_type_coercion():
    e = MemoryEntry.create("conversation", "sc", "hi")
    assert e.memory_type == MemoryType.CONVERSATION


# -- MemoryStore lifecycle --

def test_store_put_and_get():
    store = MemoryStore()
    e = MemoryEntry.create(MemoryType.CONVERSATION, "scope-1", "hello")
    store.put(e)
    assert store.get(e.entry_id).content == "hello"
    assert len(store) == 1


def test_store_rejects_bad_hash():
    store = MemoryStore()
    e = MemoryEntry.create(MemoryType.CONVERSATION, "sc", "ok")
    e.content = "tampered"
    with pytest.raises(MemoryError):
        store.put(e)


def test_store_rejects_duplicate_id():
    store = MemoryStore()
    e1 = MemoryEntry.create(MemoryType.SESSION, "sc", "a", entry_id="dup")
    e2 = MemoryEntry.create(MemoryType.SESSION, "sc", "b", entry_id="dup")
    store.put(e1)
    with pytest.raises(MemoryError):
        store.put(e2)


def test_store_rejects_non_entry():
    store = MemoryStore()
    with pytest.raises(MemoryError):
        store.put("not-an-entry")  # type: ignore[arg-type]


def test_store_list_by_type():
    store = MemoryStore()
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "sc", "c1"))
    store.put(MemoryEntry.create(MemoryType.SESSION, "sc", "s1"))
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "sc", "c2"))
    assert len(store.list_by_type(MemoryType.CONVERSATION)) == 2
    assert len(store.list_by_type(MemoryType.SESSION)) == 1
    assert len(store.list_by_type("conversation")) == 2


def test_store_list_by_scope():
    store = MemoryStore()
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "scope-A", "a"))
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "scope-B", "b"))
    assert len(store.list_by_scope("scope-A")) == 1
    assert store.list_by_scope("scope-A")[0].content == "a"


def test_store_isolation_scope_a_not_in_scope_b():
    store = MemoryStore()
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "scope-A", "secret A"))
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "scope-B", "secret B"))
    a_entries = store.list_by_scope("scope-A")
    assert all(e.scope_id == "scope-A" for e in a_entries)
    b_entries = store.list_by_scope("scope-B")
    assert all(e.scope_id == "scope-B" for e in b_entries)
    assert not any(e.content == "secret A" for e in b_entries)
    assert not any(e.content == "secret B" for e in a_entries)


def test_store_search_isolation():
    store = MemoryStore()
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "scope-A", "hello from A"))
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "scope-B", "hello from B"))
    hits_a = store.search("hello", scope_id="scope-A")
    assert len(hits_a) == 1
    assert hits_a[0].scope_id == "scope-A"
    hits_all = store.search("hello")
    assert len(hits_all) == 2


def test_store_search_case_insensitive_and_ranking():
    store = MemoryStore()
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "sc", "hello hello hello", entry_id="aaa"))
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "sc", "hello", entry_id="bbb"))
    hits = store.search("hello")
    assert hits[0].entry_id == "aaa"  # higher count first
    assert hits[1].entry_id == "bbb"


def test_store_search_with_type_filter():
    store = MemoryStore()
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "sc", "hello world"))
    store.put(MemoryEntry.create(MemoryType.SESSION, "sc", "hello world"))
    hits = store.search("hello", memory_type=MemoryType.SESSION)
    assert len(hits) == 1
    assert hits[0].memory_type == MemoryType.SESSION


def test_store_search_empty_query():
    store = MemoryStore()
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "sc", "hello"))
    assert store.search("") == []
    assert store.search("   ") == []


def test_store_delete():
    store = MemoryStore()
    e = MemoryEntry.create(MemoryType.CONVERSATION, "sc", "to delete")
    store.put(e)
    store.delete(e.entry_id)
    assert len(store) == 0
    with pytest.raises(MemoryError):
        store.get(e.entry_id)
    with pytest.raises(MemoryError):
        store.delete("missing")


def test_store_verify_all():
    store = MemoryStore()
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "sc", "x"))
    store.put(MemoryEntry.create(MemoryType.SESSION, "sc", "y"))
    assert store.verify_all()
    # Tamper underlying entry
    eid = store.list_all()[0].entry_id
    store._entries[eid].content = "tampered"  # type: ignore[attr-defined]
    assert not store.verify_all()


def test_store_contains_and_len():
    store = MemoryStore()
    e = MemoryEntry.create(MemoryType.KNOWLEDGE, "sc", "k")
    store.put(e)
    assert e.entry_id in store
    assert "missing" not in store
    assert len(store) == 1


def test_store_thread_safety():
    store = MemoryStore()
    n = 20
    barrier = threading.Barrier(n)

    def put_one(i: int):
        barrier.wait()
        store.put(MemoryEntry.create(MemoryType.CONVERSATION, f"scope-{i % 4}", f"content {i} hello"))

    threads = [threading.Thread(target=put_one, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(store) == n
    assert store.verify_all()


def test_store_get_missing_raises():
    store = MemoryStore()
    with pytest.raises(MemoryError):
        store.get("nope")


def test_store_list_all_unscoped_returns_all():
    store = MemoryStore()
    store.put(MemoryEntry.create(MemoryType.CONVERSATION, "scope-A", "a"))
    store.put(MemoryEntry.create(MemoryType.SESSION, "scope-B", "b"))
    assert len(store.list_all()) == 2
