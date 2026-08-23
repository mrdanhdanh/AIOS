"""M18 context pipeline test matrix (T117-T124).

Covers the acceptance criteria / test matrices from ``docs/detailtask/T117.md``
.. ``T124.md``. Every scenario asserts the deterministic, fail-closed,
provenance-bearing invariants required by the master spec.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from aios.context import (
    BuildError,
    BuiltChunk,
    BuiltContext,
    ConformanceResult,
    ConformanceVerdict,
    ContextBuilder,
    ContextConformance,
    ContextError,
    ContextHarness,
    ContextRetriever,
    DependencyGraph,
    DependencyGraphError,
    Embedding,
    HybridIndex,
    HybridIndexError,
    RetrievalError,
    RetrievalHit,
    RetrievalResult,
    RepositoryScanner,
    ScanError,
    SecretBoundary,
    SymbolIndex,
    SymbolIndexError,
    VerificationResult,
    VerificationVerdict,
    ContextVerification,
)
from aios.governance.evidence.store import EvidenceStore


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _make_repo(files: dict[str, str]) -> str:
    """Create a temp repo with the given {rel_path: content} files."""
    root = tempfile.mkdtemp(prefix="m18-repo-")
    for rel, content in files.items():
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return root


def _build_pipeline_inputs(repo_root: str, query: str, chunks):
    """Run scanner+symbol+dep+hybrid+retriever and return (retrieval, store)."""
    store = EvidenceStore()
    scanner = RepositoryScanner(evidence_store=store, run_id="r1", task_id="TASK-117")
    scan = scanner.scan(repo_root)
    sources = []
    for f in scan.files:
        full = os.path.join(repo_root, f.path)
        try:
            text = Path(full).read_text(encoding="utf-8")
        except Exception:
            continue
        lang = "python" if f.file_type == "py" else "generic"
        sources.append((text, f.path, lang))
    sym = SymbolIndex(evidence_store=store, run_id="r1", task_id="TASK-118")
    sym_res = sym.index(sources)
    dep = DependencyGraph(evidence_store=store, run_id="r1", task_id="TASK-119")
    dep_res = dep.build(sources)
    hyb = HybridIndex(evidence_store=store, run_id="r1", task_id="TASK-120")
    hyb.build(sym_res, dep_res, chunks)
    retr = ContextRetriever(evidence_store=store, run_id="r1", task_id="TASK-121")
    retrieval = retr.retrieve(hyb, query)
    return retrieval, store


# =========================================================================== #
# T117 — Repository Scanner
# =========================================================================== #
def test_t117_scan_repo_metadata():
    repo = _make_repo({"a.py": "x=1\n", "sub/b.txt": "hello"})
    scanner = RepositoryScanner(run_id="r1", task_id="TASK-117")
    res = scanner.scan(repo)
    paths = {f.path for f in res.files}
    assert paths == {"a.py", "sub/b.txt"}
    by_path = {f.path: f for f in res.files}
    assert by_path["a.py"].file_type == "py"
    assert by_path["a.py"].size > 0
    assert by_path["a.py"].content_hash  # T078 hash present


def test_t117_unhashable_reject_fail_closed():
    repo = _make_repo({"a.py": "x=1"})

    def reader(path):
        if path.endswith("a.py"):
            raise OSError("permission denied")
        return b""

    scanner = RepositoryScanner(file_reader=reader, run_id="r1", task_id="TASK-117")
    with pytest.raises(ScanError):
        scanner.scan(repo)


def test_t117_change_detection():
    repo = _make_repo({"a.py": "x=1", "b.py": "y=2"})
    scanner = RepositoryScanner(run_id="r1", task_id="TASK-117")
    first = scanner.scan(repo)
    Path(repo, "a.py").write_text("x=111", encoding="utf-8")
    Path(repo, "b.py").unlink()
    Path(repo, "c.py").write_text("z=3", encoding="utf-8")
    second = scanner.scan(repo)
    diff = scanner.diff(first, second)
    assert "a.py" in diff.modified
    assert "c.py" in diff.new
    assert "b.py" in diff.deleted


def test_t117_secret_not_leaked():
    repo = _make_repo({"a.py": "x=1", ".env": "SECRET=abc"})
    scanner = RepositoryScanner(run_id="r1", task_id="TASK-117")
    res = scanner.scan(repo)
    assert all(not SecretBoundary.is_secret_path(f.path) for f in res.files)
    assert ".env" not in {f.path for f in res.files}


def test_t117_deterministic():
    repo = _make_repo({"a.py": "x=1", "b.py": "y=2"})
    scanner = RepositoryScanner(run_id="r1", task_id="TASK-117")
    r1 = scanner.scan(repo)
    r2 = scanner.scan(repo)
    assert r1.scan_id == r2.scan_id
    assert r1.content_hash == r2.content_hash


def test_t117_evidence_provenance():
    repo = _make_repo({"a.py": "x=1"})
    store = EvidenceStore()
    scanner = RepositoryScanner(evidence_store=store, run_id="r1", task_id="TASK-117")
    res = scanner.scan(repo)
    assert res.evidence_ref
    ev = store.get(res.evidence_ref)
    assert ev.content_hash == res.content_hash
    assert ev.task_id == "TASK-117"


# =========================================================================== #
# T118 — Source / Symbol Index
# =========================================================================== #
def test_t118_parse_symbols():
    idx = SymbolIndex(run_id="r1", task_id="TASK-118")
    syms = idx.index_source("def foo():\n    pass\nclass Bar:\n    x=1\n", "m.py")
    names = {s.name: s.kind for s in syms}
    assert names.get("foo") == "function"
    assert names.get("Bar") == "class"
    assert names.get("x") == "variable"
    for s in syms:
        assert s.file == "m.py" and s.line > 0


def test_t118_symbol_hash_and_evidence():
    store = EvidenceStore()
    idx = SymbolIndex(evidence_store=store, run_id="r1", task_id="TASK-118")
    res = idx.index([("def foo():\n    pass\n", "m.py", "python")])
    assert res.symbols
    for s in res.symbols:
        assert s.content_hash
    assert res.evidence_ref
    assert store.get(res.evidence_ref).content_hash == res.content_hash


def test_t118_parse_fail_reject():
    idx = SymbolIndex(run_id="r1", task_id="TASK-118")
    with pytest.raises(SymbolIndexError):
        idx.index_source("def foo(:\n", "bad.py")  # invalid python


def test_t118_lookup():
    idx = SymbolIndex(run_id="r1", task_id="TASK-118")
    idx.index([("def foo():\n    pass\nclass Bar:\n    pass\n", "m.py", "python")])
    assert any(s.name == "foo" for s in idx.lookup(name="foo"))
    assert any(s.name == "Bar" for s in idx.lookup(kind="class"))


def test_t118_deterministic():
    idx1 = SymbolIndex(run_id="r1", task_id="TASK-118")
    idx2 = SymbolIndex(run_id="r1", task_id="TASK-118")
    s1 = idx1.index_source("def foo():\n    pass\nclass Bar:\n    pass\n", "m.py")
    s2 = idx2.index_source("def foo():\n    pass\nclass Bar:\n    pass\n", "m.py")
    assert [(s.name, s.kind, s.line) for s in s1] == [(s.name, s.kind, s.line) for s in s2]


def test_t118_secret_not_indexed():
    idx = SymbolIndex(run_id="r1", task_id="TASK-118")
    with pytest.raises(SymbolIndexError):
        idx.index_source("x=1", "config/.env")


# =========================================================================== #
# T119 — Dependency Graph
# =========================================================================== #
def test_t119_extract_edges():
    dep = DependencyGraph(run_id="r1", task_id="TASK-119")
    res = dep.build([("import os\nfrom a import b\ndef f():\n    g()\n", "m.py", "python")])
    edge_kinds = {e.kind for e in res.edges}
    assert "import" in edge_kinds
    assert "call" in edge_kinds
    node_ids = {n.id for n in res.nodes}
    assert "m.py" in node_ids and "os" in node_ids


def test_t119_cycle_detected_blocks():
    dep = DependencyGraph(run_id="r1", task_id="TASK-119")
    # module a imports b; module b imports a -> cycle (same node ids)
    res = dep.build(
        [
            ("import b\n", "a", "python"),
            ("import a\n", "b", "python"),
        ]
    )
    assert res.has_cycle is True  # BLOCK (T001 Rule 2)


def test_t119_node_hash_and_evidence():
    store = EvidenceStore()
    dep = DependencyGraph(evidence_store=store, run_id="r1", task_id="TASK-119")
    res = dep.build([("import os\n", "m.py", "python")])
    for n in res.nodes:
        assert n.content_hash
    assert res.evidence_ref
    assert store.get(res.evidence_ref).content_hash == res.content_hash


def test_t119_secret_not_graph():
    dep = DependencyGraph(run_id="r1", task_id="TASK-119")
    with pytest.raises(DependencyGraphError):
        dep.build([("x=1", "config/.env", "python")])


def test_t119_deterministic():
    dep1 = DependencyGraph(run_id="r1", task_id="TASK-119")
    dep2 = DependencyGraph(run_id="r1", task_id="TASK-119")
    r1 = dep1.build([("import os\n", "m.py", "python")])
    r2 = dep2.build([("import os\n", "m.py", "python")])
    assert r1.has_cycle == r2.has_cycle
    assert {(e.frm, e.to, e.kind) for e in r1.edges} == {(e.frm, e.to, e.kind) for e in r2.edges}


def test_t119_evidence_provenance():
    store = EvidenceStore()
    dep = DependencyGraph(evidence_store=store, run_id="r1", task_id="TASK-119")
    res = dep.build([("import os\n", "m.py", "python")])
    assert res.evidence_ref
    assert store.get(res.evidence_ref).task_id == "TASK-119"


# =========================================================================== #
# T120 — Semantic + Hybrid Index
# =========================================================================== #
def _sym_dep_for(chunks):
    store = EvidenceStore()
    sym = SymbolIndex(evidence_store=store, run_id="r1", task_id="TASK-118")
    sym_res = sym.index([("def foo():\n    pass\n", "m.py", "python")])
    dep = DependencyGraph(evidence_store=store, run_id="r1", task_id="TASK-119")
    dep_res = dep.build([("def foo():\n    pass\n", "m.py", "python")])
    hyb = HybridIndex(evidence_store=store, run_id="r1", task_id="TASK-120")
    hyb_res = hyb.build(sym_res, dep_res, chunks)
    return hyb, hyb_res, store


def test_t120_build_hybrid():
    hyb, res, _ = _sym_dep_for([("def foo", "m.py")])
    assert res.embeddings
    assert res.symbol_ref and res.dependency_ref


def test_t120_hybrid_query_ranked():
    hyb, _, _ = _sym_dep_for([("def foo", "m.py"), ("unrelated text", "n.py")])
    q = hyb.query("def foo")
    assert q.hits
    assert q.hits[0].chunk == "def foo"
    assert q.hits[0].combined >= q.hits[-1].combined


def test_t120_embedding_fail_reject():
    store = EvidenceStore()
    sym = SymbolIndex(evidence_store=store, run_id="r1", task_id="TASK-118")
    sym_res = sym.index([("def foo():\n    pass\n", "m.py", "python")])
    dep = DependencyGraph(evidence_store=store, run_id="r1", task_id="TASK-119")
    dep_res = dep.build([("def foo():\n    pass\n", "m.py", "python")])
    hyb = HybridIndex(
        evidence_store=store, run_id="r1", task_id="TASK-120",
        embed_fn=lambda t: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    with pytest.raises(HybridIndexError):
        hyb.build(sym_res, dep_res, [("x", "m.py")])


def test_t120_secret_not_embedded():
    store = EvidenceStore()
    sym = SymbolIndex(evidence_store=store, run_id="r1", task_id="TASK-118")
    sym_res = sym.index([("def foo():\n    pass\n", "m.py", "python")])
    dep = DependencyGraph(evidence_store=store, run_id="r1", task_id="TASK-119")
    dep_res = dep.build([("def foo():\n    pass\n", "m.py", "python")])
    hyb = HybridIndex(evidence_store=store, run_id="r1", task_id="TASK-120")
    with pytest.raises(HybridIndexError):
        hyb.build(sym_res, dep_res, [("secret", "config/.env")])


def test_t120_deterministic():
    hyb1, _, _ = _sym_dep_for([("def foo", "m.py")])
    hyb2, _, _ = _sym_dep_for([("def foo", "m.py")])
    q1 = hyb1.query("def foo")
    q2 = hyb2.query("def foo")
    assert [(h.chunk, h.combined) for h in q1.hits] == [(h.chunk, h.combined) for h in q2.hits]


def test_t120_evidence_provenance():
    hyb, res, store = _sym_dep_for([("def foo", "m.py")])
    assert res.evidence_ref
    assert store.get(res.evidence_ref).task_id == "TASK-120"


# =========================================================================== #
# T121 — Context Retriever
# =========================================================================== #
def test_t121_query_hybrid():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    retrieval, _ = _build_pipeline_inputs(repo, "def foo", [("def foo", "m.py")])
    assert retrieval.hits


def test_t121_hit_hash_and_evidence():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    retrieval, store = _build_pipeline_inputs(repo, "def foo", [("def foo", "m.py")])
    for h in retrieval.hits:
        assert h.content_hash
    assert retrieval.evidence_ref
    assert store.get(retrieval.evidence_ref).task_id == "TASK-121"


def test_t121_secret_not_returned():
    store = EvidenceStore()
    sym = SymbolIndex(evidence_store=store, run_id="r1", task_id="TASK-118")
    sym_res = sym.index([("def foo():\n    pass\n", "m.py", "python")])
    dep = DependencyGraph(evidence_store=store, run_id="r1", task_id="TASK-119")
    dep_res = dep.build([("def foo():\n    pass\n", "m.py", "python")])
    hyb = HybridIndex(evidence_store=store, run_id="r1", task_id="TASK-120")
    # Build with a public chunk; the hybrid index itself rejects secret sources
    # (T120), so we inject a secret-source chunk to exercise the retriever
    # boundary (T121 defense-in-depth: never return a secret chunk).
    hyb.build(sym_res, dep_res, [("public", "m.py")])
    hyb._chunks.append(
        Embedding(chunk="secret", source="config/.env", vector=[0.0] * 64, content_hash="sec")
    )
    retr = ContextRetriever(evidence_store=store, run_id="r1", task_id="TASK-121")
    res = retr.retrieve(hyb, "secret")
    assert all(not SecretBoundary.is_secret_path(h.source) for h in res.hits)


def test_t121_index_not_ready_reject():
    retr = ContextRetriever(run_id="r1", task_id="TASK-121")
    with pytest.raises(RetrievalError):
        retr.retrieve(HybridIndex(run_id="r1", task_id="TASK-120"), "q")


def test_t121_deterministic():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    r1, _ = _build_pipeline_inputs(repo, "def foo", [("def foo", "m.py")])
    r2, _ = _build_pipeline_inputs(repo, "def foo", [("def foo", "m.py")])
    assert [(h.chunk, h.score) for h in r1.hits] == [(h.chunk, h.score) for h in r2.hits]


def test_t121_evidence_provenance():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    retrieval, store = _build_pipeline_inputs(repo, "def foo", [("def foo", "m.py")])
    assert retrieval.evidence_ref
    assert store.get(retrieval.evidence_ref).content_hash == retrieval.content_hash


# =========================================================================== #
# T122 — Context Builder + Budget
# =========================================================================== #
def _retrieval_with(hits):
    return RetrievalResult(
        query="q",
        hits=hits,
        retriever_id="ret-1",
        policy_ref="pol",
        evidence_ref="ev-1",
        content_hash="h",
    )


def test_t122_build_context():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    retrieval, _ = _build_pipeline_inputs(repo, "def foo", [("def foo", "m.py")])
    built = ContextBuilder(run_id="r1", task_id="TASK-122").build(retrieval)
    assert built.assembled_chunks
    assert built.within_budget


def test_t122_over_budget_trim():
    hits = [
        RetrievalHit("low priority chunk", "m.py", 0.1, "c1"),
        RetrievalHit("another low chunk", "m.py", 0.1, "c2"),
    ]
    built = ContextBuilder(run_id="r1", task_id="TASK-122").build(
        _retrieval_with(hits), budget_limit=2
    )
    # Over budget -> low-priority chunks trimmed (fail-closed trim, not error).
    assert built.within_budget
    assert built.budget_used <= 2


def test_t122_priority_trim_keeps_high():
    hits = [
        RetrievalHit("critical chunk", "m.py", 0.95, "c1"),
        RetrievalHit("low chunk", "m.py", 0.05, "c2"),
    ]
    built = ContextBuilder(run_id="r1", task_id="TASK-122").build(
        _retrieval_with(hits), budget_limit=3
    )
    kept = {c.chunk for c in built.assembled_chunks}
    assert "critical chunk" in kept
    assert "low chunk" not in kept


def test_t122_chunk_hash_and_evidence():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    retrieval, store = _build_pipeline_inputs(repo, "def foo", [("def foo", "m.py")])
    built = ContextBuilder(evidence_store=store, run_id="r1", task_id="TASK-122").build(retrieval)
    for c in built.assembled_chunks:
        assert c.content_hash
    assert built.evidence_ref
    assert store.get(built.evidence_ref).content_hash == built.content_hash


def test_t122_deterministic():
    hits = [RetrievalHit("critical chunk", "m.py", 0.95, "c1"),
            RetrievalHit("low chunk", "m.py", 0.05, "c2")]
    b1 = ContextBuilder(run_id="r1", task_id="TASK-122").build(_retrieval_with(hits), budget_limit=10)
    b2 = ContextBuilder(run_id="r1", task_id="TASK-122").build(_retrieval_with(hits), budget_limit=10)
    assert [(c.chunk, c.priority) for c in b1.assembled_chunks] == [
        (c.chunk, c.priority) for c in b2.assembled_chunks
    ]


def test_t122_secret_not_built():
    hits = [RetrievalHit("secret", "config/.env", 0.9, "c1")]
    with pytest.raises(BuildError):
        ContextBuilder(run_id="r1", task_id="TASK-122").build(_retrieval_with(hits))


# =========================================================================== #
# T123 — Context Verification + Evidence
# =========================================================================== #
def test_t123_verify_correct_pass():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    retrieval, store = _build_pipeline_inputs(repo, "def foo", [("def foo", "m.py")])
    built = ContextBuilder(evidence_store=store, run_id="r1", task_id="TASK-122").build(retrieval)
    ver = ContextVerification(evidence_store=store, run_id="r1", task_id="TASK-123").verify(built)
    assert ver.verification_result == VerificationVerdict.PASS
    assert ver.integrity_verified is True


def test_t123_verify_wrong_fail():
    # A built context whose chunk is missing a content_hash -> FAIL.
    bad = BuiltContext(
        retrieval_ref="r",
        assembled_chunks=[BuiltChunk("x", "m.py", 1, 1, "")],
        budget_used=1,
        budget_limit=10,
        within_budget=True,
        evidence_ref="ev",
        content_hash="h",
    )
    ver = ContextVerification(run_id="r1", task_id="TASK-123").verify(bad)
    assert ver.verification_result == VerificationVerdict.FAIL


def test_t123_inconclusive_not_promoted():
    # Well-formed context but integrity not verified -> INCONCLUSIVE (not PASS).
    ctx = BuiltContext(
        retrieval_ref="r",
        assembled_chunks=[BuiltChunk("x", "m.py", 1, 1, "hashx")],
        budget_used=1,
        budget_limit=10,
        within_budget=True,
        evidence_ref="ev-missing",  # not in store -> integrity fails
        content_hash="hashx",
    )
    ver = ContextVerification(run_id="r1", task_id="TASK-123").verify(ctx)
    assert ver.verification_result == VerificationVerdict.INCONCLUSIVE
    assert ver.integrity_verified is False


def test_t123_evidence_provenance():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    retrieval, store = _build_pipeline_inputs(repo, "def foo", [("def foo", "m.py")])
    built = ContextBuilder(evidence_store=store, run_id="r1", task_id="TASK-122").build(retrieval)
    ver = ContextVerification(evidence_store=store, run_id="r1", task_id="TASK-123").verify(built)
    assert ver.evidence_ref
    assert store.get(ver.evidence_ref).task_id == "TASK-123"


def test_t123_deterministic():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    retrieval, store = _build_pipeline_inputs(repo, "def foo", [("def foo", "m.py")])
    built = ContextBuilder(evidence_store=store, run_id="r1", task_id="TASK-122").build(retrieval)
    v1 = ContextVerification(evidence_store=store, run_id="r1", task_id="TASK-123").verify(built)
    v2 = ContextVerification(evidence_store=store, run_id="r1", task_id="TASK-123").verify(built)
    assert v1.verification_result == v2.verification_result


def test_t123_secret_not_verified():
    ctx = BuiltContext(
        retrieval_ref="r",
        assembled_chunks=[BuiltChunk("x", "config/.env", 1, 1, "h")],
        budget_used=1,
        budget_limit=10,
        within_budget=True,
        evidence_ref="ev",
        content_hash="h",
    )
    ver = ContextVerification(run_id="r1", task_id="TASK-123").verify(ctx)
    assert ver.verification_result == VerificationVerdict.FAIL


# =========================================================================== #
# T124 — Context Harness + Conformance
# =========================================================================== #
def test_t124_harness_pipeline_runs():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    harness = ContextHarness(run_id="r1")
    out = harness.run_pipeline(repo, "def foo", [("def foo", "m.py")])
    assert set(out.keys()) == {
        "scan", "symbol_index", "dependency", "hybrid", "retrieval", "built", "verification"
    }


def test_t124_conformance_pass():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    harness = ContextHarness(run_id="r1")
    out = harness.run_pipeline(repo, "def foo", [("def foo", "m.py")])
    conf = ContextConformance(run_id="r1").evaluate(out)
    assert isinstance(conf, ConformanceResult)
    assert conf.conformance_result == ConformanceVerdict.PASS
    assert conf.integrity_verified is True


def test_t124_stage_fail_conformance_fail():
    # Empty repo -> scan stage FAIL -> conformance FAIL (fail-closed).
    repo = _make_repo({})
    harness = ContextHarness(run_id="r1")
    out = harness.run_pipeline(repo, "def foo", [("def foo", "m.py")])
    conf = ContextConformance(run_id="r1").evaluate(out)
    assert conf.conformance_result == ConformanceVerdict.FAIL


def test_t124_stage_inconclusive_conformance_fail():
    # Craft a harness result where verification is INCONCLUSIVE but all other
    # stages PASS -> conformance must FAIL (T078).
    store = EvidenceStore()
    harness = ContextHarness(evidence_store=store, run_id="r1")
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    out = harness.run_pipeline(repo, "def foo", [("def foo", "m.py")])
    out["verification"] = VerificationResult(
        built_context_ref="x",
        verification_result=VerificationVerdict.INCONCLUSIVE,
        integrity_verified=False,
        evidence_ref="ev",
        content_hash="h",
    )
    conf = ContextConformance(evidence_store=store, run_id="r1").evaluate(out)
    assert conf.conformance_result == ConformanceVerdict.FAIL


def test_t124_integrity_not_verified_conformance_fail():
    store = EvidenceStore()
    harness = ContextHarness(evidence_store=store, run_id="r1")
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    out = harness.run_pipeline(repo, "def foo", [("def foo", "m.py")])
    out["verification"].integrity_verified = False
    conf = ContextConformance(evidence_store=store, run_id="r1").evaluate(out)
    assert conf.conformance_result == ConformanceVerdict.FAIL


def test_t124_deterministic():
    repo = _make_repo({"m.py": "def foo():\n    pass\n"})
    harness = ContextHarness(run_id="r1")
    out1 = harness.run_pipeline(repo, "def foo", [("def foo", "m.py")])
    out2 = harness.run_pipeline(repo, "def foo", [("def foo", "m.py")])
    c1 = ContextConformance(run_id="r1").evaluate(out1)
    c2 = ContextConformance(run_id="r1").evaluate(out2)
    assert c1.conformance_result == c2.conformance_result
    assert c1.content_hash == c2.content_hash
