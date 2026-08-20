"""Automated tests for the knowledge index (TASK-007)."""

import hashlib
import threading

import pytest

from aios.runtime.knowledge import (
    KnowledgeDocument,
    KnowledgeError,
    KnowledgeHit,
    KnowledgeIndex,
    KnowledgeSource,
    KnowledgeSourceType,
)


# -- Source types --

def test_source_type_all_four():
    assert set(KnowledgeSourceType.all()) == {
        KnowledgeSourceType.LOCAL_DOC,
        KnowledgeSourceType.LOCAL_PDF,
        KnowledgeSourceType.LOCAL_CODE,
        KnowledgeSourceType.INLINE,
    }


def test_source_create():
    src = KnowledgeSource.create(KnowledgeSourceType.LOCAL_DOC, uri="docs/a.md")
    assert src.source_type == KnowledgeSourceType.LOCAL_DOC
    assert src.uri == "docs/a.md"


def test_source_create_str_coercion():
    src = KnowledgeSource.create("inline")
    assert src.source_type == KnowledgeSourceType.INLINE


def test_source_unknown_type_rejected():
    with pytest.raises(KnowledgeError):
        KnowledgeSource.create("unknown")


# -- Document --

def test_document_create_computes_hash():
    doc = KnowledgeDocument.create("hello world", source_id="s1", source_type=KnowledgeSourceType.INLINE)
    assert doc.content_hash == hashlib.sha256(b"hello world").hexdigest()
    assert doc.verify()


def test_document_create_from_bytes():
    doc = KnowledgeDocument.create(b"bytes", source_id="s1", source_type=KnowledgeSourceType.LOCAL_CODE)
    assert doc.content == "bytes"
    assert doc.verify()


def test_document_provenance():
    doc = KnowledgeDocument.create(
        "data", source_id="s1", source_type=KnowledgeSourceType.LOCAL_DOC,
        producer="agent-1", task_id="TASK-007", run_id="run-1", metadata={"k": "v"},
    )
    assert doc.producer == "agent-1"
    assert doc.task_id == "TASK-007"
    assert doc.metadata["k"] == "v"


def test_document_verify_tampered():
    doc = KnowledgeDocument.create("original", source_id="s1", source_type=KnowledgeSourceType.INLINE)
    doc.content = "tampered"
    assert not doc.verify()


def test_document_missing_source_id_rejected():
    with pytest.raises(KnowledgeError):
        KnowledgeDocument.create("data", source_id="", source_type=KnowledgeSourceType.INLINE)


def test_document_non_str_bytes_rejected():
    with pytest.raises(KnowledgeError):
        KnowledgeDocument.create(12345, source_id="s1", source_type=KnowledgeSourceType.INLINE)


# -- KnowledgeIndex: sources + ingest --

def test_index_add_source_and_list():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.LOCAL_DOC))
    assert idx.source_count == 1
    assert idx.get_source(src.source_id).source_id == src.source_id


def test_index_rejects_duplicate_source():
    idx = KnowledgeIndex()
    src = KnowledgeSource.create(KnowledgeSourceType.INLINE, source_id="dup")
    idx.add_source(src)
    with pytest.raises(KnowledgeError):
        idx.add_source(src)


def test_index_rejects_non_source():
    idx = KnowledgeIndex()
    with pytest.raises(KnowledgeError):
        idx.add_source("not-a-source")  # type: ignore[arg-type]


def test_index_get_source_missing():
    idx = KnowledgeIndex()
    with pytest.raises(KnowledgeError):
        idx.get_source("nope")


def test_index_ingest_and_get():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.LOCAL_DOC))
    doc = idx.ingest("hello world knowledge", source_id=src.source_id, metadata={"page": 1})
    assert idx.get(doc.doc_id).content == "hello world knowledge"
    assert idx.get(doc.doc_id).metadata["page"] == 1
    assert idx.get(doc.doc_id).source_id == src.source_id


def test_index_ingest_requires_registered_source():
    idx = KnowledgeIndex()
    with pytest.raises(KnowledgeError):
        idx.ingest("data", source_id="unknown")


def test_index_rejects_duplicate_doc_id():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
    idx.ingest("hello", source_id=src.source_id, doc_id="dup")
    with pytest.raises(KnowledgeError):
        idx.ingest("hello again", source_id=src.source_id, doc_id="dup")


def test_index_list_by_source():
    idx = KnowledgeIndex()
    src1 = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.LOCAL_DOC))
    src2 = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
    idx.ingest("doc A", source_id=src1.source_id)
    idx.ingest("doc B", source_id=src2.source_id)
    idx.ingest("doc C", source_id=src1.source_id)
    assert len(idx.list_by_source(src1.source_id)) == 2
    assert len(idx.list_by_source(src2.source_id)) == 1


def test_index_provenance_preserved_through_ingest():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.LOCAL_PDF))
    doc = idx.ingest("pdf text", source_id=src.source_id, producer="p1", task_id="t1", run_id="r1")
    fetched = idx.get(doc.doc_id)
    assert fetched.producer == "p1"
    assert fetched.task_id == "t1"
    assert fetched.run_id == "r1"
    assert fetched.content_hash == hashlib.sha256(b"pdf text").hexdigest()


def test_index_all_four_source_types_ingestable():
    idx = KnowledgeIndex()
    for st in KnowledgeSourceType.all():
        src = idx.add_source(KnowledgeSource.create(st))
        doc = idx.ingest(f"content for {st.value}", source_id=src.source_id)
        assert doc.source_type == st


def test_index_get_missing_raises():
    idx = KnowledgeIndex()
    with pytest.raises(KnowledgeError):
        idx.get("missing")


# -- Search: deterministic ranking --

def test_search_basic():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
    idx.ingest("hello world", source_id=src.source_id)
    idx.ingest("goodbye world", source_id=src.source_id)
    hits = idx.search("hello")
    assert len(hits) == 1
    assert hits[0].content == "hello world"


def test_search_deterministic_same_order():
    def build():
        idx = KnowledgeIndex()
        src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
        idx.ingest("hello hello hello", source_id=src.source_id, doc_id="a")
        idx.ingest("hello", source_id=src.source_id, doc_id="b")
        idx.ingest("hello hello", source_id=src.source_id, doc_id="c")
        return [h.doc_id for h in idx.search("hello")]

    assert build() == build()


def test_search_ranking_tf_then_source_priority_then_doc_id():
    idx = KnowledgeIndex()
    # Same TF but different source types — LOCAL_DOC should win over INLINE
    src_doc = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.LOCAL_DOC, source_id="s-doc"))
    src_inline = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE, source_id="s-inline"))
    idx.ingest("hello world", source_id=src_inline.source_id, doc_id="doc-inline")
    idx.ingest("hello world", source_id=src_doc.source_id, doc_id="doc-local")
    hits = idx.search("hello")
    assert hits[0].doc_id == "doc-local"
    assert hits[1].doc_id == "doc-inline"
    # Tie on TF + priority -> doc_id asc
    idx2 = KnowledgeIndex()
    src = idx2.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
    idx2.ingest("hello", source_id=src.source_id, doc_id="bbb")
    idx2.ingest("hello", source_id=src.source_id, doc_id="aaa")
    hits2 = idx2.search("hello")
    assert [h.doc_id for h in hits2] == ["aaa", "bbb"]


def test_search_source_type_filter():
    idx = KnowledgeIndex()
    src_doc = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.LOCAL_DOC))
    src_code = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.LOCAL_CODE))
    idx.ingest("hello from doc", source_id=src_doc.source_id)
    idx.ingest("hello from code", source_id=src_code.source_id)
    hits = idx.search("hello", source_type=KnowledgeSourceType.LOCAL_CODE)
    assert len(hits) == 1
    assert hits[0].source_type == KnowledgeSourceType.LOCAL_CODE


def test_search_limit():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
    for i in range(5):
        idx.ingest("hello", source_id=src.source_id)
    hits = idx.search("hello", limit=2)
    assert len(hits) == 2


def test_search_empty_and_no_match():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
    idx.ingest("hello", source_id=src.source_id)
    assert idx.search("") == []
    assert idx.search("   ") == []
    assert idx.search("nomatch") == []


def test_search_carries_evidence():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.LOCAL_DOC))
    doc = idx.ingest("evidence content", source_id=src.source_id, metadata={"page": 42}, producer="p")
    hits = idx.search("evidence")
    assert len(hits) == 1
    h = hits[0]
    assert h.source_id == src.source_id
    assert h.content_hash == doc.content_hash == hashlib.sha256(b"evidence content").hexdigest()
    assert h.metadata["page"] == 42
    # Fields sufficient to build Evidence
    assert isinstance(h, KnowledgeHit)
    assert h.producer == "p"


def test_search_no_embeddings_no_llm_pure_tf():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
    idx.ingest("hello hello hello", source_id=src.source_id, doc_id="a")
    idx.ingest("hello", source_id=src.source_id, doc_id="b")
    hits = idx.search("hello")
    # Pure TF: a (3) > b (1)
    assert hits[0].doc_id == "a"
    assert hits[0].score == 3
    assert hits[1].score == 1


def test_search_case_insensitive():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
    idx.ingest("Hello WORLD", source_id=src.source_id)
    assert len(idx.search("hello")) == 1
    assert len(idx.search("WORLD")) == 1


# -- Integrity & containment --

def test_verify_all():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
    idx.ingest("x", source_id=src.source_id)
    idx.ingest("y", source_id=src.source_id)
    assert idx.verify_all()
    did = next(iter(idx._docs))  # type: ignore[attr-defined]
    idx._docs[did].content = "tampered"  # type: ignore[attr-defined]
    assert not idx.verify_all()


def test_contains_and_len():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
    doc = idx.ingest("data", source_id=src.source_id)
    assert doc.doc_id in idx
    assert "missing" not in idx
    assert len(idx) == 1


def test_thread_safety():
    idx = KnowledgeIndex()
    src = idx.add_source(KnowledgeSource.create(KnowledgeSourceType.INLINE))
    n = 20
    barrier = threading.Barrier(n)

    def ingest_one(i: int):
        barrier.wait()
        idx.ingest(f"content {i} hello keyword", source_id=src.source_id)

    threads = [threading.Thread(target=ingest_one, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(idx) == n
    assert idx.verify_all()
    # Search should still be consistent under concurrent reads — basic smoke.
    hits = idx.search("hello")
    assert len(hits) == n
